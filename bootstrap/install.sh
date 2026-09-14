#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
export PYTHONDONTWRITEBYTECODE=1
exec python3 "$repo/bootstrap/lib/deploy.py" "$@"
