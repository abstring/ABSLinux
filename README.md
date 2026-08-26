<p align="center">
  <img src="ABSLinux_hero_ad.png" alt="ABS Linux — Stop skidding. Control your computer." width="900">
</p>

# ABS Linux

> **Stop skidding. Control your computer.**

ABS Linux is a curated, opinionated Linux desktop environment built on **Debian Stable + i3**. It is a reproducible configuration, integration, and bootstrap layer that turns a clean Debian installation into a polished, keyboard-first workstation without hiding or replacing Debian underneath.

ABS Linux is not a conventional distribution, a Debian fork, or a new operating-system base. Debian supplies the operating system; ABS supplies an integrated desktop experience.

## Philosophy

- Keep Debian Stable underneath and preserve its standard mechanisms.
- Make i3 productive out of the box for keyboards, mice, TrackPoints, touchscreens, and tablets.
- Prefer mature upstream software from Debian over bespoke replacements.
- Keep configuration direct, inspectable, and portable.
- Detect hardware capabilities instead of encoding machine names.
- Produce the same coherent experience across laptops, rugged tablets, and workstations.
- Make setup reproducible and, wherever practical, idempotent.

## Goals

- Turn a clean Debian installation into a consistent ABS workstation through a reviewable bootstrap process.
- Provide thoughtful defaults and integration for a modern i3 desktop.
- Compose features from detected capabilities such as batteries, touchscreens, TrackPoints, rotation sensors, hardware buttons, and multiple displays.
- Support specialized interfaces—including a future LCARS-style touch launcher—without coupling them to the generic i3 configuration.
- Remain close enough to standard Debian that an experienced Linux user can understand and maintain the system.

## Non-goals

- Forking Debian, maintaining an independent package base, or replacing Debian's operating-system foundations.
- Modifying `/etc/os-release` to present ABS Linux as an independent distribution.
- Reimplementing well-maintained upstream tools without a compelling integration need.
- Hostname-specific behavior for known development machines.
- Supporting every possible workflow or desktop environment.

## Planned architecture

```text
Debian Stable
    ↓
systemd / NetworkManager / PipeWire / standard Debian plumbing
    ↓
X11
    ↓
i3
    ↓
Polybar + Rofi + Dunst
    ↓
ABS Linux configuration, scripts, themes, profiles, and integration
```

Debian remains responsible for boot, packages, services, hardware enablement, and other operating-system foundations. i3 is the primary window manager. ABS owns the configuration and integration that make the pieces feel like one desktop. See [Architecture](docs/architecture.md).

## Hardware-adaptive design

Behavior is driven by capabilities, not hostnames. The eventual detector will expose facts similar to:

```text
touchscreen=true
tablet_mode=true
battery=true
trackpoint=true
rotation_sensor=true
hardware_buttons=true
multi_monitor=true
```

An external Lenovo USB TrackPoint keyboard should receive TrackPoint tuning even on a Dell workstation. A battery should enable battery UI; a desktop without one should not show it. Touch and rotation controls should appear only when the related hardware is present. Machine-specific profiles are reserved for genuine quirks that generic detection cannot express cleanly. See [Hardware detection](docs/hardware-detection.md).

## Planned core components

The initial desktop is planned around i3, Polybar, Rofi, Dunst, Kitty, NetworkManager, PipeWire, pavucontrol, Blueman, Fastfetch, btop, fzf, ripgrep, fd, bat, eza, and zoxide.

Clipboard history integrated with Rofi, screenshots, screen locking, display management, power management, touchscreen/tablet support, TrackPoint tuning, and multi-monitor handling are planned; exact packages and implementation details remain under evaluation where they have not yet been selected. The LCARS-style touch launcher is also planned as an optional specialized interface, isolated from the generic i3 configuration.

## Repository structure

```text
.
├── ABSLinux_hero_ad.png  # Existing project hero artwork
├── assets/               # Future project artwork and screenshots
├── bootstrap/            # Installer entry point, package manifests, shared helpers
├── config/               # Application configuration and future Fastfetch branding
├── docs/                 # Architecture, capability strategy, and roadmap
├── LICENSE               # GPL-3.0 license text
├── LICENSES/             # Additional license texts, including CC0-1.0
├── profiles/             # Capability-oriented configuration composition
├── scripts/              # Runtime and maintenance utilities
└── tests/                # Validation and automated tests
```

Subdirectories are added when they contain an implementation or documentation; the repository intentionally avoids empty placeholder trees.

## Project status

**ABS Linux is in its foundation stage.** Repository conventions and architecture are being established. Desktop configuration, capability detection, profile composition, and deployment are not yet implemented. The versioned plan is in the [roadmap](docs/roadmap.md).

### Development and test hardware

The initial test fleet covers different capability classes:

- Getac K120 G2 rugged touchscreen/tablet laptop
- Lenovo ThinkPad T440s with TrackPoint
- Dell Precision T7810 workstation, sometimes with an external Lenovo TrackPoint keyboard

These systems are test platforms only. Their machine identity must never select features; detected hardware capabilities do that.

## Installation status

> [!WARNING]
> Installation and bootstrap are **not production-ready**. `bootstrap/install.sh` is currently a non-installing placeholder and deliberately makes no system changes.

The long-term interface is intended to be:

```bash
git clone <repo>
cd ABSLinux
./bootstrap/install.sh
```

Do not expect that workflow to configure a machine yet.

## Contributing

Issues and focused pull requests are welcome while conventions settle. Please keep changes understandable, capability-driven, upstream-first, and safe to rerun. Avoid hostname checks, committed machine-local state, and broad system modifications. New executable scripts should use appropriate strict Bash practices and include `SPDX-License-Identifier: GPL-3.0-or-later`.

When adding a dependency, prefer a maintained Debian package and document why it is needed. When adding hardware behavior, include a generic detection strategy and test expectations.

## Licensing

Original ABS Linux software—including code, executable scripts, and software-oriented configuration—is licensed under **GNU GPL v3 or later** (`GPL-3.0-or-later`). See [LICENSE](LICENSE).

Original ABS Linux artwork and branding—including logos and wallpapers—is dedicated under **Creative Commons Zero v1.0 Universal** (`CC0-1.0`). See [LICENSES/CC0-1.0.txt](LICENSES/CC0-1.0.txt). This dedication does **not** apply to third-party assets; those retain their respective licenses and must be identified separately.

Debian and all other upstream components retain their own copyrights, trademarks, and licenses. ABS Linux does not own or relicense Debian or upstream software.

## Debian attribution and disclaimer

ABS Linux is an independent project based on Debian GNU/Linux. It is **not affiliated with or endorsed by the Debian Project**. Debian is a trademark of Software in the Public Interest, Inc.; use of the name here describes the upstream operating-system base.
