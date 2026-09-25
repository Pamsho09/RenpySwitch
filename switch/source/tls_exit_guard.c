/* Hardware experiment: ignore unmapped pthread TLS values at thread exit.
 *
 * The video decoder crashes in libnx threadExit when it calls the C++
 * exception-state destructor with an unmapped value. Preserve normal TLS
 * cleanup and clear only values that cannot point to readable memory.
 */

#include <switch.h>
#include <stdio.h>
#include <stdint.h>

void __real_threadExit(void);

void __wrap_threadExit(void)
{
    /* The pinned libnx 4.4.2 binary iterates 27 user TLS slots in threadExit.
     * ThreadVars is an internal type, so use the verified count here. */
    enum { TLS_SLOT_COUNT = 27 };

    for (int slot = 0; slot < TLS_SLOT_COUNT; ++slot) {
        void *value = threadTlsGet(slot);
        if (!value)
            continue;

        MemoryInfo info = {0};
        u32 page_info = 0;
        Result rc = svcQueryMemory(&info, &page_info, (u64)(uintptr_t)value);
        if (R_FAILED(rc) || info.type == MemType_Unmapped || !(info.perm & Perm_R)) {
            threadTlsSet(slot, NULL);
            FILE *log = fopen("sdmc:/renpy-switch-tls-diagnostic.txt", "a");
            if (log) {
                fprintf(log, "threadExit cleared unmapped TLS slot %d value %p result 0x%x\n",
                    slot, value, rc);
                fclose(log);
            }
        }
    }

    __real_threadExit();
}
