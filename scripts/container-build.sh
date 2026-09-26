#!/usr/bin/env bash
set -euo pipefail
case "${RUNTIME:-renpy8}" in
    renpy8) exec bash scripts/build-renpy8.sh ;;
    renpy7) exec bash scripts/build-renpy7.sh ;;
    *) echo "RUNTIME must be renpy7 or renpy8" >&2; exit 2 ;;
esac
