/* Switch experiment: use SDL's generic TLS instead of pthread TLS.
 *
 * Two hardware crash reports point to invalid per-thread pointers during
 * SDL_TLSCleanup. SDL 2.0.14 has a generic TLS implementation intended as a
 * fallback when platform TLS is unavailable. Linker wrapping redirects only
 * SDL's own platform TLS calls to that fallback.
 */

extern void *SDL_Generic_GetTLSData(void);
extern int SDL_Generic_SetTLSData(void *data);

void *__wrap_SDL_SYS_GetTLSData(void)
{
    return SDL_Generic_GetTLSData();
}

int __wrap_SDL_SYS_SetTLSData(void *data)
{
    return SDL_Generic_SetTLSData(data);
}
