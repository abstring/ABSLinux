#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Safe installer tests: temporary directories and package metadata only."""
import hashlib
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
import yaml

REPO = Path(__file__).resolve().parents[1]

def load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module

deploy = load('deploy', REPO / 'bootstrap/lib/deploy.py')
detector = load('detector', REPO / 'scripts/abs-capabilities')

class Foundation(unittest.TestCase):
    def test_config_and_execution_order(self):
        cal = REPO / 'installer/calamares'
        for p in [*cal.rglob('*.conf'), *cal.rglob('*.desc')]:
            self.assertIsInstance(yaml.safe_load(p.read_text()), dict, p)
        settings = yaml.safe_load((cal / 'settings.conf').read_text())
        self.assertFalse(settings['dont-chroot'])
        self.assertTrue(settings['prompt-install'])
        sequence = settings['sequence'][1]['exec']
        for before, after in [('partition','mount'),('mount','unpackfs'),('unpackfs','users'),
                              ('luksbootkeyfile','fstab'),('users','shellprocess@abs-deploy'),
                              ('packages','initramfs'),('initramfs','umount')]:
            self.assertLess(sequence.index(before), sequence.index(after))
        for instance in settings['instances']:
            self.assertTrue((cal / 'modules' / instance['config']).is_file())
            self.assertIn(instance['module'] + '@' + instance['id'], sequence)
        root = Path(os.environ.get('ABS_CALAMARES_ROOT', '/'))
        module_dirs = list((root / 'usr/lib').glob('*/calamares/modules'))
        if module_dirs:
            for name in set(settings['sequence'][0]['show'] + sequence + ['finished']):
                self.assertTrue(any((d / name.split('@')[0] / 'module.desc').is_file() for d in module_dirs), name)
        services = yaml.safe_load((cal / 'modules/services-systemd.conf').read_text())
        self.assertTrue(all(u['action'] == 'enable' for u in services['units']))
        partition = yaml.safe_load((cal / 'modules/partition.conf').read_text())
        self.assertEqual(partition['defaultFileSystemType'], 'ext4')
        self.assertEqual(partition['initialPartitioningChoice'], 'none')
        self.assertEqual(partition['defaultPartitionTableType'], 'gpt')
        branding = cal / 'branding' / settings['branding']
        brand = yaml.safe_load((branding / 'branding.desc').read_text())
        for name in [*brand['images'].values(), brand['slideshow']]:
            self.assertTrue((branding / name).is_file(), name)
        self.assertEqual((branding / 'hero.png').read_bytes(), (REPO / 'ABSLinux_hero_ad.png').read_bytes())

    def test_manifests(self):
        names = set()
        for p in [*(REPO / 'bootstrap/packages').glob('*.list'), *(REPO / 'installer/calamares/package-lists').glob('*.list')]:
            local = set()
            for line in p.read_text().splitlines():
                name = line.split('#', 1)[0].strip()
                if not name:
                    continue
                self.assertRegex(name, r'^[a-z0-9][a-z0-9+.-]+$')
                self.assertIn('#', line, 'Each package needs a reason')
                self.assertNotIn(name, local)
                names.add(name)
                local.add(name)
        if shutil.which('apt-cache'):
            for name in sorted(names):
                output = subprocess.check_output(['apt-cache', 'show', name], text=True)
                self.assertIn('Package: ' + name + '\n', output, name)
        for groups in json.loads((REPO / 'profiles/profiles.json').read_text())['capabilities'].values():
            self.assertTrue(deploy.packages(groups))

    def test_capability_fixtures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertFalse(any(detector.detect(root, []).values()))
            def put(p, text):
                f = root / p; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(text)
            put('class/power_supply/pack/type', 'Battery')
            put('class/input/event0/device/capabilities/sw', '2')
            put('class/drm/card0-eDP-1/status', 'connected')
            put('class/drm/card0-DP-1/status', 'connected')
            put('class/bluetooth/hci0/present', '1')
            put('bus/iio/devices/iio:device0/in_accel_x_raw', '0')
            caps = detector.detect(root, [{'ID_INPUT_TOUCHSCREEN':'1'}, {'ID_INPUT_POINTINGSTICK':'1'}])
            for cap in ('battery','tablet_mode','multi_monitor','bluetooth','rotation_sensor','touchscreen','trackpoint'):
                self.assertTrue(caps[cap], cap)
            self.assertIn('touch', deploy.groups_for(caps))
            self.assertIn('trackpoint', deploy.groups_for(caps))
            put('class/power_supply/pack/scope', 'Device')
            self.assertFalse(detector.detect(root, [])['battery'])
            put('class/power_supply/pack/scope', 'System')
            put('class/power_supply/pack/present', '0')
            self.assertFalse(detector.detect(root, [])['battery'])

    def test_deployment_dry_run_idempotency_and_conflicts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'etc').mkdir()
            uid = os.getuid() or 1000
            gid = os.getgid() or 1000
            (root / 'etc/passwd').write_text(f'tester:x:{uid}:{gid}:Test:/home/tester:/bin/bash\n')
            cmd = [str(REPO / 'bootstrap/install.sh'), '--root', str(root), '--user', 'tester']
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
            def snapshot():
                return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in root.rglob('*') if p.is_file()}
            before = snapshot()
            subprocess.run(cmd, env=env, check=True, stdout=subprocess.DEVNULL)
            self.assertEqual(before, snapshot(), 'Dry run must not write')
            subprocess.run(cmd + ['--apply'], env=env, check=True, stdout=subprocess.DEVNULL)
            once = snapshot()
            subprocess.run(cmd + ['--apply'], env=env, check=True, stdout=subprocess.DEVNULL)
            self.assertEqual(once, snapshot())
            config = root / 'home/tester/.config/i3/config'
            self.assertEqual(config.stat().st_uid, uid)
            config.write_text('# user edits\n')
            edited = snapshot()
            result = subprocess.run(cmd + ['--apply'], env=env, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b'User configuration conflict', result.stderr)
            self.assertEqual(edited, snapshot(), 'Conflicts must fail before any writes')

    def test_symlink_escape_and_unknown_user(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root = Path(tmp)
            (root / 'etc').mkdir()
            (root / 'etc/skel').symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'symlink'):
                deploy.plan(root, skel=True)
            (root / 'etc/passwd').write_text('root:x:0:0:root:/root:/bin/bash\n')
            with self.assertRaises(ValueError):
                deploy.plan(root, 'root')
            with self.assertRaises(ValueError):
                deploy.plan(root, 'unknown')
            self.assertEqual(list(Path(outside).iterdir()), [])

    def test_live_image_staging(self):
        prep = load('prepare', REPO / 'build/prepare.py')
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / 'build'
            prep.prepare(work)
            root = work / 'config/includes.chroot'
            self.assertTrue((root / 'usr/share/abs/bootstrap/install.sh').is_file())
            self.assertTrue((root / 'etc/skel/.config/i3/config').is_file())
            for p in ('usr/local/bin/abs-install','usr/share/abs/installer-finalize.sh'):
                self.assertTrue(os.access(root / p, os.X_OK))
            self.assertFalse((root / 'home').exists())
            self.assertFalse((root / 'etc/passwd').exists())
            self.assertFalse(list(root.rglob('.git')))
            self.assertFalse(list(root.rglob('__pycache__')))
            with self.assertRaises(ValueError):
                prep.prepare(work)
            packages = (work / 'config/package-lists/abs.list.chroot').read_text().splitlines()
            self.assertIn('grub-efi-amd64', packages)
            self.assertIn('user-setup', packages)
            self.assertIn('console-setup', packages)
            self.assertFalse((root / 'etc/apt/sources.list.d/abs.sources').exists())
            self.assertIn('qml6-module-qtquick', packages)
            self.assertNotIn('calamares-settings-debian', packages)

    def test_script_syntax_and_portability(self):
        shell = []
        for folder in ('bootstrap','build','scripts','installer'):
            for p in (REPO / folder).rglob('*'):
                if not p.is_file() or 'output' in p.parts or p.suffix == '.png':
                    continue
                text = p.read_text()
                if text.startswith('#!'):
                    self.assertNotRegex(text, r'(?m)^[^#\n]*\b(defuser|deb440|abstring)\b')
                    self.assertNotIn('/home/abstring', text)
                    if 'python3' in text.splitlines()[0]:
                        compile(text, str(p), 'exec')
                    else:
                        subprocess.run(['bash','-n',str(p)], check=True)
                        shell.append(str(p))
        checker = os.environ.get('SHELLCHECK') or shutil.which('shellcheck')
        if checker:
            subprocess.run([checker, *shell], check=True)
        else:
            print('NOTE: shellcheck unavailable; Bash syntax checked')
        if shutil.which('i3'):
            subprocess.run(['i3','-C','-c',str(REPO / 'config/i3/config')], check=True)

    def test_rofi_parser(self):
        if not shutil.which('rofi') or not os.environ.get('DISPLAY'):
            self.skipTest('Rofi parser check needs an X display')
        result = subprocess.check_output(['rofi', '-config', str(REPO / 'config/rofi/config.rasi'),
                                          '-dump-config'], text=True)
        self.assertRegex(result, r'(?:modi|modes): "drun,run";')
        self.assertRegex(result, r'(?m)^\s*font: "Noto Sans 12";')

    def test_no_obvious_secret_material(self):
        # Scan only distributable source, not prompts or developer home state.
        patterns = [r'-----BEGIN (?:OPENSSH|RSA|EC|DSA) PRIVATE KEY-----',
                    r'gh[pousr]_[A-Za-z0-9]{30,}', r'AKIA[A-Z0-9]{16}']
        for folder in ('bootstrap','config','profiles','scripts','installer','build'):
            for p in (REPO / folder).rglob('*'):
                if p.is_file() and 'output' not in p.parts and p.suffix != '.png':
                    text = p.read_text()
                    for pattern in patterns:
                        self.assertIsNone(re.search(pattern,text), str(p))

if __name__ == '__main__':
    unittest.main(verbosity=2)
