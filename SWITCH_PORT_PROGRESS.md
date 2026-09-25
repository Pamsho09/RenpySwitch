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
- `renpy.patch` maps either ZL or ZR to Ren'Py's `toggle_skip` action. The
  choice and menu selection bindings remain on the normal face button.
- `switch/source/sdl_tls.c` routes SDL TLS through its generic implementation.
  `switch/source/tls_exit_guard.c` clears TLS slots that point to unreadable
  memory before libnx runs thread destructors. A second video crash showed
  that this scan alone was insufficient, so the current experiment also
  clears the C++ exception-state slot at the final handoff. This can retain a
  small per-thread allocation until process exit. The guard performs no file
  I/O during thread exit.
- `switch_fixes.patch` enables late-frame dropping for Switch movie channels.
  This keeps the movie timeline moving when software decoding misses frames.

## Validation

- Patch application and the full Docker Compose build passed on native
  x86-64 Linux in [GitHub Actions run 36048734192](https://github.com/Pamsho09/RenpySwitch/actions/runs/36048734192).
  The artifact contains the Switch executable, patched runtime archive,
  compiled common scripts, and loading image.
- On hardware, a LayeredFS version of the `InputValue` change updated a field
  using the Switch software keyboard.
- On hardware, a diagnostic test bypassing `renpy.audio.music.play` and
  `stop` continued without sound. Later crash reports located the native fault
  in a C++ exception TLS destructor called by libnx `threadExit`. A trial with
  the current guard played music and both variants of a short looping video,
  then progressed through later scenes. A second WebM later triggered a
  restart in the same C++ TLS destructor. The final slot-clear change is
  awaiting hardware validation. The observed videos are VP9 at 1080p/60 fps;
  a separate game-side test is preparing VP8 720p/30 fps overrides. This is
  one hardware trial, not a general codec or stability certification.
- With `0x52_URM.rpa` in a desktop validation project, Ren'Py loaded the mod
  and reached the interface. An initial Switch trial with the archive stayed
  on the loading screen before the menu. The update-check bypass is a targeted
  diagnostic change and has not yet been tested on hardware. The L + R + X
  shortcut and other mod behavior also remain unverified on Switch. A later
  startup reached gameplay, and the console traceback reported the mod's
  version, confirming that the archive loaded on hardware.
- A save write in the title save area returned I/O error despite a successful
  preflight commit. A diagnostic overlay redirected saves to a per-title SD
  directory and produced valid save archives. In the latest hardware trial,
  the loader discovered both slots and gameplay resumed from a save. The SD
  override is still specific to that test and is not in this reusable runtime.
  The build retains a compressed ELF with symbols to identify native crashes.
- A diagnostic overlay initially transmitted every Ren'Py statement over UDP,
  which added work during scene changes. The next hardware overlay limits
  tracing to labels and selected events; this diagnostic tracer is not part
  of the reusable runtime.
- Python errors before the Ren'Py exception handler now write stderr to
  `sdmc:/renpy-switch-python-error.txt` and show the captured traceback on
  the console error screen. This is awaiting a hardware test.
- An Apple Silicon build under `linux/amd64` emulation applied the patches but
  the emulated cross compiler segfaulted while building a module. Use native
  x86-64 Linux for reliable builds.

The Docker Compose build produces a reusable runtime. Packaging game data and
testing a finished title on Switch are separate steps.
