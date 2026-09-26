#include <Python.h>
#include <switch.h>
#include <stdio.h>
#include "init_python.h"
#include "probe_io.h"

int main(void)
{
    if (freopen("sdmc:/renpy8-python-smoke-errors.txt", "w", stderr)) {
        setvbuf(stderr, NULL, _IONBF, 0);
    }
    Result romfs_result = romfsInit();
    fprintf(stderr, "romfsInit: 0x%08x\n", (unsigned int)romfs_result);
    probe_file("romfs:/Contents/python39.zip");
    char error[256] = {0};
    int initialized = switch_python_initialize(
        L"romfs:/Contents/python39.zip", NULL, error, sizeof error);
    int ok = 0;
    if (initialized) {
        ok = (PyRun_SimpleString(
            "import zlib, math, struct, random, pickle, datetime, json, unicodedata, os\n"
            "assert zlib.decompress(zlib.compress(b'Switch')) == b'Switch'\n"
            "assert struct.unpack('<I', struct.pack('<I', 1234)) == (1234,)\n"
            "assert pickle.loads(pickle.dumps({'test': 42})) == {'test': 42}\n"
            "assert math.isqrt(144) == 12\n"
            "assert len(os.urandom(32)) == 32\n"
            "assert 0 <= random.random() < 1\n") == 0);
    }
    FILE *result = fopen("sdmc:/renpy8-python-smoke.txt", "w");
    if (result) {
        fprintf(result, "CPython 3.9 initialized: %s\nerror: %s\n",
                initialized ? "yes" : "no", error);
        fprintf(result, "stdlib checks: %s\n", ok ? "PASS" : "FAIL");
        fclose(result);
    }
    probe_show_result("Python 3", ok, error);
    if (initialized) {
        Py_FinalizeEx();
    }
    romfsExit();
    return ok ? 0 : 1;
}
