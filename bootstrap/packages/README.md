# Package manifests

Each `.list` contains one Debian binary package per line, with an inline reason.
`base` and `desktop` are always selected. `laptop`, `touch`, `trackpoint`, and
`bluetooth` map to detected capabilities in `profiles/profiles.json`. The live
image includes all these groups for offline installation and hardware portability.
`development` and `optional` are reviewable choices, excluded by default.

`installer/calamares/package-lists/live.list` adds installer/live/UEFI packages and
LightDM for new images. Manual deployment preserves an existing display manager.
The inventory and deviations from Defuser are in `docs/reference-inventory.md`.
Dependencies remain APT's responsibility. Tests check names against available
APT metadata, not a copied list of everything installed on a reference machine.
