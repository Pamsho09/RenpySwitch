#!/usr/bin/env bash
set -euo pipefail

bash setup.bash
bash build.bash

test -s raw/switch/exefs/main
test -s raw/switch/romfs/Contents/lib.zip
test -s raw/switch/romfs/Contents/loading.png

mkdir -p /artifacts
cp -a raw/. /artifacts/
(cd /artifacts && sha256sum switch/exefs/main switch/romfs/Contents/lib.zip switch/romfs/Contents/loading.png > SHA256SUMS)

echo "Runtime ready in /artifacts"
