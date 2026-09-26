"""Importable subprocess adapter; Switch cannot spawn external processes."""
import errno

PIPE = -1
STDOUT = -2
DEVNULL = -3


class SubprocessError(Exception):
    pass


class CalledProcessError(SubprocessError):
    def __init__(self, returncode, cmd, output=None, stderr=None):
        super().__init__("Command %r exited with status %s" % (cmd, returncode))
        self.returncode, self.cmd = returncode, cmd
        self.output, self.stderr = output, stderr

    @property
    def stdout(self):
        return self.output


class TimeoutExpired(SubprocessError):
    def __init__(self, cmd, timeout, output=None, stderr=None):
        super().__init__("Command %r timed out after %s seconds" % (cmd, timeout))
        self.cmd, self.timeout = cmd, timeout
        self.output, self.stderr = output, stderr

    @property
    def stdout(self):
        return self.output


def _unsupported(*args, **kwargs):
    raise OSError(errno.ENOSYS, "External processes are unavailable on Switch")


class Popen:
    def __init__(self, *args, **kwargs):
        _unsupported()


call = check_call = check_output = run = getoutput = getstatusoutput = _unsupported
