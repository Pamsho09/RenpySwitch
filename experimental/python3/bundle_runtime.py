"""Bundle pure Python Ren'Py dependencies for a Switch import probe."""

import argparse
import importlib.util
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def add_python_tree(archive, root, package):
    count = 0
    for path in sorted(root.rglob("*.py")):
        if "test" in path.relative_to(root).parts:
            continue
        name = package / path.relative_to(root)
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
        count += add_python_tree(archive, args.renpy_package, Path("renpy"))
        count += add_python_tree(archive, args.pygame_package, Path("pygame_sdl2"))
        for package in ("future", "past"):
            spec = importlib.util.find_spec(package)
            if spec is None or not spec.submodule_search_locations:
                raise ValueError(f"Required package not installed: {package}")
            root = Path(next(iter(spec.submodule_search_locations)))
            count += add_python_tree(archive, root, Path(package))
    print(f"Bundled {count} Python files in {args.output}")


if __name__ == "__main__":
    main()
