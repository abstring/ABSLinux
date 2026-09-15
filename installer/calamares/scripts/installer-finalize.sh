#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Run inside the target chroot, exclusively from Calamares.
set -euo pipefail
[[ $(stat -Lc '%d:%i' /) != $(stat -Lc '%d:%i' /proc/1/root) ]] || {
    echo 'Refusing to finalize outside a target chroot' >&2
    exit 1
}
# The live medium is visible to Calamares but not at this path in its target.
if [[ -e /run/live/medium/live/filesystem.squashfs ]]; then
    echo 'Refusing to finalize a running live system' >&2
    exit 1
fi
[[ -d /sys/firmware/efi ]] || { echo 'UEFI installation required' >&2; exit 1; }
# Image-local files, not network profiles or arbitrary user state.
rm -f /usr/share/applications/abs-install.desktop /usr/local/bin/abs-install
# Debian live-build's chroot marker must not label installed shell prompts.
if [[ -f /etc/debian_chroot && $(cat /etc/debian_chroot) == live ]]; then
    rm /etc/debian_chroot
fi
# Ensure an encrypted install never leaves key material in world-readable initramfs.
install -d /etc/initramfs-tools/conf.d
printf '%s\n' 'UMASK=0077' > /etc/initramfs-tools/conf.d/abs-permissions
# Package removal below must not download anything. Existing Debian sources remain.
# NetworkManager creates runtime DNS configuration on the first installed boot.
ln -sfn /run/NetworkManager/resolv.conf /etc/resolv.conf
