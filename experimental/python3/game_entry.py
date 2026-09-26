"""Launch the staged game using upstream Ren'Py bootstrap callbacks."""
import sys
import os
import traceback
import switch_bootstrap

BASE = "sdmc:/switch/agent17"


def stage(message):
    print(message, file=sys.stderr, flush=True)
    with open(BASE + "/boot-stage.txt", "w") as out:
        out.write(message + "\n")


def run():
    switch_bootstrap.install()
    sys.stdout = sys.stderr
    os.makedirs(BASE + "/logs", exist_ok=True)
    os.makedirs(BASE + "/saves", exist_ok=True)
    os.chdir(BASE)
    os.environ["RENPY_RENDERER"] = "gles2"
    os.environ["RENPY_PLATFORM"] = "switch-aarch64"
    os.environ["RENPY_LOG_TO"] = BASE + "/logs"
    sys.argv = [BASE + "/Agent17.py", BASE]
    stage("Checking game files")
    if not os.path.isfile(BASE + "/game/archive.rpa"):
        raise FileNotFoundError(BASE + "/game/archive.rpa")
    import renpy_launcher as launcher
    launcher.path_to_renpy_base = lambda: BASE
    launcher.path_to_gamedir = lambda basedir, name: BASE + "/game"
    launcher.path_to_common = lambda basedir: "romfs:/Contents/common"
    launcher.path_to_saves = lambda gamedir, save_directory=None: BASE + "/saves"
    launcher.path_to_logdir = lambda basedir: BASE + "/logs"
    import renpy
    original_import_all = renpy.import_all

    def import_all():
        stage("Importing full RenPy engine")
        original_import_all()
        stage("Engine modules loaded; preparing game initialization")
        original_main = renpy.main.main

        def game_main():
            stage("Initializing game scripts and display")
            return original_main()

        renpy.main.main = game_main

    renpy.import_all = import_all
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
