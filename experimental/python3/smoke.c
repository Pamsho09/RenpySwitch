#include <Python.h>
#include <switch.h>

int main(void)
{
    romfsInit();
    Py_InitializeEx(0);
    if (Py_IsInitialized()) {
        PyRun_SimpleString("switch_python = 1 + 1");
        Py_FinalizeEx();
    }
    romfsExit();
    return 0;
}
