# Architecture

## System boundary

ABS Linux is a curated Debian-based Linux desktop distribution built around i3, designed to remain understandable, controllable, hardware-adaptive, and close to upstream Debian. It does not fork Debian or maintain an independent package base. Debian remains responsible for the operating-system foundation: boot and service management, package management, security updates, drivers, networking primitives, audio plumbing, and the standard filesystem layout.

ABS Linux owns the integration and user experience above that foundation: selected packages, application configuration, themes, capability discovery, profile composition, and a reproducible bootstrap path.

```text
Debian Stable
    ↓
systemd / NetworkManager / PipeWire / standard Debian plumbing
    ↓
X11
    ↓
i3
    ↓
i3bar/i3blocks + Rofi + Dunst
    ↓
ABS Linux configuration, scripts, themes, profiles, and integration
```

## Design rules

### Preserve Debian

Configuration layered on Debian is preferred to replacing fundamental Debian mechanisms. ABS does not modify `/etc/os-release` or claim ownership of the underlying distribution. Deviations from Debian defaults must be narrow, documented, and reversible.

### i3 is the desktop core

i3 is the primary window manager and X11 is the initial display stack. i3bar/i3blocks, Rofi, Dunst, and Kitty form the initial shell around it. See [ADR 0001](adr-0001-i3blocks.md) for the reference-driven bar decision. Specialized interfaces, such as the future LCARS-style touch launcher, are optional integrations activated through capabilities or profiles—not assumptions embedded in the generic i3 configuration.

### Capability-driven composition

Hardware behavior derives from detected facilities. Detection produces simple facts; profile composition maps those facts to configuration; application-specific adapters apply the result. This separation keeps detection testable and prevents configuration from accumulating hostname checks.

Conceptually:

```text
system inspection → capabilities → profile composition → generated/user configuration
```

Machine-specific overrides are allowed only for documented quirks that cannot be handled through a generic hardware rule.

### Upstream first

Most components should be mature upstream projects available as Debian packages. ABS should integrate them and contribute appropriate fixes upstream rather than grow private replacements. Custom code is justified for ABS-specific orchestration, capability mapping, or UX that existing tools do not provide cleanly.

### Understandable configuration

A technically competent Linux user should be able to trace what the bootstrap installs, which source owns a setting, and why a profile is active. Plain configuration and small scripts are preferred to an unnecessary framework. Generated configuration, when needed, should retain a clear path back to its source.

### Reproducible and idempotent operation

The shared deployment layer turns a clean supported Debian installation into the reviewed source configuration. Repeated runs should be safe wherever practical. Operations must validate prerequisites, report changes, avoid overwriting user data silently, and fail clearly when they cannot reach the intended state.

## Configuration ownership

- `bootstrap/` discovers prerequisites and installs or deploys the layer.
- `config/` contains application-oriented configuration.
- `profiles/` describes composable behavior for capability classes.
- `scripts/` contains narrow runtime and maintenance integrations.
- `docs/` records decisions and user-facing behavior.
- `tests/` validates parsing, composition, configuration, and installer safety.

These boundaries are initial conventions and may evolve through documented changes as implementation experience accumulates.

## Installer foundation

See [Installer architecture](installer-architecture.md) for Calamares/live-build,
shared deployment, APT ownership, configuration lifecycle and future Guix boundary.
See [Reference inventory](reference-inventory.md) for observed versus authored behavior.
