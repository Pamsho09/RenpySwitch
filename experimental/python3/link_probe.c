/* First link and import probe for the native Ren'Py 8 module set. */
#include <Python.h>
#include <switch.h>
#include <stdio.h>
#include "init_python.h"
#include "probe_io.h"

int register_renpy8_static_modules(void);

int main(void)
{
    FILE *errors = freopen("sdmc:/renpy8-link-probe-errors.txt", "w", stderr);
    if (errors) {
        setvbuf(stderr, NULL, _IONBF, 0);
    }
    Result romfs_result = romfsInit();
    fprintf(stderr, "romfsInit: 0x%08x\n", (unsigned int)romfs_result);
    probe_file("romfs:/Contents/python39.zip");
    probe_file("romfs:/Contents/renpy8.zip");
    char error[256] = {0};

    int registered = register_renpy8_static_modules();
    int initialized = 0;
    int native_imported = 0;
    int pygame_imported = 0;
    int renpy_imported = 0;

    if (registered == 0) {
        initialized = switch_python_initialize(
            L"romfs:/Contents/python39.zip",
            L"romfs:/Contents/renpy8.zip", error, sizeof error);
        if (initialized) {
            native_imported = PyRun_SimpleString("import _renpy") == 0;
            pygame_imported = PyRun_SimpleString("import pygame_sdl2") == 0;
            renpy_imported = PyRun_SimpleString("import renpy") == 0;
        }
    }

    FILE *result = fopen("sdmc:/renpy8-link-probe.txt", "w");
    if (result) {
        fprintf(result,
                "registered=%d initialized=%d native=%d pygame=%d renpy=%d\nerror: %s\n",
                registered == 0, initialized, native_imported,
                pygame_imported, renpy_imported, error);
        fclose(result);
    }
    probe_show_result("RenPy imports",
                      native_imported && pygame_imported && renpy_imported, error);
    if (initialized) {
        Py_FinalizeEx();
    }
    romfsExit();
    return native_imported && pygame_imported && renpy_imported ? 0 : 1;
}
