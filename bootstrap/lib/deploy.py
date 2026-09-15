#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared ABS deployment. Default is a read-only plan; --apply changes files."""
import argparse
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

SOURCE = Path(__file__).resolve().parents[2]
PAYLOAD = ('bootstrap', 'config', 'profiles', 'scripts')

def packages(groups):
    result = set()
    for group in groups:
        if not re.fullmatch(r'[a-z]+', group):
            raise ValueError('Invalid package group')
        for line in (SOURCE / 'bootstrap/packages' / (group + '.list')).read_text().splitlines():
            name = line.split('#', 1)[0].strip()
            if name:
                if not re.fullmatch(r'[a-z0-9][a-z0-9+.-]+', name):
                    raise ValueError('Invalid package: ' + name)
                result.add(name)
    return sorted(result)

def groups_for(caps):
    profiles = json.loads((SOURCE / 'profiles/profiles.json').read_text())
    return profiles['common'] + [g for cap, groups in profiles['capabilities'].items()
                                 if caps.get(cap, False) for g in groups]

def configure_brave(root):
    for source, destination in (
        ('brave-browser-archive-keyring.gpg', 'usr/share/keyrings/brave-browser-archive-keyring.gpg'),
        ('brave-browser-release.sources', 'etc/apt/sources.list.d/brave-browser-release.sources'),
    ):
        target = target_path(root, destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE / 'bootstrap/apt' / source, target)
        target.chmod(0o644)

def target_path(root, relative):
    path = root / relative
    # Refuse symlink traversal, including a symlink destination, before writing.
    for part in (path, *path.parents):
        if part == root:
            break
        if part.is_symlink():
            raise ValueError('Refusing symlink destination: ' + str(part))
    if not path.resolve().is_relative_to(root):
        raise ValueError('Path escapes target: ' + str(path))
    return path

def plan(root, user=None, skel=False):
    owner = None
    if skel:
        home = Path('etc/skel')
    else:
        if not user or not re.fullmatch(r'[a-z_][a-z0-9_-]*', user):
            raise ValueError('Supply a normal target --user')
        records = [x.split(':') for x in (root / 'etc/passwd').read_text().splitlines()]
        record = next((x for x in records if x[0] == user), None)
        if record is None or int(record[2]) < 1000 or not record[5].startswith('/home/'):
            raise ValueError('Target user must exist with UID >= 1000 and a home under /home')
        owner = (int(record[2]), int(record[3]))
        home = Path(record[5].lstrip('/'))
        if '..' in home.parts:
            raise ValueError('Unsafe user home')
    entries = []
    for folder in PAYLOAD:
        for src in sorted((SOURCE / folder).rglob('*')):
            if src.is_symlink():
                raise ValueError('Source symlink rejected: ' + str(src))
            if src.is_file() and '__pycache__' not in src.parts and not src.name.endswith('.pyc'):
                entries.append((src, Path('usr/share/abs') / src.relative_to(SOURCE), None, True))
    for src in sorted((SOURCE / 'config').rglob('*')):
        if src.is_file() and src.name != 'README.md' and 'wallpaper' not in src.relative_to(SOURCE / 'config').parts:
            entries.append((src, home / '.config' / src.relative_to(SOURCE / 'config'), owner, False))
    for src in sorted((SOURCE / 'scripts').glob('abs-*')):
        entries.append((src, Path('usr/local/bin') / src.name, None, True))
    result = []
    for src, rel, uid, managed in entries:
        dst = target_path(root, rel)
        if dst.exists() and not dst.is_file():
            raise ValueError('Destination is not a file: ' + str(dst))
        if dst.exists() and src.read_bytes() != dst.read_bytes() and not managed:
            raise ValueError('User configuration conflict (back up and move it first): ' + str(dst))
        result.append((src, dst, uid))
    return result

def apply_files(entries, root):
    for src, dst, owner in entries:
        missing = []
        parent = dst.parent
        while not parent.exists():
            missing.append(parent)
            parent = parent.parent
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.resolve() != dst.resolve():
            shutil.copyfile(src, dst)
            dst.chmod(0o755 if os.access(src, os.X_OK) else 0o644)
        if owner and os.geteuid() == 0:
            os.chown(dst, *owner)
            for directory in missing:
                os.chown(directory, *owner)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path('/'))
    choice = p.add_mutually_exclusive_group(required=True)
    choice.add_argument('--user')
    choice.add_argument('--skel', action='store_true', help='Seed image skeleton; requires a staging root')
    p.add_argument('--apply', action='store_true')
    p.add_argument('--install-packages', action='store_true', help='APT install on running Debian 13 only')
    p.add_argument('--all-hardware', action='store_true', help='Image package plan includes all supported hardware groups')
    args = p.parse_args()
    if args.root.is_symlink():
        raise ValueError('Target root cannot be a symlink')
    root = args.root.resolve()
    if args.skel and root == Path('/'):
        raise ValueError('--skel requires a staging root')
    loader = importlib.machinery.SourceFileLoader('capabilities', str(SOURCE / 'scripts/abs-capabilities'))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    detector = importlib.util.module_from_spec(spec)
    loader.exec_module(detector)
    caps = detector.detect()
    groups = groups_for(caps)
    if args.all_hardware:
        groups = ['base', 'desktop', 'laptop', 'touch', 'trackpoint', 'bluetooth']
    selected = packages(groups)
    entries = plan(root, args.user, args.skel)
    if root == Path('/') or args.install_packages:
        release = dict(line.split('=', 1) for line in (root / 'etc/os-release').read_text().splitlines() if '=' in line)
        if release.get('ID', '').strip('"') != 'debian' or release.get('VERSION_ID', '').strip('"') != '13':
            raise ValueError('Only Debian 13 is supported')
    if args.install_packages and root != Path('/'):
        raise ValueError('APT mode requires --root /; image packages belong to live-build')
    print(json.dumps({'apply': args.apply, 'root': str(root), 'capabilities': caps,
                      'groups': groups, 'packages': selected, 'files': [str(e[1]) for e in entries]}, indent=2))
    if not args.apply:
        return
    if root == Path('/') and os.geteuid() != 0:
        raise ValueError('--apply to / requires root')
    if args.install_packages:
        configure_brave(root)
        subprocess.run(['apt-get', 'update'], check=True)
        subprocess.run(['apt-get', 'install', '--no-install-recommends', '-y', *selected], check=True)
    apply_files(entries, root)

if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        sys.exit('ABS deployment: ' + str(error))
