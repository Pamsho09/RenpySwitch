# Switch runtime status

This document tracks the reusable Ren'Py 7.6.3 Switch runtime. It contains
no game files, console keys, packaged titles, or game-specific setup steps.

## Runtime changes

- `switch_fixes.patch` stops engine log writes after an I/O failure and updates
  `InputValue` fields with the complete text returned by the Switch keyboard.
- `switch_loading.patch` displays a fallback startup image and an indeterminate
  activity bar when a game has no presplash image.
- `switch_urm.patch` maps L + R + X to the `Alt+M` shortcut of the optional
  0x52 Universal Ren'Py Mod. The mapping activates only when the mod loads.
  The mod archive is supplied separately by the game owner.

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
  and reached the interface. The L + R + X shortcut and mod behavior on
  Switch still need hardware validation.
- An Apple Silicon build under `linux/amd64` emulation applied the patches but
  the emulated cross compiler segfaulted while building a module. Use native
  x86-64 Linux for reliable builds.

The Docker Compose build produces a reusable runtime. Packaging game data and
testing a finished title on Switch are separate steps.
