"""Route CPython entropy requests through libnx, including early hash init."""
from pathlib import Path
import sys

path = Path(sys.argv[1]) / "Python/bootstrap_hash.c"
source = path.read_text()
include = '#include "Python.h"\n'
assert source.count(include) == 1
source = source.replace(include, include + '#ifdef __SWITCH__\n#  include <switch.h>\n#endif\n')
needle = "#ifdef MS_WINDOWS\n    return win32_urandom((unsigned char *)buffer, size, raise);"
assert source.count(needle) == 1
source = source.replace(needle, """#if defined(__SWITCH__)
    Result rc = csrngInitialize();
    if (R_SUCCEEDED(rc)) {
        rc = csrngGetRandomBytes(buffer, (size_t)size);
        csrngExit();
    }
    if (R_FAILED(rc)) {
        /* Hash initialization runs before Python exceptions are available. */
        if (raise) {
            PyErr_Format(PyExc_OSError, "Switch csrng failed: 0x%08x",
                         (unsigned int)rc);
        }
        return -1;
    }
    return 0;
#elif defined(MS_WINDOWS)
    return win32_urandom((unsigned char *)buffer, size, raise);""")
path.write_text(source)
