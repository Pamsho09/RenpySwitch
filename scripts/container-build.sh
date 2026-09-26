#!/usr/bin/env bash
set -euo pipefail

bash experimental/python3/bootstrap.sh

mkdir -p /artifacts
cp /tmp/python3-switch/Python-3.9.21/libpython3.9.a /artifacts/
cp /tmp/python3-switch/Python-3.9.21/pyconfig.h /artifacts/
cp /tmp/python3-switch/smoke.elf /artifacts/
cp /tmp/python3-switch/smoke.nso /artifacts/
cp /tmp/python3-switch/python39.zip /artifacts/
cp /tmp/python3-switch/romfs/Contents/renpy8.zip /artifacts/
cp /tmp/python3-switch/smoke.nro /artifacts/
cp /tmp/python3-switch/libpygame_sdl2.a /artifacts/
cp /tmp/python3-switch/librenpy8-modules.a /artifacts/
cp /tmp/python3-switch/librenpy8-support.a /artifacts/
cp /tmp/python3-switch/static_modules.c /artifacts/
cp /tmp/python3-switch/link-probe.elf /artifacts/
cp /tmp/python3-switch/link-probe.nro /artifacts/

cp /tmp/python3-switch/agent17.nro /artifacts/
cp /tmp/python3-switch/agent17.elf /artifacts/

echo "CPython 3.9 cross-compile probe ready in /artifacts"
