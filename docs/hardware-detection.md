# Hardware capability detection

## Principle

ABS Linux selects behavior from hardware and system capabilities, not computer names. Development systems are useful test fixtures, but their hostnames carry no reliable information about present hardware. Devices can be added, removed, docked, or replaced; a hostname cannot describe those changes.

Code like this is therefore prohibited except as a documented last-resort quirk:

```bash
if [[ "$(hostname)" == "some-machine-name" ]]; then
    # ...
fi
```

Instead, detection should expose small, stable facts such as:

```text
touchscreen=true
tablet_mode=true
battery=true
trackpoint=true
rotation_sensor=true
hardware_buttons=true
multi_monitor=true
```

## Intended sources

| Capability | Preferred evidence |
| --- | --- |
| Input device type | udev properties, libinput capabilities, and XInput under X11 |
| Battery | relevant battery devices below `/sys/class/power_supply` |
| Touchscreen | input-device touch capabilities rather than product-name allowlists |
| TrackPoint | actual pointing-stick device properties, including hot-plugged USB devices |
| Displays | connected outputs and topology reported by `xrandr` |
| Network and VPN | NetworkManager state and supported interfaces |
| Rotation sensor | an available, supported sensor interface |
| Tablet mode | a kernel/udev switch or other supported interface where exposed |
| Hardware buttons | input events and udev identity/capabilities |

Product or vendor identifiers may refine detection when capability metadata is insufficient, but should describe the device—not the host containing it.

## Detection and composition

Detection should be read-only and deterministic. It should emit a documented representation that can be inspected and tested. Profile composition then enables relevant layers:

- a battery enables battery status and power behavior;
- no battery means no meaningless battery module;
- a touchscreen enables touch-oriented controls;
- rotation controls require usable rotation support;
- any detected TrackPoint, including one on an external Lenovo USB keyboard, enables appropriate tuning;
- multiple connected displays enable multi-monitor layout behavior.

Conflicting or ambiguous signals should degrade safely and remain visible in diagnostic output. Profile order and precedence must be explicit.

## Quirk profiles

A narrowly scoped machine or device quirk is acceptable only when generic capability detection cannot express the issue. Such a rule should record:

1. the actual affected hardware identifier;
2. the observed problem;
3. why generic detection is insufficient;
4. the smallest necessary override; and
5. how the rule can be tested or eventually removed.

Even quirk matching should prefer stable device identifiers over hostnames.

## Privacy and testability

Diagnostic fixtures must be sanitized before commit. They must not contain usernames, serial numbers, network identifiers, credentials, or other machine-local secrets. Tests should model capability combinations directly so every behavior does not require access to physical hardware.

## Implemented foundation

Run `scripts/abs-capabilities` for JSON facts. It queries udev input properties,
sysfs battery/DRM/Bluetooth devices, IIO accelerometer channels and tablet-switch
capability bits. Battery peripherals with `scope=Device` and absent packs are
excluded. `tablet_mode` means a switch exists, not its current state;
`hardware_buttons` means key-capable input exists, not a known vendor mapping.
Rotation/display facts are diagnostic only in this pass. Profile composition is
in `profiles/profiles.json`; the runtime bar redetects at session/bar startup.
Tests use synthetic fixtures and do not need physical test machines.
