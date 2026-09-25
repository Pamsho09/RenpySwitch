# Ren'Py 8 native bootstrap

This branch probes the first dependency for a native Ren'Py 8.3 runtime:
CPython 3.9 built for libnx. The existing Ren'Py 7.6.3 runtime uses
`libpython2.7.a`; it cannot load Python 3 game scripts.

`bootstrap.sh` intentionally stops at `libpython3.9.a`. A successful cross
compile alone does not make a usable runtime. The library must still be linked
with libnx, initialized in an NSO, and tested on Switch. Then pygame_sdl2 and
Ren'Py 8 native modules must be compiled, followed by game initialization,
input, saves, audio, and video. No Agent17 assets belong in this repository.
