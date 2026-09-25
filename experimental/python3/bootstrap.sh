#!/usr/bin/env bash
set -euo pipefail

# First native Ren'Py 8 prerequisite: a CPython 3.9 static library for libnx.
# Keep this isolated from the working Ren'Py 7 build until it links and runs.
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y build-essential curl ca-certificates xz-utils

version=3.9.21
archive="Python-${version}.tar.xz"
curl -fL --retry 3 "https://www.python.org/ftp/python/${version}/${archive}" -o "/tmp/${archive}"
mkdir -p /tmp/python3-switch
tar -xf "/tmp/${archive}" -C /tmp/python3-switch
cd "/tmp/python3-switch/Python-${version}"

# CPython 3.9's configure only names Linux, Cygwin, and VxWorks as cross
# targets. libnx exposes enough POSIX interfaces to use the Linux probes as
# a starting point; missing calls will be disabled or shimmed explicitly.
python3 - <<'PY'
from pathlib import Path
path = Path('configure')
data = path.read_text()
needle = '\t*-*-linux*)\n\t\tac_sys_system=Linux\n'
assert data.count(needle) == 1
data = data.replace(needle, '\t*-*-elf*)\n\t\tac_sys_system=Linux\n\t\t;;\n' + needle)
needle = '\t*-*-linux*)\n\t\tcase "$host_cpu" in\n'
assert data.count(needle) == 1
data = data.replace(needle, '\t*-*-elf*)\n\t\t_host_cpu=$host_cpu\n\t\t;;\n' + needle)
path.write_text(data)
PY

export DEVKITPRO=/opt/devkitpro
export PATH="${DEVKITPRO}/devkitA64/bin:${PATH}"
export CC=aarch64-none-elf-gcc
export CXX=aarch64-none-elf-g++
export AR=aarch64-none-elf-ar
export RANLIB=aarch64-none-elf-ranlib
export CFLAGS="-O2 -fPIC -D__SWITCH__ -I${DEVKITPRO}/libnx/include -I${DEVKITPRO}/portlibs/switch/include"
export LDFLAGS="-specs=${DEVKITPRO}/libnx/switch.specs -L${DEVKITPRO}/libnx/lib -L${DEVKITPRO}/portlibs/switch/lib"
export ac_cv_file__dev_ptmx=no
export ac_cv_file__dev_ptc=no
export ac_cv_func_fork=no
export ac_cv_func_vfork=no
export ac_cv_func_dlopen=no

./configure \
    --build=x86_64-pc-linux-gnu \
    --host=aarch64-none-elf \
    --disable-shared \
    --without-ensurepip \
    --without-pymalloc \
    --disable-ipv6

# posixmodule.c assumes fork exists on all Unix-like targets even though
# libnx has no process forking. Its statvfs wrapper also assumes fstatvfs
# whenever statvfs was detected. Disable those interfaces consistently.
python3 - <<'PY'
from pathlib import Path
posix = Path('Modules/posixmodule.c')
data = posix.read_text()
needle = '#      define HAVE_FORK       1\n'
assert data.count(needle) == 1
posix.write_text(data.replace(needle, '/* libnx has no fork. */\n'))
config = Path('pyconfig.h')
data = config.read_text()
data += ('\n#undef HAVE_FORK\n#undef HAVE_FSTATVFS\n'
         '#undef HAVE_STATVFS\n#undef HAVE_WORKING_TZSET\n')
config.write_text(data)
PY

make -j2 libpython3.9.a
