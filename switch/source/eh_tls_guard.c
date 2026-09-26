/* Guard the libstdc++ exception-state TLS destructor at the callback boundary.
 *
 * In the pinned static libstdc++ build, eh_globals_dtor is 0x50 bytes before
 * __cxa_get_globals. The callback is installed by pthread_key_create during
 * startup. Checking at invocation is necessary: the TLS value can become
 * invalid after a scan at threadExit entry.
 */

#include <pthread.h>
#include <stdint.h>
#include <switch.h>

extern void *__cxa_get_globals(void);
int __real_pthread_key_create(pthread_key_t *key, void (*destructor)(void *));

static void (*original_eh_destructor)(void *);

static void safe_eh_destructor(void *value)
{
    if (!value || !original_eh_destructor)
        return;

    MemoryInfo info = {0};
    u32 page_info = 0;
    Result rc = svcQueryMemory(&info, &page_info, (u64)(uintptr_t)value);
    if (R_FAILED(rc) || info.type == MemType_Unmapped || !(info.perm & Perm_R))
        return;

    original_eh_destructor(value);
}

int __wrap_pthread_key_create(pthread_key_t *key, void (*destructor)(void *))
{
    if (destructor &&
        (uintptr_t)destructor + 0x50 == (uintptr_t)&__cxa_get_globals) {
        original_eh_destructor = destructor;
        destructor = safe_eh_destructor;
    }

    return __real_pthread_key_create(key, destructor);
}
