"""Launch the staged game using upstream Ren'Py bootstrap callbacks."""
import sys
import os
import traceback
import shutil
import switch_bootstrap

BASE = "sdmc:/switch/agent17"
COMMON = BASE + "/engine-common-8.3.7"


def stage(message):
    print(message, file=sys.stderr, flush=True)
    with open(BASE + "/boot-stage.txt", "w") as out:
        out.write(message + "\n")


def prepare_common(source="romfs:/Contents/common", destination=COMMON):
    marker = os.path.join(destination, ".ready")
    if os.path.isfile(marker) and os.path.isfile(os.path.join(destination, "_errorhandling.rpym")):
        return
    stage("Preparing engine script cache on SD")
    for directory, _, files in os.walk(source):
        target = os.path.join(destination, os.path.relpath(directory, source))
        os.makedirs(target, exist_ok=True)
        for filename in files:
            shutil.copyfile(os.path.join(directory, filename), os.path.join(target, filename))
    if not os.path.isfile(os.path.join(destination, "_errorhandling.rpym")):
        raise RuntimeError("Engine common resources could not be copied to SD")
    with open(marker, "w") as out:
        out.write("RenPy 8.3.7 common resources\n")


def path_to_renpy_base():
    return BASE


def path_to_gamedir(basedir, name):
    return BASE + "/game"


def path_to_common(basedir):
    return COMMON


def path_to_saves(gamedir, save_directory=None):
    return BASE + "/saves"


def path_to_logdir(basedir):
    return BASE + "/logs"


_original_import_all = None
_original_main = None


def engine_import_all():
    global _original_main
    import renpy
    stage("Importing full RenPy engine")
    _original_import_all()
    stage("Engine modules loaded; preparing game initialization")
    _original_main = renpy.main.main
    renpy.main.main = game_main


def game_main():
    import renpy
    import switch_profile
    if switch_profile.apply not in renpy.game.post_init:
        renpy.game.post_init.append(switch_profile.apply)
    stage("Initializing game scripts and display")
    return _original_main()


def run():
    global _original_import_all
    switch_bootstrap.install()
    sys.stdout = sys.stderr
    os.makedirs(BASE + "/logs", exist_ok=True)
    os.makedirs(BASE + "/saves", exist_ok=True)
    os.chdir(BASE)
    os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
    os.environ["RENPY_RENDERER"] = "gles2"
    os.environ["RENPY_PLATFORM"] = "switch-aarch64"
    os.environ["RENPY_LOG_TO"] = BASE + "/logs"
    sys.argv = [BASE + "/Agent17.py", BASE]
    stage("Checking game files")
    if not os.path.isfile(BASE + "/game/archive.rpa"):
        raise FileNotFoundError(BASE + "/game/archive.rpa")
    prepare_common()
    import switch_launcher as launcher
    launcher.path_to_renpy_base = path_to_renpy_base
    launcher.path_to_gamedir = path_to_gamedir
    launcher.path_to_common = path_to_common
    launcher.path_to_saves = path_to_saves
    launcher.path_to_logdir = path_to_logdir
    import renpy
    _original_import_all = renpy.import_all
    renpy.import_all = engine_import_all
    stage("Starting RenPy bootstrap")
    try:
        launcher.main()
    except SystemExit as exc:
        if exc.code not in (None, 0):
            raise RuntimeError("RenPy exited with status %r" % (exc.code,)) from exc
        stage("RenPy exited normally")
    except BaseException:
        stage("RenPy bootstrap failed; see boot-errors.txt")
        traceback.print_exc()
        raise
