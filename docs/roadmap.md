# Roadmap

## v0.1 — Installer foundation (active)

- Implemented: Debian 13 manifests, portable i3/i3blocks defaults, capability facts,
  shared dry-run/deployment layer, ABS Calamares settings/branding, live-build
  staging, temporary-root tests and VM workflow.
- Next acceptance gate: build first ISO; boot under UEFI/OVMF; install to fresh
  qcow2 disks with automatic and manual GPT/ext4; reboot and validate offline
  installation, user ownership, package cleanup and Debian updates.
- Still experimental: encrypted installations; no Secure Boot acceptance yet.

## v0.2 — Adaptive hardware

- Validate native/external TrackPoint behavior and laptop lid/suspend handling.
- Exercise touch, multiple batteries, docking and display changes on hardware.
- Review BatteryBar integration and hotplug/runtime profile refresh.

## v0.3 — Desktop quality

- Visual VM review, artwork sizing and consistent app themes.
- Clipboard/menu improvements, audio/network controls and desktop accessibility.
- Configuration upgrade/merge and rollback tooling.

## v0.4 — Tablet/rugged UX

- Generalize optional LCARS integration and document vendor button quirks.
- Add tested rotation and tablet-mode behavior with capability-based activation.
- Evaluate resume/hibernate separately from normal suspend.

## v0.5 — Release reproducibility

- Snapshot-pinned builds, CI VM installation tests and artifact provenance.
- Package the ABS layer; signed releases and a supported update mechanism.
- Optional Guix developer environments only after the Debian installer is reliable.
