/* Filesystem diagnostics for the experimental Switch bootstrap only. */
#pragma once
#include <switch.h>
#include <stdio.h>
#include <errno.h>
#include <sys/stat.h>

static void probe_file(const char *path)
{
    struct stat st;
    errno = 0;
    int rc = stat(path, &st);
    fprintf(stderr, "stat %s: rc=%d errno=%d", path, rc, errno);
    if (rc == 0) {
        fprintf(stderr, " mode=%lo size=%lld", (unsigned long)st.st_mode,
                (long long)st.st_size);
    }
    fprintf(stderr, "\n");
    errno = 0;
    FILE *file = fopen(path, "rb");
    if (!file) {
        fprintf(stderr, "open failed: errno=%d\n", errno);
        return;
    }
    unsigned char signature[4] = {0};
    size_t count = fread(signature, 1, sizeof signature, file);
    fprintf(stderr, "ZIP header bytes=%zu: %02x %02x %02x %02x\n",
            count, signature[0], signature[1], signature[2], signature[3]);
    rc = fseek(file, -22, SEEK_END);
    fprintf(stderr, "ZIP end seek: rc=%d errno=%d\n", rc, errno);
    fclose(file);
}

static void probe_show_result(const char *name, int ok, const char *error)
{
    consoleInit(NULL);
    printf("Agent17 - %s\n\nResult: %s\n%s\n\n"
           "Diagnostic logs are saved on the SD.\n"
           "\nPress A to return to hbmenu.\n", name, ok ? "PASS" : "FAIL", error);
    padConfigureInput(1, HidNpadStyleSet_NpadStandard);
    PadState pad;
    padInitializeDefault(&pad);
    while (appletMainLoop()) {
        padUpdate(&pad);
        if (padGetButtonsDown(&pad) & HidNpadButton_A) break;
        consoleUpdate(NULL);
    }
    consoleExit(NULL);
}
