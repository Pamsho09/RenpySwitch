/* First link and import probe for the native Ren'Py 8 module set. */
#include <Python.h>
#include <switch.h>
#include <stdio.h>

PyMODINIT_FUNC PyInit__renpy(void);

int main(void)
{
    romfsInit();
    Py_NoSiteFlag = 1;
    Py_DontWriteBytecodeFlag = 1;
    Py_SetPath(L"romfs:/Contents/python39.zip");

    int registered = PyImport_AppendInittab("_renpy", PyInit__renpy);
    int initialized = 0;
    int imported = 0;

    if (registered == 0) {
        Py_InitializeEx(0);
        initialized = Py_IsInitialized();
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
        fprintf(result, "registered=%d initialized=%d imported=%d\n",
                registered == 0, initialized, imported);
        fclose(result);
    }
    romfsExit();
    return imported ? 0 : 1;
}
