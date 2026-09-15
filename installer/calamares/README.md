# ABS Calamares configuration

`settings.conf` defines the upstream module sequence; `modules/` supplies ABS
settings. `branding/abs` contains the original root hero artwork copied unchanged
and a minimal Qt 6 slideshow. Both installer and wallpaper copies are byte-for-byte
copies of `ABSLinux_hero_ad.png`, licensed CC0-1.0. No replacement logo or cropped
asset was generated. The hero's wide aspect ratio may need a reviewed icon-sized
derivative after visual VM testing.

`scripts/abs-install` is the live-only launcher. Calamares runs `shellprocess-abs`
inside its mounted target, invoking the same bootstrap used for manual deployment.
`installer-finalize.sh` refuses execution outside a chroot, removes the live
launcher and sets target boot/DNS defaults. `package-lists/live.list` adds only
image/installer-specific packages to the shared manifests. No Calamares fork,
Debian settings package, or network-dependent bootloader helper is required.

See [architecture](../../docs/installer-architecture.md), [build and VM tests](../../build/README.md),
and [manual installation](../../bootstrap/README.md). Automatic and manual/offline
UEFI/ext4 installs have passed QEMU checks; see the dated
[validation report](../../docs/vm-validation.md) for exact coverage.
