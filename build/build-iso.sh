#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
export PYTHONDONTWRITEBYTECODE=1
version=$(<"$repo/VERSION")
[[ $version =~ ^[0-9]+\.[0-9]+\.[0-9]+(-(alpha|beta|rc)\.[1-9][0-9]*)?$ ]] || {
    echo 'Invalid VERSION; see docs/releases.md' >&2; exit 1;
}
case "${1:---check}" in
    --check|--prepare-only|--build) mode=${1:---check} ;;
    *) echo "Usage: $0 [--check|--prepare-only|--build]" >&2; exit 2 ;;
esac
[[ $# -le 1 ]] || { echo 'Unexpected arguments' >&2; exit 2; }
command -v python3 >/dev/null || { echo "Missing prerequisite: python3" >&2; exit 1; }
python3 -c 'import yaml' || { echo 'Install python3-yaml' >&2; exit 1; }
if [[ $mode != --prepare-only ]]; then
    for tool in lb debootstrap grep-dctrl rsvg-convert xorriso mksquashfs grub-mkstandalone mcopy mkfs.vfat; do
        command -v "$tool" >/dev/null || { echo "Missing $tool; see build/README.md prerequisites" >&2; exit 1; }
    done
    for path in /usr/lib/grub/x86_64-efi/configfile.mod /usr/lib/grub/i386-efi/configfile.mod \
                /usr/lib/grub/i386-pc/boot_hybrid.img /usr/lib/ISOLINUX/isohdpfx.bin \
                /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf; do
        [[ -f $path ]] || { echo "Missing $path; see build/README.md prerequisites" >&2; exit 1; }
    done
    [[ $(dpkg --print-architecture) == amd64 ]] || { echo 'amd64 build host required' >&2; exit 1; }
    # shellcheck disable=SC1091
    source /etc/os-release
    [[ $ID == debian && $VERSION_ID == 13 ]] || { echo 'Debian 13 build host required' >&2; exit 1; }
fi
if [[ $mode == --check ]]; then
    echo 'Build prerequisites available; use --build to create an ISO.'
    exit 0
fi
mkdir -p "$repo/build/output"
# Each run uses a new directory, never recursive cleanup of a mounted chroot.
work=$(mktemp -d "$repo/build/output/run-XXXXXXXX")
python3 "$repo/build/prepare.py" "$work"
[[ $mode != --prepare-only ]] || exit 0
available=$(df -Pk "$work" | awk 'NR == 2 {print $4}')
(( available >= 20971520 )) || { echo 'At least 20 GiB free space is required' >&2; exit 1; }
cd "$work"
lb config --ignore-system-defaults --mode debian --distribution trixie --architectures amd64 \
    --build-with-chroot false --debootstrap-options "--include=ca-certificates" \
    --archive-areas 'main non-free-firmware' --binary-images iso-hybrid \
    --bootloaders grub-efi --uefi-secure-boot disable --debian-installer none \
    --apt-recommends false --apt-indices true --firmware-chroot false --memtest none \
    --chroot-filesystem squashfs --image-name "abs-linux-$version" \
    --bootappend-live 'boot=live components username=live hostname=abs-live locales=en_US.UTF-8 keyboard-layouts=us'
# APT reads extra archives before live-build copies includes. Seed the scoped
# public key into the freshly bootstrapped build root before that first read.
if (( EUID == 0 )); then
    lb bootstrap
    install -Dm644 "$repo/bootstrap/apt/brave-browser-archive-keyring.gpg" \
        chroot/usr/share/keyrings/brave-browser-archive-keyring.gpg
    lb build
else
    sudo lb bootstrap
    sudo install -Dm644 "$repo/bootstrap/apt/brave-browser-archive-keyring.gpg" \
        chroot/usr/share/keyrings/brave-browser-archive-keyring.gpg
    sudo lb build
fi
iso=("$work"/*.iso)
[[ -f ${iso[0]} ]] || { echo "No ISO produced; inspect $work" >&2; exit 1; }
sha256sum -- "${iso[@]##*/}" > "$work/SHA256SUMS"
printf 'ISO build complete: %s\n' "${iso[@]}"
