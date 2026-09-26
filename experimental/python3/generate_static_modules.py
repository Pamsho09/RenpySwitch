"""Generate the Python 3 built-in module table from static Cython sources."""

import argparse
from pathlib import Path


def entries(directory, prefix):
    paths = sorted(Path(directory).glob("*.c"))
    if not paths:
        raise ValueError(f"No generated C sources in {directory}")
    result = []
    for path in paths:
        module = path.stem
        if prefix and not module.startswith(prefix + "."):
            raise ValueError(f"Unexpected module name: {module}")
        symbol = module.removeprefix(prefix + ".") if prefix else module.replace(".", "_")
        result.append((module, "PyInit_" + symbol))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pygame_sources", type=Path)
    parser.add_argument("renpy_sources", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    modules = entries(args.pygame_sources, "pygame_sdl2")
    modules += entries(args.renpy_sources, "")
    if len(modules) < 60:
        raise ValueError(f"Expected at least 60 modules; found {len(modules)}")
    lines = [
        "/* Generated from the Cython static module sources. */",
        "#include <Python.h>",
        "",
    ]
    for _, symbol in modules:
        lines.append(f"PyMODINIT_FUNC {symbol}(void);")
    lines += ["", "int register_renpy8_static_modules(void)", "{"]
    for name, symbol in modules:
        lines.append(f'    if (PyImport_AppendInittab("{name}", {symbol}) != 0) return -1;')
    lines += ["    return 0;", "}", ""]
    args.output.write_text("\n".join(lines))
    print(f"Generated {len(modules)} static module registrations in {args.output}")


if __name__ == "__main__":
    main()
