#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Prepare a new live-build directory, without root or installing packages."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys

repo = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('deploy', repo / 'bootstrap/lib/deploy.py')
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)

def prepare(work):
    if work.exists() and any(work.iterdir()):
        raise ValueError('Use a new empty build directory')
    root = work / 'config/includes.chroot'
    root.mkdir(parents=True)
    subprocess.run([str(repo / 'bootstrap/install.sh'), '--root', str(root), '--skel', '--all-hardware', '--apply'],
                   check=True, stdout=subprocess.DEVNULL)
    cal = repo / 'installer/calamares'
    (root / 'etc/calamares').mkdir(parents=True)
    for name in ('settings.conf', 'modules', 'branding'):
        src = cal / name
        if src.is_dir():
            shutil.copytree(src, root / 'etc/calamares' / name)
        else:
            shutil.copyfile(src, root / 'etc/calamares' / name)
    shutil.copyfile(cal / 'scripts/installer-finalize.sh', root / 'usr/share/abs/installer-finalize.sh')
    (root / 'usr/share/abs/installer-finalize.sh').chmod(0o755)
    shutil.copyfile(cal / 'scripts/abs-install', root / 'usr/local/bin/abs-install')
    (root / 'usr/local/bin/abs-install').chmod(0o755)
    (root / 'usr/share/applications').mkdir(parents=True)
    shutil.copyfile(cal / 'abs-install.desktop', root / 'usr/share/applications/abs-install.desktop')
    # APT and live-build install the packages; deployment never shells out to
    # APT against a mounted target or guesses the host's devices.
    pkgs = deploy.packages(['base', 'desktop', 'laptop', 'touch', 'trackpoint', 'bluetooth'])
    pkgs += [line.split('#', 1)[0].strip() for line in (cal / 'package-lists/live.list').read_text().splitlines()]
    lists = work / 'config/package-lists'
    lists.mkdir(parents=True)
    (lists / 'abs.list.chroot').write_text('\n'.join(sorted(set(filter(None, pkgs)))) + '\n')
    hooks = work / 'config/hooks/live'
    hooks.mkdir(parents=True)
    shutil.copyfile(repo / 'build/0100-abs.hook.chroot', hooks / '0100-abs.hook.chroot')
    (hooks / '0100-abs.hook.chroot').chmod(0o755)
    # LightDM i3 is a deliberate new-image choice, not a change to the developer host.
    lightdm = root / 'etc/lightdm/lightdm.conf.d'
    lightdm.mkdir(parents=True)
    (lightdm / '50-abs.conf').write_text('[Seat:*]\nuser-session=i3\n')
    print(work)

if __name__ == '__main__':
    prepare(Path(sys.argv[1]).resolve())
