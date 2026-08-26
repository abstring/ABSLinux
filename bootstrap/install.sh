#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

set -euo pipefail

readonly PROGRAM_NAME="${0##*/}"

main() {
    printf '%s\n' \
        "ABS Linux bootstrap is not implemented yet." \
        "No packages, configuration, or system files were changed." >&2
    return 1
}

main "$@"
