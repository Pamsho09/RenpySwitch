#!/usr/bin/env bash
set -euo pipefail

bash experimental/python3/bootstrap.sh

mkdir -p /artifacts
cp /tmp/python3-switch/Python-3.9.21/libpython3.9.a /artifacts/
cp /tmp/python3-switch/Python-3.9.21/pyconfig.h /artifacts/
cp /tmp/python3-switch/smoke.elf /artifacts/
cp /tmp/python3-switch/smoke.nso /artifacts/
cp /tmp/python3-switch/python39.zip /artifacts/
cp /tmp/python3-switch/smoke.nro /artifacts/
cp /tmp/python3-switch/libpygame_sdl2.a /artifacts/
cp /tmp/python3-switch/renpy.pydict.o /artifacts/

echo "CPython 3.9 cross-compile probe ready in /artifacts"
