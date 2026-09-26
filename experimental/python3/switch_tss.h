/* CPython TSS without libnx's shared pthread TLS slots.
 * Native callback threads must recover the exact PyThreadState pointer.
 */
#include <stdlib.h>

typedef struct switch_tss_entry {
    Py_tss_t *key;
    pthread_t thread;
    void *value;
    struct switch_tss_entry *next;
} switch_tss_entry;

static pthread_mutex_t switch_tss_mutex = PTHREAD_MUTEX_INITIALIZER;
static switch_tss_entry *switch_tss_entries;

int PyThread_tss_create(Py_tss_t *key)
{
    key->_is_initialized = 1;
    return 0;
}

void PyThread_tss_delete(Py_tss_t *key)
{
    pthread_mutex_lock(&switch_tss_mutex);
    switch_tss_entry **link = &switch_tss_entries;
    while (*link) {
        switch_tss_entry *entry = *link;
        if (entry->key == key) {
            *link = entry->next;
            free(entry);
        } else {
            link = &entry->next;
        }
    }
    key->_is_initialized = 0;
    pthread_mutex_unlock(&switch_tss_mutex);
}

int PyThread_tss_set(Py_tss_t *key, void *value)
{
    if (!key->_is_initialized)
        return -1;
    pthread_t thread = pthread_self();
    pthread_mutex_lock(&switch_tss_mutex);
    switch_tss_entry **link = &switch_tss_entries;
    while (*link) {
        switch_tss_entry *entry = *link;
        if (entry->key == key && pthread_equal(entry->thread, thread)) {
            if (value) {
                entry->value = value;
            } else {
                *link = entry->next;
                free(entry);
            }
            pthread_mutex_unlock(&switch_tss_mutex);
            return 0;
        }
        link = &entry->next;
    }
    if (value) {
        switch_tss_entry *entry = malloc(sizeof(*entry));
        if (!entry) {
            pthread_mutex_unlock(&switch_tss_mutex);
            return -1;
        }
        *entry = (switch_tss_entry){key, thread, value, switch_tss_entries};
        switch_tss_entries = entry;
    }
    pthread_mutex_unlock(&switch_tss_mutex);
    return 0;
}

void *PyThread_tss_get(Py_tss_t *key)
{
    void *value = NULL;
    pthread_t thread = pthread_self();
    pthread_mutex_lock(&switch_tss_mutex);
    for (switch_tss_entry *entry = switch_tss_entries; entry; entry = entry->next) {
        if (entry->key == key && pthread_equal(entry->thread, thread)) {
            value = entry->value;
            break;
        }
    }
    pthread_mutex_unlock(&switch_tss_mutex);
    return value;
}
