# Ren’Py 8 native bootstrap

Current integration status: [SWITCH_PORT_PROGRESS.md](../../SWITCH_PORT_PROGRESS.md).
Build from main with `RUNTIME=renpy8` (the default).

## Native dependencies

The bootstrap builds CPython 3.9.21, pygame_sdl2 and Ren’Py 8.3.7. Source
archives from the official releases are checked with SHA-256 before compilation.
All 66 native modules (23 pygame_sdl2 and 43 Ren’Py) register and link in an
ARM64 executable. SDL’s frame allocation path is used in ffmedia.

The static Python archive explicitly includes portable stdlib extensions in
`Setup.local`, including zlib, BLAKE2 and SHA-3/SHAKE. CPython and libhydrogen
use libnx `csrng` for entropy; service failures propagate instead of falling
back to `/dev/urandom`.

## Diagnostic probes

- `smoke.nro` checks Python initialization, compression, serialization, math
  and randomness. It writes `sdmc:/renpy8-python-smoke.txt` and
  `sdmc:/renpy8-python-smoke-errors.txt`.
- `link-probe.nro` checks imports of `_renpy`, `pygame_sdl2` and `renpy`.
  It writes `sdmc:/renpy8-link-probe.txt` and
  `sdmc:/renpy8-link-probe-errors.txt`.

Both probes passed their basic hardware checks. They record RomFS mount
status and show PASS/FAIL, then wait for A before returning to hbmenu.
They do not establish full engine, controls, save/load or media stability.

Both NACP and RomFS are supplied to elf2nro so that assets are embedded.
`verify_nro.py` fails the build unless embedded files match inputs by SHA-256.
PyConfig’s explicit path list preserves the colon in device-prefixed paths.

## Runtime adapters and launcher

`switch_bootstrap.py` recognizes registered dotted native modules and installs
an explicit ENOSYS subprocess adapter. Platform queries identify Switch and
return `aarch64` without spawning a process.

The C launcher mounts RomFS, initializes Python and starts `game_entry.py`.
Installation paths are defined in `game_entry.py` and `game_main.c`; output
names and NACP metadata are defined in `bootstrap.sh`. Common engine resources
are embedded in RomFS, then copied to the versioned writable SD directory
`engine-common-8.3.7` so compiled script caches can be reused.
Saves and logs have separate directories. `boot-errors.txt` captures Python
output and `boot-stage.txt` identifies the last startup stage.

The runtime includes ecdsa 0.19.1 and six 1.17.0 for save signatures, plus
Ren’Py’s test package required by `import_all`. Device-prefixed paths are
absolute, including when joined after a base path. Desktop editor, TTS and
relaunch integrations report ENOSYS for unsupported external processes.
The launcher requests the GLES2 renderer.

`switch_launcher` lives outside Ren’Py’s module backup prefix. Path callbacks
and progress hooks are module-level functions so they can be serialized.
The save-path callback is also exposed through `__main__` for optional extensions.
External resources are supplied separately and are not bundled in CI.

## Thread state and input

The native build wraps `pthread_key_create` to guard a specific C++
exception-state destructor. It skips unmapped or unreadable values while
preserving normal destructor calls. The pinned libstdc++ callback offset must
be verified in the ELF if the toolchain changes. This is a mitigation; the
underlying TLS corruption remains unresolved.

CPython TSS uses a mutex-protected map keyed by TSS key address and pthread
identity, independent of pthread TLS slots. NULL assignments and key deletion
free entries. Host stress checks cover independent keys across eight threads,
10,000 set/get iterations per thread, deletion and recreation.

SDL uses generic TLS storage. `SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS` is set
before initialization, controller events do not require desktop keyboard focus,
and joystick/controller events are enabled explicitly. Diagnostic logging
is limited to avoid excessive work during input processing.

## Display, controls and media

The post-init Lite profile requests 1280×720 and 30 FPS. Holding ZL or ZR
emits skip; releasing the final held trigger stops skipping. L+R+physical X
emits Alt+M only when an optional extension is present; otherwise it shows
an availability message. The extension is supplied separately.

Video-size metadata preserves the original virtual size of Movie objects
without overriding explicit sizes. Late-frame dropping keeps the media
timeline moving when decoding misses frames. Slow image loads are sampled
for diagnosis. These changes require visual and performance checks on hardware.

Normal exit returns directly to hbmenu. After SDL video initialization,
failures are recorded in the log rather than reopening the diagnostic console.
