#include <Python.h>
#include <switch.h>
#include <stdio.h>

int main(void)
{
    romfsInit();
    Py_NoSiteFlag = 1;
    Py_DontWriteBytecodeFlag = 1;
    Py_SetPath(L"romfs:/Contents/python39.zip");
    Py_InitializeEx(0);
    int ok = 0;
    if (Py_IsInitialized()) {
        ok = (PyRun_SimpleString("switch_python = 1 + 1\nassert switch_python == 2") == 0);
        Py_FinalizeEx();
    }
    FILE *result = fopen("sdmc:/renpy8-python-smoke.txt", "w");
    if (result) {
        fprintf(result, "CPython 3.9 initialized: %s\n", ok ? "yes" : "no");
        fclose(result);
    }
    romfsExit();
    return ok ? 0 : 1;
}
