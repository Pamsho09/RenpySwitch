#include <Python.h>
#include <switch.h>
#include <stdio.h>
#include "init_python.h"

int main(void)
{
    romfsInit();
    char error[256] = {0};
    int initialized = switch_python_initialize(
        L"romfs:/Contents/python39.zip", NULL, error, sizeof error);
    int ok = 0;
    if (initialized) {
        ok = (PyRun_SimpleString("switch_python = 1 + 1\nassert switch_python == 2") == 0);
    }
    FILE *result = fopen("sdmc:/renpy8-python-smoke.txt", "w");
    if (result) {
        fprintf(result, "CPython 3.9 initialized: %s\nerror: %s\n",
                ok ? "yes" : "no", error);
        fclose(result);
    }
    if (initialized) {
        Py_FinalizeEx();
    }
    romfsExit();
    return ok ? 0 : 1;
}
