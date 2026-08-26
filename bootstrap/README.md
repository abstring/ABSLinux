# Bootstrap

This area will contain the idempotent path from a clean Debian Stable installation to an ABS Linux workstation.

`install.sh` is currently a safe placeholder: it reports that the installer is unfinished, changes nothing, and exits unsuccessfully so automation cannot mistake it for a completed installation. Future work will add preflight checks, package manifests in `packages/`, reusable functions in `lib/`, explicit confirmation for privileged changes, and clear recovery messages.
