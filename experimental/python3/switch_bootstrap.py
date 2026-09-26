"""Platform setup before importing statically linked Ren'Py packages."""
import sys
from importlib.machinery import BuiltinImporter


class SwitchBuiltinFinder:
    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        # Python 3.9's BuiltinImporter rejects package search paths. Our
        # dotted builtins are genuine registered modules, with normal loaders.
        if fullname.startswith(("pygame_sdl2.", "renpy.")):
            return BuiltinImporter.find_spec(fullname)
        return None


def install():
    sys.platform = "switch"
    if SwitchBuiltinFinder not in sys.meta_path:
        sys.meta_path.insert(0, SwitchBuiltinFinder)
