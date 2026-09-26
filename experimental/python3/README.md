# Ren'Py 8 native bootstrap

This branch builds dependencies for a native Ren'Py 8.3.7 runtime. The
existing Ren'Py 7.6.3 runtime uses Python 2.7 and cannot load Python 3 game
scripts. The CI build now produces a Python 3.9 static library, a small
smoke-test NSO/NRO, and a static pygame_sdl2 library. It also generates
Ren'Py 8 Cython sources and attempts to cross-compile all 43 native modules.

libhydrogen's entropy initialization uses libnx's `csrng` service on Switch.
The source archive and pygame_sdl2 archive are downloaded from the official
Ren'Py 8.3.7 release and SHA-256 checked before compilation.

All 66 native modules (23 pygame_sdl2 and 43 Ren'Py) now register and link in
an ARM64 executable. Switch uses SDL's frame allocation path in ffmedia.
Python initialization uses PyConfig's path list to preserve the colon in
RomFS paths. The import probe bundles the pure Python packages as well.

Both NROs still need hardware testing. `smoke.nro` checks Python initialization
and writes `sdmc:/renpy8-python-smoke.txt`. `link-probe.nro` checks imports of
`_renpy`, `pygame_sdl2`, and `renpy`, writing `sdmc:/renpy8-link-probe.txt`
and `sdmc:/renpy8-link-probe-errors.txt`. Neither starts the game. Next comes
the full engine bootstrap, followed by testing input, saves, audio, and video.
No Agent17 assets belong in this repository.
