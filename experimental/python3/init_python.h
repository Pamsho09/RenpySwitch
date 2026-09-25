/* Initialize CPython with a literal RomFS path containing ':'. */
#pragma once

#include <Python.h>
#include <stdio.h>

static int switch_python_initialize(const wchar_t *stdlib_zip,
                                    char *error, size_t error_size)
{
    PyConfig config;
    PyConfig_InitIsolatedConfig(&config);
    config.site_import = 0;
    config.write_bytecode = 0;
    config.module_search_paths_set = 1;

    PyStatus status = PyWideStringList_Append(&config.module_search_paths,
                                             stdlib_zip);
    if (!PyStatus_Exception(status)) {
        status = Py_InitializeFromConfig(&config);
    }
    if (PyStatus_Exception(status) && error_size) {
        snprintf(error, error_size, "%s",
                 status.err_msg ? status.err_msg : "Python initialization failed");
    }
    PyConfig_Clear(&config);
    return !PyStatus_Exception(status) && Py_IsInitialized();
}
