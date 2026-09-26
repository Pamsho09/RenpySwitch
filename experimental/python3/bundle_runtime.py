"""Bundle pure Python Ren'Py dependencies for a Switch import probe."""

import argparse
import importlib.util
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def add_python_tree(archive, root, package):
    count = 0
    for path in sorted(root.rglob("*.py")):
        name = package / path.relative_to(root)
        if name.as_posix() in {"renpy/bootstrap.py", "renpy/editor.py", "renpy/display/tts.py"}:
            source = path.read_text()
            if source.count("\nimport subprocess\n") != 1:
                raise ValueError("Unexpected subprocess import: " + str(name))
            source = source.replace("\nimport subprocess\n", "\nimport switch_process as subprocess\n")
            archive.writestr(name.as_posix(), source)
        else:
            archive.write(path, name.as_posix())
        count += 1
    if not count:
        raise ValueError(f"No Python files in {root}")
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("renpy_package", type=Path)
    parser.add_argument("pygame_package", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with ZipFile(args.output, "w", ZIP_DEFLATED) as archive:
        for name in ("switch_bootstrap.py", "switch_process.py", "game_entry.py"):
            archive.write(Path(__file__).with_name(name), name)
            count += 1
        archive.write(args.renpy_package.parent / "renpy.py", "switch_launcher.py")
        count += 1
        count += add_python_tree(archive, args.renpy_package, Path("renpy"))
        count += add_python_tree(archive, args.pygame_package, Path("pygame_sdl2"))
        for package in ("future", "past", "ecdsa"):
            spec = importlib.util.find_spec(package)
            if spec is None or not spec.submodule_search_locations:
                raise ValueError(f"Required package not installed: {package}")
            root = Path(next(iter(spec.submodule_search_locations)))
            count += add_python_tree(archive, root, Path(package))
        spec = importlib.util.find_spec("six")
        if spec is None or spec.origin is None:
            raise ValueError("Required dependency missing: six")
        archive.write(spec.origin, "six.py")
        count += 1
    print(f"Bundled {count} Python files in {args.output}")


if __name__ == "__main__":
    main()
