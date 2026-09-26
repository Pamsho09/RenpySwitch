"""Explicit unsupported process API for Ren'Py desktop integrations on Switch."""
import errno


class Popen:
    def __init__(self, *args, **kwargs):
        raise OSError(errno.ENOSYS, "External processes are unavailable on Switch")


def call(*args, **kwargs):
    return Popen(*args, **kwargs).wait()
