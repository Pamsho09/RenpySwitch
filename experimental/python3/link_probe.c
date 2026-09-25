/* First link and import probe for the native Ren'Py 8 module set. */
#include <Python.h>
#include <switch.h>
#include <stdio.h>
#include "init_python.h"

int register_renpy8_static_modules(void);

int main(void)
{
    romfsInit();
    char error[256] = {0};

    int registered = register_renpy8_static_modules();
    int initialized = 0;
    int imported = 0;

    if (registered == 0) {
        initialized = switch_python_initialize(
            L"romfs:/Contents/python39.zip", error, sizeof error);
        if (initialized) {
            imported = PyRun_SimpleString("import _renpy") == 0;
            if (!imported) {
                PyErr_Print();
            }
            Py_FinalizeEx();
        }
    }

    FILE *result = fopen("sdmc:/renpy8-link-probe.txt", "w");
    if (result) {
        fprintf(result, "registered=%d initialized=%d imported=%d\nerror: %s\n",
                registered == 0, initialized, imported, error);
        fclose(result);
    }
    romfsExit();
    return imported ? 0 : 1;
}
