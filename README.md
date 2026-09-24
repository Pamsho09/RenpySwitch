## Описание

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
the name prompt. A separate crash occurs
when `stop music fadeout 1` runs at the start of a game: temporarily bypassing
`renpy.audio.music.stop` allows execution to continue, but also prevents normal
audio stops. That diagnostic bypass is not included in this build. See
`SWITCH_PORT_PROGRESS.md` for the evidence and current limitations.

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
