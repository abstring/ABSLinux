# Build an ABS Linux live ISO

Target: Debian 13 amd64, UEFI, Secure Boot disabled, GPT/ext4 installation.
Build in a disposable Debian 13 VM where practical. These commands do not write
an ISO to any physical device. Budget at least 20 GiB free space (30 GiB advised),
4 GiB RAM, and network access to Debian mirrors.

## Prerequisites

```sh
sudo apt-get update
sudo apt-get install live-build debootstrap squashfs-tools xorriso \
  grub-common grub-efi-amd64-bin mtools dosfstools python3 python3-yaml \
  shellcheck qemu-system-x86 qemu-utils ovmf
```

QEMU/OVMF are needed for VM testing, not image staging. `shellcheck` is used when
available. Tests also use the installed i3 parser when available.

## Validate, prepare, build

Run from the repository root as your normal development user:

```sh
./tests/run.sh
./build/build-iso.sh --check
./build/build-iso.sh --prepare-only  # no root, no package installation, no lb required
./build/build-iso.sh --build         # prompts through sudo for lb build
```

No argument performs `--check`. This deliberate default makes the command safe
to explore. Each prepare/build creates a unique `build/output/run-*` directory.
The generated `config/includes.chroot`, package lists and hook are reviewable.
Nothing copies a home directory, network profiles, or the running root filesystem.
Successful builds read `VERSION` and leave an
`abs-linux-<version>-amd64.hybrid.iso`, live-build package/build metadata,
and `SHA256SUMS` inside that run directory. Generated files are gitignored.

A rerun starts fresh; it never deletes an earlier chroot or mounted build tree.
After a failed build, inspect mounts below that specific run directory and use
`sudo lb clean --purge` **from that run directory** before manually reclaiming it.
Do not recursively delete a tree that still has mounted filesystems.

Only `--build` requires host build prerequisites. The script fails on errors and
does not start Calamares, format disks, change the developer desktop, or flash USB.
Builds follow moving Debian mirrors; byte reproducibility is not yet claimed.

## First VM boot and installation

Use a fresh directory and a **new virtual disk**. Replace the ISO path with the
actual output of the completed build. Do not pass host block devices to QEMU.

```sh
mkdir -p build/output/vm-ext4
cd build/output/vm-ext4
cp /usr/share/OVMF/OVMF_VARS_4M.fd OVMF_VARS.fd
qemu-img create -f qcow2 system.qcow2 32G
qemu-system-x86_64 -enable-kvm -m 4096 -smp 2 \
  -drive if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE_4M.fd \
  -drive if=pflash,format=raw,file=OVMF_VARS.fd \
  -drive file=system.qcow2,if=virtio,format=qcow2 \
  -cdrom /absolute/path/to/abs-linux-amd64.hybrid.iso \
  -boot d -nic user,model=virtio-net-pci -vga virtio
```

If KVM is unavailable, omit `-enable-kvm`; emulation will be slower. OVMF package
filenames can vary: use the matching non-Secure-Boot CODE/VARS pair on your host.
The live account is `live`; Debian live-config's default live password is `live`.
This account is created at live boot and is not shipped in the squashfs account
database. Select “Install ABS Linux” in Rofi, or run `abs-install` from a terminal.
The installer launcher rejects a non-live or non-UEFI environment.

1. Verify the live desktop, artwork, Rofi, notifications, audio, networking and
   installer pages. Record Calamares/live-build package versions and ISO checksum.
2. In the VM only, choose erase disk, ext4 and small swap; create a new user.
3. Complete installation. Power off, then rerun QEMU **without `-cdrom` and
   `-boot d`**, retaining the same qcow2 disk and OVMF variable file.
4. Verify UEFI boot, LightDM/i3 login, user configuration ownership, sudo,
   `/etc/os-release` reporting Debian 13, `findmnt / /boot/efi`, `swapon --show`,
   `systemctl --failed`, and `apt-get update`. Check that live packages and the
   installer launcher are absent and the installed user is not auto-logged in.
5. Repeat in a second new VM disk using manual GPT partitioning: FAT32 ESP mounted
   at `/boot/efi` and ext4 root at `/`. Do not format an existing ESP when testing
   reuse. Also test offline installation with `-nic none`.
6. Encryption, ESP reuse, hardware suspend, touchscreen and native TrackPoint
   require separate test runs. Do not treat syntax tests as boot/install evidence.

## QEMU screenshot monitoring

For a headless guest, add these options to the QEMU command above:

```sh
-display none -qmp unix:/absolute/path/to/vm/qmp.sock,server=on,wait=off
```

QEMU's QMP `screendump` captures the actual guest framebuffer. Run this with
Python 3, using paths writable by the QEMU process owner:

```python
import json
import socket

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect("/absolute/path/to/vm/qmp.sock")
stream = sock.makefile("rwb", buffering=0)
json.loads(stream.readline())  # greeting

def call(command, arguments=None):
    stream.write((json.dumps({"execute": command,
                              "arguments": arguments or {}}) + "\n").encode())
    while True:
        reply = json.loads(stream.readline())
        if "error" in reply:
            raise RuntimeError(reply["error"])
        if "return" in reply:
            return reply["return"]

call("qmp_capabilities")
call("screendump", {"filename": "/absolute/path/to/vm/screenshot.png",
                    "format": "png"})
```

## Validation evidence

The 2026-09-14 build and QEMU tests passed the UEFI/ext4 VM acceptance gate.
See [the validation report](../docs/vm-validation.md) for the final ISO checksum,
build versions, automatic/manual/offline results, screenshots and remaining limits.
Build outputs, VM disks and raw screenshots are retained locally under
`build/output/` and excluded from Git. No physical disk was passed into QEMU.

Release naming, checksums and publication are documented in [Releases](../docs/releases.md).
