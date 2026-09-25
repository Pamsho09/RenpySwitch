# Ren'Py 8 native bootstrap

This branch builds dependencies for a native Ren'Py 8.3.7 runtime. The
existing Ren'Py 7.6.3 runtime uses Python 2.7 and cannot load Python 3 game
scripts. The CI build now produces a Python 3.9 static library, a small
smoke-test NSO/NRO, and a static pygame_sdl2 library. It also generates
Ren'Py 8 Cython sources and attempts to cross-compile all 43 native modules.

libhydrogen's entropy initialization uses libnx's `csrng` service on Switch.
The source archive and pygame_sdl2 archive are downloaded from the official
Ren'Py 8.3.7 release and SHA-256 checked before compilation.

The smoke NRO still needs a hardware test. The Ren'Py modules need complete
cross-compilation and linking into a game runtime, followed by testing input,
saves, audio, and video. A successful static build does not establish that
Agent17 runs. No Agent17 assets belong in this repository.
