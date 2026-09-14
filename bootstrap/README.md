# Manual ABS deployment on Debian 13

Use an existing ordinary user account with a home under `/home`. Start with a
fresh account: differing files in the destination `.config` cause a preflight
failure. Existing user files are never silently overwritten.

```sh
./bootstrap/install.sh --user YOUR_USER
sudo ./bootstrap/install.sh --user YOUR_USER --install-packages --apply
```

The first command is a read-only plan. The second installs the capability-selected
APT packages and deploys ABS configuration. It does not partition disks, create
accounts, switch display managers, or modify `/etc/os-release`. Select i3 at your
existing login screen after installation. On a minimal system without a display
manager, install/configure a Debian display manager separately.

For a target-directory test, create a fixture `/etc/passwd` inside a temporary
root and use `--root /path/to/root --user tester`; see the automated tests.
`--skel --root /staging/root --apply` seeds the live image skeleton without a user
account. APT operations are rejected for alternate roots: live-build owns image
package installation, and Calamares reuses already installed image packages.

Capability detection reads the running hardware (also from the install environment
when called in Calamares). Bar behavior is detected again on each session/bar
start. Adding hardware later may require installing its documented package group
and restarting the bar/session; this is not a hotplug package manager.

The source payload lives in `/usr/share/abs`; the same command can be run there
for a later explicit deployment. System-managed payload/scripts may be replaced.
User edits require a deliberate backup/move of conflicting files before an
update. There is no transactional rollback or merge tool yet. APT failures and
I/O failures are reported rather than hidden.
