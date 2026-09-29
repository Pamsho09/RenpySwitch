# RenPy 7: technical history

Current integration status: [overview](../SWITCH_PORT_PROGRESS.md).
These notes describe the reusable Ren’Py 7.6.3 Switch runtime.

## Runtime changes

- `switch_fixes.patch` stops engine log writes after an I/O failure, grows the
  Switch save area before writing it, and updates `InputValue` fields with the
  complete text returned by the Switch keyboard.
- `switch_loading.patch` displays a fallback startup image and an indeterminate
  activity bar when no presplash image is available.
- `switch_urm.patch` provides a conditional L + R + X shortcut for an optional
  extension and bypasses its automatic network update check. The extension
  is supplied separately.
- `renpy.patch` maps either ZL or ZR to Ren’Py’s `toggle_skip` action.
  Choice and menu selection bindings remain on the normal face button.
- `switch/source/sdl_tls.c` routes SDL TLS through its generic implementation.
- `switch/source/tls_exit_guard.c` clears TLS slots that point to unreadable
  memory before libnx runs thread destructors. Historical hardware crashes
  showed that this scan alone is insufficient. The follow-up C++ guard checks
  the pointer at the destructor callback itself and performs no file I/O
  during thread exit. General TLS stability remains unresolved.
- `switch_fixes.patch` enables late-frame dropping for movie channels.
- Decoder workers are limited to two for video and one for audio.

## Validation and limitations

Patch application and the full Docker Compose build passed on native
x86-64 Linux. The artifact contains the Switch executable, patched runtime
archive, compiled common scripts, loading image and compressed ELF symbols.

The software-keyboard `InputValue` change was checked on hardware. Audio and
video tests exposed native faults in the C++ exception TLS destructor called
by libnx `threadExit`. These results do not establish general codec or runtime
stability. Optional extension behavior also requires hardware validation.

Python errors before the Ren’Py exception handler write stderr to
`sdmc:/renpy-switch-python-error.txt` and show the captured traceback on the
console error screen. Hardware validation remains pending.

An Apple Silicon build under `linux/amd64` emulation applied the patches but
the emulated cross compiler segfaulted while building a module. Use native
x86-64 Linux for reliable builds.
