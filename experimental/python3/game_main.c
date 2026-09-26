/* Experimental game bootstrap. Game data stays on SD, outside the repo. */
#include <Python.h>
#include <switch.h>
#include <SDL.h>
#include <stdio.h>
#include <sys/stat.h>
#include "init_python.h"
#include "probe_io.h"

int register_renpy8_static_modules(void);

int main(void)
{
    mkdir("sdmc:/switch/agent17", 0777);
    if (freopen("sdmc:/switch/agent17/boot-errors.txt", "w", stderr))
        setvbuf(stderr, NULL, _IONBF, 0);
    Result rc = romfsInit();
    fprintf(stderr, "Agent17 game bootstrap; romfs=0x%08x\n", (unsigned int)rc);
    char error[256] = {0};
    int initialized = 0, ok = 0;
    if (R_SUCCEEDED(rc) && register_renpy8_static_modules() == 0) {
        initialized = switch_python_initialize(L"romfs:/Contents/python39.zip",
            L"romfs:/Contents/renpy8.zip", error, sizeof error);
        if (initialized)
            ok = PyRun_SimpleString("import game_entry; game_entry.run()") == 0;
    }
    SDL_Quit();
    if (!ok && !error[0])
        snprintf(error, sizeof error, "Read switch/agent17/boot-errors.txt on the SD.");
    probe_show_result("Game bootstrap", ok, error);
    /* The OS reclaims Python after exit. Engine threads must not access a
       partially finalized interpreter if startup failed halfway through. */
    romfsExit();
    return ok ? 0 : 1;
}
