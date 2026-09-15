# ISO and QEMU validation — 2026-09-14

## Artifact

- ISO: `build/output/run-KHfNFL37/abs-linux-amd64.hybrid.iso`
- Size: 771442688 bytes (about 736 MiB).
- SHA-256: `5516bf9f7ca361af7bdc2084b0367f59e7e8dfac6a34c34c3faf14a3f616f88b`
- Debian 13.7 (trixie), kernel `6.12.107+deb13-amd64`.
- Calamares `3.3.14-1`; live-build `1:20250505+deb13u1`.
- QEMU `10.0.13`, KVM, OVMF UEFI without Secure Boot, 4 GiB RAM,
  two virtual CPUs, VirtIO graphics and a fresh 32 GiB qcow2 disk per test.

The full corrected image was built with live-build. After the Rofi parser fix,
the two staged and chroot Rofi configuration copies were updated from source,
and `lb clean --binary` / `lb binary` regenerated the final ISO. The final ISO
was then installed again to a fresh virtual disk. Builds use moving Debian
mirrors; this checksum identifies this artifact, not a reproducibility promise.

## Results

| Image and VM directory under build/output | Installation | Independent disk boot |
| --- | --- | --- |
| Corrected package image: `vm-20260914-ext4` | Automatic GPT: 512 MiB ESP, ext4 root, small swap; networking enabled | Passed; LightDM login and i3 desktop |
| Same image: `vm-20260914-manual` | Manual GPT: 512 MiB ESP, ext4 root, no swap; `-nic none` throughout | Passed offline; LightDM login and i3 desktop |
| Final ISO: `vm-20260914-final` | Rofi launched Calamares; automatic GPT/ext4 and small swap | Passed; ISO removed before boot |

The manual/offline run used the image immediately before the Rofi-only change.
Its installer and package contents match the final image; the exact final ISO
was retested with automatic partitioning. Manual/offline installation of that
exact final checksum has not been repeated.

Checks include mounted ESP and ext4 root, active swap on automatic layouts,
new-user configuration ownership, sudo access, no failed system or user units,
removal of the live account, installer launcher and live-only packages. Debian
identity is retained. The online installation passed `apt-get update` without
duplicate source warnings. Offline checks confirmed only the loopback interface.
The final desktop additionally passed Rofi launch and Fastfetch display checks.
Nine automated foundation tests passed, including real Rofi configuration parsing,
ShellCheck and i3 syntax validation.

## Integration fixes discovered

1. The initial ISO reached LightDM but could not create the live account because
   package recommends are disabled. Added the explicit `user-setup` dependency,
   and remove it from the installed target with other live-only packages.
2. Added `console-setup` for console/keyboard initialization.
3. Removed duplicate custom APT sources; live-build supplies the final Debian
   sources after chroot hooks have run.
4. Split Rofi configuration properties across lines. The packaged parser consumed
   the one-line modes and font settings incorrectly, preventing launcher startup.
   Added a parser regression check.

## Evidence retained locally

All screenshots are actual QEMU QMP `screendump` PNGs. They were inspected during
live boot, installer pages, partition review, installation progress, completion,
and disk-only boot/login. Generated evidence is gitignored and is not distributed
with a source checkout.

- `run-KHfNFL37/SHA256SUMS`, `build.log`, `binary-rebuild.log`.
- `vm-20260914-ext4/screenshots/19-install-complete.png`,
  `21-installed-desktop.png`, and `installed-checks.txt`.
- `vm-20260914-manual/screenshots/16-offline-summary.png`,
  `19-offline-complete.png`, `21-installed-desktop.png`, and `installed-checks.txt`.
- `vm-20260914-final/screenshots/01-rofi-fixed.png`,
  `02-launcher-started-installer.png`, `04-final-summary.png`,
  `10-complete.png`, `11-installed-boot.png`, `13-installed-rofi.png`,
  `14-installed-fastfetch.png`, and `installed-checks.txt`.
- Each VM directory retains its qcow2 disk, OVMF variables and serial logs.
  `vm-20260914-final/installed-block-devices.json` records the disk-only boot.

The test VMs were shut down after validation; their disks and evidence remain.
Only disposable qcow2 disks were partitioned. No host block device was attached
to the guests. See [the build guide](../build/README.md) for launch commands and
QMP screenshot monitoring.

## Remaining acceptance work

- Real hardware installation, suspend/resume, audio playback, touch, TrackPoint,
  brightness, Bluetooth and wireless validation.
- Existing ESP reuse, encryption, Btrfs and BIOS boot need separate tests.
- Secure Boot has not been validated.
- Visual polish: original artwork still mentions Polybar; the desktop uses
  i3blocks. Wallpaper scaling, default Debian splash, duplicate upstream live
  installer menu entry, inherited `(live)` shell-prompt prefix on installed systems,
  and a nonfatal live GRUB font warning remain follow-ups.
- Snapshot pinning, signed artifacts, CI installation and update/rollback coverage
  remain release work. This establishes a working VM installer foundation.
