# Alpha.2 validation — 2026-09-14

## Artifact

- Version: `0.1.0-alpha.2`, amd64 UEFI preview; Secure Boot disabled.
- File: `abs-linux-0.1.0-alpha.2-amd64.hybrid.iso`
- Size: 1556994048 bytes (about 1.45 GiB).
- SHA-256: `10c244ef7585d243569d153d47692e3c80cbe27b963aa43d3c01256e33cb47c0`
- Build directory: `build/output/run-qqO9U33A`.
- Desktop implementation: commit `89f4b62`; the release tag adds complete host
  packaging prerequisite checks, update guidance and this validation report.
- Debian 13.7, kernel `6.12.107+deb13-amd64`, Calamares `3.3.14-1`,
  Brave `1.95.101` with `brave-keyring` `1.20`.

The image uses upstream Debian packages plus Brave's signed stable repository.
Build-time failures exposed the need to bootstrap CA certificates, seed Brave's
scoped public key before APT runs, and avoid live-build's additional temporary
APT environment during binary packaging. The recipe now uses host binary tools
and checks their documented prerequisites. The tested ISO completed with those
settings. Build logs and package metadata are retained beside it.

## VM acceptance

QEMU/KVM with OVMF, VirtIO graphics, 4 GiB RAM, two CPUs and a fresh 32 GiB qcow2.
No host block device was attached. Installation ran with `-nic none` and completed
without downloads. Layout: GPT, 512 MiB FAT32 ESP, ext4 root, approximately 3.1 GiB
swap. The installed system booted independently with the ISO detached, then used
QEMU user-mode networking for update and browser checks.

Passed:

- Live autologin, supplied wallpaper and Rofi installer launch.
- Offline installation and disk-only boot to LightDM, followed by i3 login.
- Normal user prompt without `(live)`; no `/etc/debian_chroot` marker remains.
- QEMU framebuffer inspection and generated configuration confirm the GRUB entry reads `ABS Linux GNU/Linux`, not a literal shell command.
- New-user configuration ownership, mounted ESP/root, active swap, sudo access.
- No failed system or user units; live account, installer launcher and live-only
  packages removed.
- `apt-get update` succeeds for Debian and Brave with no duplicate-source or
  signature errors.
- Brave launches from Super+B in the live image. Both live and installed accounts
  report `brave-browser.desktop` as the default browser; installed `xdg-open
  https://example.com` launches Brave and displays the page.
- Super+N opens NetworkManager setup; its connection list shows the active virtual
  wired connection. Wi-Fi requires a physical radio and remains a hardware check.
- Screenshot keyboard selection (Ctrl+A), Save (Ctrl+S), cancellation and the
  recovery shortcut were exercised. A PNG was saved in the installed test account.
- Eleven automated tests, including the Rofi parser, ShellCheck/i3 validation,
  scoped Brave key configuration, public-key packet inspection, and a subprocess
  test that verifies bar-launched applications detach and receive closed stdin.

## Issue disposition and limits

- **#2 GRUB label:** resolved by disabling `keep_distributor` so Calamares uses the
  plain ABS branding label. Debian OS identity and EFI bootloader ID stay unchanged.
- **#3 Live prompt:** resolved; target finalization removes only the known `live`
  chroot marker. The upgrade guide preserves custom labels.
- **#1 Screenshot:** partially addressed, stays open. Launches now wait for input
  release and detach from bar status execution; Super+Shift+Esc terminates the
  user's Flameshot process. Keyboard capture/save and recovery passed. Automated
  pointer drags did not reliably produce a selected region, and the original X13
  freeze has not been conclusively reproduced and resolved. Do not claim the full
  issue is fixed. A guest-only xdotool/XInput experiment did not establish a remedy;
  no experimental Qt override or test package is included in the ISO.
- **#4 Wi-Fi:** setup entry points implemented; stays open pending real X13 network
  selection, password entry and successful association. The VM contains no Wi-Fi
  radio. The new workflow uses Super+N or the network status, then Activate a connection.

The user reported successful installation of alpha.1 on a fresh Lenovo X13.
That is useful hardware evidence for alpha.1, not an alpha.2 hardware acceptance
claim. Secure Boot, encryption, ESP reuse, suspend and physical-device tests remain
separate. Existing alpha.1 users can follow [the update guide](upgrade-alpha1.md).

## Evidence

Actual QEMU `screendump` PNGs and VM disks are retained locally (gitignored):

- `build/output/vm-alpha2/screenshots/02-live.png`: new wallpaper.
- `06-summary.png`, `09-complete.png`: reviewed layout and offline completion.
- `grub-3.png`: actual installed GRUB menu with the corrected label.
- `11-installed-prompt.png`: installed Fastfetch and corrected shell prompt.
- `12-network.png`, `13-network-connections.png`: setup UI and wired connection.
- `14-default-browser-link.png`: HTTP link opened in Brave.
- `19-capture-now.png`: screenshot Save dialog; `installed-checks.txt` records the PNG.
- `installed-checks.txt`, `installed-block-devices.json`: guest audit and detached ISO.
- `build/output/vm-alpha2-live/screenshots/01-brave.png`, `02-default-browser.png`:
  live Brave and default-browser registration.

The original `ABSLinux_wallpaper_0.png` is copied unchanged into the desktop payload;
its SHA-256 is `fb9c20f5e36f6c66047092484847170be3e669bd55c8e69c6054623b551311f4`.
The installer continues to use the original hero artwork.
