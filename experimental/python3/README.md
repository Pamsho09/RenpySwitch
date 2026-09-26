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

Both NROs have passed their basic hardware checks (see results below). `smoke.nro` checks Python initialization
and writes `sdmc:/renpy8-python-smoke.txt`. `link-probe.nro` checks imports of
`_renpy`, `pygame_sdl2`, and `renpy`, writing `sdmc:/renpy8-link-probe.txt`
and `sdmc:/renpy8-link-probe-errors.txt`. Neither starts the game. Next comes
the full engine bootstrap, followed by testing input, saves, audio, and video.
No Agent17 assets belong in this repository.

The static Python archive now explicitly includes portable stdlib extensions
in `Setup.local`, including zlib (required to open compressed RomFS ZIPs).
CPython entropy uses libnx csrng for both hash initialization and os.urandom;
service failures propagate instead of falling back to /dev/urandom.
The smoke probe exercises compression, serialization, math, and randomness.
Earlier smoke NROs without these changes are obsolete.

## Hardware result: 2026-09-26

Build 36261097610 failed on hardware before codec initialization:
`failed to get the Python codec of the filesystem encoding`.
Registration succeeded, but none of the engine imports ran. The probes now
record RomFS mount status, ZIP stat/open/seek, verbose imports and the original
Python exception. Both show PASS/FAIL and wait for A before returning to hbmenu.
Smoke also writes `sdmc:/renpy8-python-smoke-errors.txt`. This is diagnostic
instrumentation used to diagnose the codec startup failure.

Root cause found by inspecting the installed NRO: its file size equaled the
code size and no ASET section existed. elf2nro exits before writing assets when
only --romfsdir is set (its guard checks icon, NACP and --romfs). Both probes
now include NACP metadata. verify_nro.py fails the build unless the embedded
RomFS files exactly match their inputs by SHA-256.

Build 36262913082 passed Python initialization and all stdlib checks on Switch.
Engine imports then exposed two issues: Python 3.9's BuiltinImporter rejects
package paths for dotted static modules, and platform eagerly imports
subprocess even when only querying platform metadata. The runtime bootstrap
now recognizes registered renpy/pygame_sdl2 submodules and identifies Switch
explicitly. The platform module loads subprocess only when needed and returns
aarch64 directly for Switch processor queries. Process spawning remains
unsupported.

## Confirmed hardware checkpoint

On 2026-09-26, build **36263659522**, commit **e73db99**, returned:

```text
registered=1 initialized=1 native=1 pygame=1 renpy=1
error:
```

The Python smoke probe also reported initialization success and
`stdlib checks: PASS`. The engine import log contained no traceback.
This confirms Python startup and imports of `_renpy`, `pygame_sdl2` and `renpy`
on the user's Switch. It does not yet validate SDL display initialization,
Ren'Py's full module initialization, game execution, controls, saves or media.
The next integration step is a game bootstrap using the staged Agent17 assets.

## Experimental game launcher

`agent17.nro` attempts the upstream Ren'Py bootstrap with game files at
`sdmc:/switch/agent17/game`. Engine common resources are embedded in RomFS.
Saves and logs use the separate `switch/agent17/saves` and `logs` directories.
`boot-errors.txt` captures Python output; `boot-stage.txt` identifies the last
startup stage. A failed startup displays a message and waits for A.

The runtime includes ecdsa 0.19.1 and six 1.17.0 for Ren'Py save signatures,
plus Ren'Py's test package required by import_all. Device-prefixed paths are
treated as absolute. Desktop editor/TTS/relaunch integrations report ENOSYS
when asked to spawn a process. The launcher requests the GLES2 renderer.
This is the first full game startup attempt; gameplay, input, save/load and
multimedia are not yet validated. Game assets are never included in CI.

### First game startup result

Build 36265211436 reached the full engine import and then failed in
`renpy.Backup`: the distributor launcher was named `renpy_launcher` and its
locally defined path callbacks could not be pickled. It is now named
`switch_launcher`, outside Ren'Py's module backup prefix, and all callbacks
and progress hooks are module-level functions. A host check using the actual
Ren'Py Backup class confirms callback serialization works even when included
in a module with the renpy prefix. The native stdlib also gains BLAKE2 and
SHA-3/SHAKE, missing from the first game's hashlib import. Hardware retest
is still required; this failure happened before game script initialization.

The following hardware run passed Backup and stopped in post_import's legacy
renpy.subprocess alias. That alias now uses the same explicit unsupported-process
adapter as the desktop integrations. DBI MTP access from the development Mac
successfully retrieved the boot logs over USB. Python-only packaging fixes can
reuse the previously built ELF with elf2nro; embedded files are verified again
before transfer, and USB transfers are downloaded back for SHA-256 comparison.
