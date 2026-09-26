/* Initialize CPython with a literal RomFS path containing ':'. */
#pragma once

#include <Python.h>
#include <stdio.h>

static int switch_python_initialize(const wchar_t *stdlib_zip,
                                    const wchar_t *runtime_zip,
                                    char *error, size_t error_size)
{
    PyConfig config;
    PyConfig_InitIsolatedConfig(&config);
    config.verbose = 1;
    config.site_import = 0;
    config.write_bytecode = 0;
    config.module_search_paths_set = 1;

    PyStatus status = PyWideStringList_Append(&config.module_search_paths,
                                             stdlib_zip);
    if (!PyStatus_Exception(status) && runtime_zip) {
        status = PyWideStringList_Append(&config.module_search_paths,
                                         runtime_zip);
    }
    if (!PyStatus_Exception(status)) {
        status = Py_InitializeFromConfig(&config);
    }
    if (PyStatus_Exception(status) && error_size) {
        snprintf(error, error_size, "%s",
                 status.err_msg ? status.err_msg : "Python initialization failed");
    }
    if (PyStatus_Exception(status) && PyGILState_GetThisThreadState()) {
        /* Initialization errors retain an exception, but returning PyStatus
           alone hides it. Avoid traceback imports in the incomplete runtime. */
        PyObject *type = NULL, *value = NULL, *traceback = NULL;
        PyErr_Fetch(&type, &value, &traceback);
        if (type) {
            PyObject *type_text = PyObject_Str(type);
            PyObject *value_text = value ? PyObject_Str(value) : NULL;
            const char *type_utf8 = type_text ? PyUnicode_AsUTF8(type_text) : NULL;
            const char *value_utf8 = value_text ? PyUnicode_AsUTF8(value_text) : NULL;
            fprintf(stderr, "Initialization exception: %s: %s\n",
                    type_utf8 ? type_utf8 : "unknown",
                    value_utf8 ? value_utf8 : "no detail");
            Py_XDECREF(type_text);
            Py_XDECREF(value_text);
        }
        Py_XDECREF(type);
        Py_XDECREF(value);
        Py_XDECREF(traceback);
        PyErr_Clear();
    }
    PyConfig_Clear(&config);
    return !PyStatus_Exception(status) && Py_IsInitialized();
}
