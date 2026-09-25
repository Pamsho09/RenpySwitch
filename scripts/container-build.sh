#!/usr/bin/env bash
set -euo pipefail

bash setup.bash
bash build.bash

test -s raw/switch/exefs/main
test -s raw/switch/romfs/Contents/lib.zip
test -s raw/switch/romfs/Contents/loading.png
test -s renpy-switch.elf

mkdir -p /artifacts
cp -a raw/. /artifacts/
gzip -9 -c renpy-switch.elf > /artifacts/renpy-switch.elf.gz
(cd /artifacts && sha256sum switch/exefs/main switch/romfs/Contents/lib.zip switch/romfs/Contents/loading.png > SHA256SUMS)

echo "Runtime ready in /artifacts"
