"""Keep platform importable without process spawning on Switch."""
from pathlib import Path
import sys

path = Path(sys.argv[1]) / "Lib/platform.py"
source = path.read_text()
needle = "import subprocess\n"
# Only remove the top-level eager import. Existing function-local imports stay.
assert source.count("\n" + needle) == 1
source = source.replace("\n" + needle, "\n", 1)
needle = "    def from_subprocess():\n"
assert source.count(needle) == 1
source = source.replace(needle, "    def get_switch():\n        return 'aarch64'\n\n" + needle)
needle = '        Fall back to `uname -p`\n        """\n'
assert source.count(needle) == 1
source = source.replace(needle, needle + '        import subprocess\n')
path.write_text(source)
