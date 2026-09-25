/* libhydrogen entropy source for Nintendo Switch/libnx. */
#include <switch.h>

static int
hydro_random_init(void)
{
    uint8_t seed[gimli_BLOCKBYTES + 8];
    Result rc = csrngInitialize();
    if (R_FAILED(rc)) {
        return -1;
    }

    rc = csrngGetRandomBytes(seed, sizeof seed);
    csrngExit();
    if (R_FAILED(rc)) {
        hydro_memzero(seed, sizeof seed);
        return -1;
    }

    memcpy(hydro_random_context.state, seed, gimli_BLOCKBYTES);
    memcpy(&hydro_random_context.counter, seed + gimli_BLOCKBYTES, 8);
    hydro_memzero(seed, sizeof seed);
    return 0;
}
