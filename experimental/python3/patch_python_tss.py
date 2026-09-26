"""Keep CPython callback state outside the failing Switch pthread TLS slots."""
from pathlib import Path
import sys

root = Path(sys.argv[1])
path = root / 'Python/thread_pthread.h'
source = path.read_text()
needle = 'int\nPyThread_tss_create(Py_tss_t *key)'
assert source.count(needle) == 1
start = source.index(needle)
# The four TSS functions form the final section of CPython 3.9.21's header.
assert source[start:].rstrip().endswith('return pthread_getspecific(key->_key);\n}')
path.write_text(source[:start] + '#ifdef __SWITCH__\n#include "switch_tss.h"\n#else\n' + source[start:] + '\n#endif\n')
(root / 'Python/switch_tss.h').write_text(Path(__file__).with_name('switch_tss.h').read_text())
