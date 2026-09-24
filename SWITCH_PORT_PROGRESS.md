# Switch runtime porting notes

These observations come from testing a Ren'Py 7.4.11 game with the 7.6.3
Switch runtime. They describe runtime behavior, without bundling game files,
keys, crash dumps, or a packaged game.

## Confirmed observations

- The game reaches its main menu on Switch. Starting a new game crashes with
  Atmosphère result `2168-0002`, a Data Abort in the exit path of an SDL thread.
- A Python AST trace reaches a `stop music fadeout 1` statement immediately
  before that crash. An instrumented LayeredFS test that makes
  `renpy.audio.music.stop` a no-op advances past the statement and reaches the
  name input screen. The no-op affects every audio channel and is only a
  diagnostic experiment. The underlying SDL thread failure is unresolved.
- When the title's save filesystem was full, writing `save:/Logs/log.log`
  raised `IOError: [Errno 5] I/O error` during startup. `switch_fixes.patch`
  disables further writes to that engine log after this failure. Save files
  still need available space; this change does not repair a full save.
- The runtime's `Input.event` returns immediately on Switch `TEXTINPUT`. For
  an input linked to `InputValue`, the field's variable is therefore left
  unchanged. `switch_fixes.patch` updates the field from the complete text
  delivered by the Switch keyboard. A LayeredFS version of this change was
  tested on hardware: the trace recorded a value update and the script
  advanced beyond the name input screen. The patch inside a rebuilt runtime
  has not yet been tested.
- After the name prompt, the script reaches its initial warning screens and
  starts a sound effect. Another `2168-0002` Data Abort occurs in an SDL
  thread. The last trace is at the warning screen pause; this timing suggests
  the audio path, but does not establish the cause. A hardware A/B test that
  suppresses both `music.play` and `music.stop` advanced through the warnings
  and into the story without a crash. This diagnostic run is silent; audio
  remains unresolved and the bypass is not included in the runtime patch.

## Reproducing patch application

`setup.bash` applies `renpy.patch`, `switch_fixes.patch`,
`switch_loading.patch`, and `switch_urm.patch` to the Ren'Py 7.6.3 source
tree. Patch application was checked against the 7.6.3 source tree. A full
Switch build and hardware validation of the patched runtime remain pending.

The Docker Compose entry point reproduces the fork's runtime build without
host-specific devkitPro or Python 2 installs. It does not package a game.
An Apple Silicon run under `linux/amd64` emulation applied all patches, then
segfaulted in the emulated cross compiler at 28% of the Switch module build.
The full build succeeded on native x86-64 Linux in GitHub Actions run
`36048734192`; the artifact contains the executable, runtime archive,
compiled common scripts, and loading image. Hardware validation remains.

The Switch presplash previously returned without drawing anything when a game
did not include `presplash.png` or `presplash.jpg`. `switch_loading.patch` adds
a generic fallback image and an indeterminate activity bar driven by the
existing presplash pump calls. This is intended to replace the long black
screen during script loading. It needs testing on the rebuilt runtime.

The optional 0x52 Universal Ren'Py Mod has an `Alt+M` key on its overlay.
`switch_urm.patch` maps L + R + X to that key when the mod is present. It
does not ship the mod archive and does not depend on a particular game.
The combination has not yet been tested on Switch hardware.
With the mod archive temporarily added to a desktop validation project,
Ren'Py 7.6.3 loaded the mod's init code and reached interface start without
an exception. This checks initialization, not menu interaction or Switch
filesystem behavior.
