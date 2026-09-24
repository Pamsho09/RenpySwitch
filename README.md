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

`switch_fixes.patch` is applied after `renpy.patch` during setup. It contains two
small runtime fixes found while testing a Ren'Py 7.6.3 game on Switch:

- Stop writing engine logs after the title's save filesystem reports an I/O
  error, instead of terminating the game during startup.
- Copy the complete text returned by the Switch software keyboard into an
  `InputValue` field. The existing Switch path returned the text without
  updating the field's variable.

The text input change was tested with a LayeredFS overlay on Switch: the
software keyboard updated an `InputValue` field and the script advanced past
the name prompt. A separate crash occurs when `stop music fadeout 1` runs at
the start of a game: temporarily bypassing `renpy.audio.music.stop` allows
execution to continue, but also prevents normal audio stops. That diagnostic
bypass is not included in this build. See `SWITCH_PORT_PROGRESS.md` for the
evidence and current limitations.

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
uses x86 tools. Set `OUTPUT_DIR` to write artifacts elsewhere or
`BUILD_PLATFORM` to override the target platform. Generated files and any
private game data are excluded from the Docker build context.

The build also places a generic loading image in
`artifacts/switch/romfs/Contents/loading.png`. During startup, the Switch
runtime shows this image and animates an activity bar while it loads scripts.
A game can override it with `game/presplash.png` or `game/presplash.jpg`.
The bar indicates activity, not a percentage of work completed.

This builds the reusable runtime. Packaging a particular game and testing it
on Switch are separate steps; no game assets or console keys are included.
GitHub Actions runs the same Compose command on Linux and uploads the runtime
tree as a build artifact.
