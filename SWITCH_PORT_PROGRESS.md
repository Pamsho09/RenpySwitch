# Switch runtime status

This document tracks the reusable Ren'Py 7.6.3 Switch runtime. It contains
no game files, console keys, packaged titles, or game-specific setup steps.

## Runtime changes

- `switch_fixes.patch` stops engine log writes after an I/O failure, grows the
  Switch save before writing it, and updates `InputValue` fields
  with the complete text returned by the Switch keyboard.
- `switch_loading.patch` displays a fallback startup image and an indeterminate
  activity bar when a game has no presplash image.
- `switch_urm.patch` maps L + R + X to the `Alt+M` shortcut of the optional
  0x52 Universal Ren'Py Mod. The mapping activates only when the mod loads.
  It also bypasses the mod's automatic update check on Switch, which starts
  a background thread during initialization. The mod archive is supplied
  separately by the game owner.

## Validation

- Patch application and the full Docker Compose build passed on native
  x86-64 Linux in [GitHub Actions run 36048734192](https://github.com/Pamsho09/RenpySwitch/actions/runs/36048734192).
  The artifact contains the Switch executable, patched runtime archive,
  compiled common scripts, and loading image.
- On hardware, a LayeredFS version of the `InputValue` change updated a field
  using the Switch software keyboard.
- On hardware, an SDL thread crash was observed when the audio path was used.
  A diagnostic test bypassing `renpy.audio.music.play` and `stop` continued
  without sound. The underlying audio failure is unresolved; the bypass is
  excluded from the runtime build.
- With `0x52_URM.rpa` in a desktop validation project, Ren'Py loaded the mod
  and reached the interface. An initial Switch trial with the archive stayed
  on the loading screen before the menu. The update-check bypass is a targeted
  diagnostic change and has not yet been tested on hardware. The L + R + X
  shortcut and other mod behavior also remain unverified on Switch. A later
  startup reached gameplay, though archive activation has not been confirmed.
- A save write failed after earlier diagnostics filled the title's save area.
  The save preflight patch is awaiting a hardware test. The build now retains
  a compressed ELF with symbols to identify native crashes such as the audio
  thread failure.
- Python errors before the Ren'Py exception handler now write stderr to
  `sdmc:/renpy-switch-python-error.txt` and show the captured traceback on
  the console error screen. This is awaiting a hardware test.
- An Apple Silicon build under `linux/amd64` emulation applied the patches but
  the emulated cross compiler segfaulted while building a module. Use native
  x86-64 Linux for reliable builds.

The Docker Compose build produces a reusable runtime. Packaging game data and
testing a finished title on Switch are separate steps.
