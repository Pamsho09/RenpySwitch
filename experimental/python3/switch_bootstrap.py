"""Platform setup before importing statically linked Ren'Py packages."""
import sys
import os
import posixpath
import importlib._bootstrap_external as _external
from importlib.machinery import BuiltinImporter


class SwitchBuiltinFinder:
    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        # Python 3.9's BuiltinImporter rejects package search paths. Our
        # dotted builtins are genuine registered modules, with normal loaders.
        if fullname.startswith(("pygame_sdl2.", "renpy.")):
            return BuiltinImporter.find_spec(fullname)
        return None


_original_join = posixpath.join
_original_isabs = posixpath.isabs
_original_realpath = posixpath.realpath
_original_import_isabs = _external._path_isabs


def _device_absolute(path):
    path = os.fspath(path)
    prefixes = (b"sdmc:/", b"romfs:/") if isinstance(path, bytes) else ("sdmc:/", "romfs:/")
    return path.startswith(prefixes)


def _isabs(path):
    return _device_absolute(path) or _original_isabs(path)


def _join(path, *paths):
    parts = tuple(os.fspath(part) for part in (path,) + paths)
    # Keep the standard type checks, including mixed str/bytes rejection.
    result = _original_join(*parts)
    for index in range(len(parts) - 1, -1, -1):
        if _device_absolute(parts[index]):
            return _original_join(*parts[index:])
    return result


def _realpath(path, *args, **kwargs):
    if _device_absolute(path):
        return posixpath.normpath(path)
    return _original_realpath(path, *args, **kwargs)


def install():
    sys.platform = "switch"
    import switch_process
    sys.modules["subprocess"] = switch_process
    posixpath.join = _join
    posixpath.isabs = _isabs
    posixpath.realpath = _realpath
    _external._path_isabs = lambda path: _device_absolute(path) or _original_import_isabs(path)
    if SwitchBuiltinFinder not in sys.meta_path:
        sys.meta_path.insert(0, SwitchBuiltinFinder)
