# Installer and live-image architecture

ABS Linux is a curated Debian-based Linux desktop distribution built around i3,
designed to remain understandable, controllable, hardware-adaptive, and close to
upstream Debian. The base is Debian 13 Stable (Trixie), currently amd64.

```text
source manifests + templates + original ABS artwork
                ↓ live-build (fresh Debian packages, never a host snapshot)
live filesystem + /etc/skel + Calamares + offline desktop package set
                ↓ upstream Calamares modules
GPT / EFI System Partition / ext4 + Debian system + target user
                ↓ bootstrap/install.sh → bootstrap/lib/deploy.py
ABS user configuration and runtime tools
                ↓ abs-capabilities → abs-bar
capability-selected i3blocks battery/Bluetooth modules; touch keyboard on demand
```

## Ownership and handoff

APT owns the kernel, firmware, initramfs, GRUB, systemd, NetworkManager, PipeWire,
Xorg, i3, LightDM, and applications. ABS does not modify `/etc/os-release` or
maintain an independent Debian package base. NetworkManager owns runtime DNS.
The image configures Debian main/non-free-firmware, updates, and security sources.

`bootstrap/packages/*.list` is the common package source; inline comments record
why each package is included. `profiles/profiles.json` maps capabilities to groups.
The live image includes every currently supported hardware group to install
offline and tolerate hardware changes. Manual bootstrap selects relevant groups.
Development and optional manifests are deliberately excluded from both defaults.
There is no package list duplicated inside Calamares.

`bootstrap/lib/deploy.py` is shared by manual bootstrap, image skeleton creation,
and Calamares' `shellprocess@abs-deploy` job. Calamares creates the user first;
the deployment then validates that account in the target `/etc/passwd`, seeds its
configuration, and sets ownership. Calamares runs this job **inside its target
chroot**. No shell parsing of a discovered mountpoint is used.

| Kind | Location | Ownership / update rule |
| --- | --- | --- |
| Source | repository `config`, `scripts`, `profiles`, `bootstrap` | reviewed source |
| System payload | `/usr/share/abs` | ABS-managed, replaced by explicit deployment |
| Runtime commands | `/usr/local/bin/abs-*` | ABS-managed, root-owned on real installations |
| Initial image user defaults | `/etc/skel/.config` | created during image staging |
| User configuration | `~/.config/{i3,i3blocks,rofi,dunst,kitty,fastfetch}` | user-editable; differing existing files block redeployment before writes |
| Generated bar configuration | private temporary directory under `$XDG_RUNTIME_DIR` | user-owned, removed on bar exit |
| Capability facts | JSON on stdout | read-only snapshot; no persistent machine identity |

The deployment plan is dry-run by default. `--apply` is explicit, and
`--install-packages` additionally authorizes APT operations. It rejects source or
destination symlinks, missing users, privileged users, and conflicting user files.
System-managed files are updated; unrelated user files are never swept or removed.
This is initial-install tooling, not yet a transactional updater or rollback system.
A failed copy/APT operation may leave partial changes; fix the reported problem
and rerun. Back up user changes before deliberately moving conflicting files aside.

## Calamares sequence

Welcome → location → keyboard → partition → users → summary → install → finish.
Upstream modules partition and mount the selected disk, unpack the immutable live
squashfs, create machine identity, write fstab/crypttab, configure locale and user,
select LightDM/i3, enable services, deploy ABS, install GRUB, remove live packages,
regenerate initramfs, and unmount. The installer requires confirmation before the
execution phase. No disk or erase operation is preselected.

The initial supported test target is **UEFI/GPT/ext4**. Erase-disk installation
creates a 512 MiB ESP and an ext4 root; manual partitioning remains available.
The default uses a small swap partition, with a no-swap alternative. Hibernation
is not configured. Secure Boot is disabled in this initial build configuration;
BIOS installation is outside this pass.

The upstream encryption UI/plumbing is present (LUKS1 for GRUB compatibility,
cryptsetup-initramfs and protected key material), but encrypted installs are
**unvalidated** and are not the acceptance baseline. Btrfs, swapfiles, LVM,
automatic rotation, and resume/hibernate need separate design and VM/hardware
validation. The manual partitioning UI may expose upstream filesystem options;
only unencrypted ext4 is in the initial acceptance matrix.

Calamares and its dependencies come directly from Debian. ABS supplies settings,
branding, and a shellprocess adapter, without a Calamares source fork or Debian
helper fork. The image preinstalls GRUB and all desktop packages so Calamares does
not need a network download. The packages job purges live-boot/live-config and
Calamares before initramfs regeneration. Installation unpacks the build squashfs,
not the running live overlay. Network profiles and live-session credentials are
not copied by a networkcfg job; reconnect after the installed system boots.

## Build reproducibility boundary

See [Build and VM instructions](../build/README.md). Builds use fresh directories,
a fixed Debian suite/architecture, explicit manifests, and source-controlled
configuration. Debian mirrors still move: this is a repeatable build recipe,
**not a bit-for-bit reproducible release**. The generated package manifest and
ISO checksums must be retained for each test build. Snapshot pinning, signed
releases, source archives, SBOMs, and a packaged ABS payload are future release
engineering work.

## Future Guix boundary

APT remains responsible for the OS, kernel, drivers, system plumbing, and core
desktop. Guix may later provide optional developer environments, selected newer
user-space tools, and reproducible application environments. No Guix code or
bootstrap dependency is introduced. It must never be required to boot, install,
update, or repair ABS.

## Upstream references checked for this implementation

- [Debian Trixie Calamares package](https://packages.debian.org/trixie/calamares)
  (3.3.14-1 extracted for module and dependency checks).
- [Debian Calamares settings](https://packages.debian.org/trixie/calamares-settings-debian)
  (13.0.13-1 inspected as a sequence reference, not installed or copied wholesale).
- [Calamares 3.3.14 configuration](https://github.com/calamares/calamares/tree/v3.3.14/src/modules)
  (partition, shellprocess, users, services, GRUB, packages, and initramfs semantics).
- [Debian live-build configuration](https://manpages.debian.org/trixie/live-build/lb_config.1.en.html)
  and [live-config](https://manpages.debian.org/trixie/live-config-doc/live-config.7.en.html).
