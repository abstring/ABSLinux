# Safe foundation tests

Run `./tests/run.sh` with Python 3 and python3-yaml. Tests use temporary target
roots, synthetic sysfs/udev fixtures and read-only package metadata. They cover
YAML structure, module order and assets, package formatting and availability,
capability composition, dry-run/no-write behavior, rerun idempotency, user-file
conflicts, ownership, symlink escapes, build staging, Python/Bash syntax, hostname
branching and recognizable credential patterns. ShellCheck and the i3 parser run
when available. The secret scan is a basic guard, not proof of absence of secrets.

Set `SHELLCHECK=/path/to/shellcheck` to use an extracted checker. Set
`ABS_CALAMARES_ROOT=/path/to/extracted/deb/root` to additionally verify that every
referenced module exists in Debian's packaged Calamares. No test runs Calamares'
partition jobs or writes a block device. See `build/README.md` for the outstanding
VM installation matrix; these checks cannot establish bootloader correctness.
