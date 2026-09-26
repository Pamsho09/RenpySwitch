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
            "assert 0 <= random.random() < 1\n"
            "import hashlib\n"
            "assert hashlib.blake2b(b'abc').hexdigest() == 'ba80a53f981c4d0d6a2797b69f12f6e94c212f14685ac4b74b12bb6fdbffa2d17d87c5392aab792dc252d5de4533cc9518d38aa8dbf1925ab92386edd4009923'\n"
            "assert hashlib.sha3_256(b'abc').hexdigest() == '3a985da74fe225b2045c172d6bd390bd855f086e3e9d525b46bfe24511431532'\n"
            "for name in hashlib.algorithms_guaranteed: hashlib.new(name, b'abc')\n") == 0);
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
