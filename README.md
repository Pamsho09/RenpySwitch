## Описание

Данный репозиторий служит сборщиком RenPy на Github Actions

Загружает исходники RenPy

Применяет патчи к RenPy

Компилирует RenPy

Пакует RenPy в lib.zip

Компилирует исполняемый файл для NSwitch

Собирает пустой проект под Switch

## Используемые образы и пакеты

- ubuntu-24.04

- devkitpro/devkita64:20230910

- renpy sdk 7.6.3

- python 2.7

- pefile 2019.4.18

- cython 0.29.36

- setuptools 0.9.8

## Switch port fixes in progress

`switch_fixes.patch` is applied after `renpy.patch` during setup. It contains
two runtime fixes for Ren'Py 7.6.3 on Switch:

- Stop writing engine logs after the save filesystem reports an I/O
  error, instead of terminating the game during startup.
- Copy the complete text returned by the Switch software keyboard into an
  `InputValue` field. The existing Switch path returned the text without
  updating the field's variable.

The text input change was tested with a LayeredFS overlay on Switch: the
software keyboard updated an `InputValue` field. The native runtime includes
SDL TLS handling and clears invalid per-thread TLS values before a decoder
thread exits. One hardware trial played music and a short video, then continued
through later scenes. Longer playback and other games still need testing. See
`SWITCH_PORT_PROGRESS.md` for current validation status.

ZL and ZR each toggle Ren'Py dialogue skipping. The game's normal selection
button remains available for menus and choices.

## Optional 0x52 Universal Ren'Py Mod

The runtime accepts `0x52_URM.rpa` from any compatible Ren'Py game. Place a
copy of the mod archive in that game's `game/` directory before packaging it;
the mod itself is not part of this repository or the runtime artifact.

On Switch, hold **L + R** and press **X** to open the mod menu. This maps to
the mod's existing `Alt+M` shortcut and is active only when the mod loaded.
The runtime skips the mod's automatic update check on Switch because it starts
a background thread during initialization. The mod's other features are left
to its own code.
Games without the mod keep their usual controller mappings. The shortcut has
been checked against the mod's scripts and the Ren'Py controller event path;
the mod still needs a successful startup and menu test on Switch hardware.

## Build with Docker Compose

From a checkout of this branch, with Docker Engine and Docker Compose available:

```sh
docker compose run --build --rm build
```

Compose builds the pinned devkitPro image, runs `setup.bash` followed by
`build.bash` inside the container, and copies the resulting `raw/` tree to
`./artifacts/` on the host. In particular, `artifacts/switch/exefs/main` is
the Switch executable and `artifacts/switch/romfs/Contents/lib.zip` is the
patched Ren'Py runtime. Check the two files with:

```sh
cd artifacts && sha256sum -c SHA256SUMS
```

The build downloads Ren'Py, pygame_sdl2 and toolchain packages. It needs an
internet connection and enough disk space for the source tree and artifacts.
On ARM hosts, Compose defaults to `linux/amd64` emulation because this build
uses x86 tools. An Apple Silicon test applied all patches but the emulated
cross compiler segfaulted while compiling `pygame_sdl2.mixer.c`. The same
Compose build completed on the fork's native x86-64 GitHub Actions runner.
Use a native x86-64 Linux host for reliable builds. Set `OUTPUT_DIR`
to write artifacts elsewhere or `BUILD_PLATFORM` to override the target
platform. Generated files and any private game data are excluded from the
Docker build context.

The build also places a generic loading image in
`artifacts/switch/romfs/Contents/loading.png`. During startup, the Switch
runtime shows this image and animates an activity bar while it loads scripts.
A game can override it with `game/presplash.png` or `game/presplash.jpg`.
The bar indicates activity, not a percentage of work completed.

This builds the reusable runtime. Packaging a particular game and testing it
on Switch are separate steps; no game assets or console keys are included.
The included GitHub Actions workflow uses the same Compose command on Linux
and uploads the runtime tree as a build artifact. Enable Actions on a fork to
run the workflow on branch pushes. GitHub requires the workflow file on the
default branch for manual dispatch.
