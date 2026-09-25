#!/usr/bin/env bash
set -euo pipefail

# First native Ren'Py 8 prerequisite: a CPython 3.9 static library for libnx.
# Keep this isolated from the working Ren'Py 7 build until it links and runs.
export DEBIAN_FRONTEND=noninteractive
project_root=$(pwd)
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
data = data.replace(needle, '/* libnx has no fork. */\n')
for symbol in ('EXECV', 'GETEGID', 'GETEUID', 'GETGID', 'GETPPID',
               'GETUID', 'PIPE', 'TTYNAME'):
    import re
    data = re.sub(r'(?m)^#\s*define HAVE_' + symbol + r'\s+1$',
                  '/* libnx has no ' + symbol.lower() + ' */', data)
needle = 'int i = (int)umask(mask);'
assert data.count(needle) == 1
data = data.replace(needle, 'int i = 0; /* libnx has no umask */')
posix.write_text(data)
config = Path('pyconfig.h')
data = config.read_text()
data += ('\n#undef HAVE_FORK\n#undef HAVE_FSTATVFS\n'
         '#undef HAVE_STATVFS\n#undef HAVE_WORKING_TZSET\n'
         '#undef HAVE_DECL_TZNAME\n#undef HAVE_SYS_RESOURCE_H\n'
         '#undef HAVE_FDATASYNC\n#undef HAVE_FCHDIR\n'
         '#undef HAVE_SYSCONF\n#undef HAVE_TTYNAME_R\n'
         '#undef HAVE_CHROOT\n#undef HAVE_SETGROUPS\n')
config.write_text(data)
setup = Path('Modules/Setup')
data = setup.read_text()
needle = 'pwd pwdmodule.c'
assert data.count(needle) == 1
setup.write_text(data.replace(needle, '#pwd pwdmodule.c'))
PY

make -j2 libpython3.9.a

# Link a small NSO-shaped program before attempting the full engine. This
# reveals missing libnx/POSIX symbols that the archive build cannot detect.
"$CC" -O2 -fPIE -D__SWITCH__ \
    -IInclude -I. -I"$DEVKITPRO/libnx/include" \
    "$project_root/experimental/python3/smoke.c" libpython3.9.a \
    -specs="$DEVKITPRO/libnx/switch.specs" \
    -L"$DEVKITPRO/libnx/lib" -L"$DEVKITPRO/portlibs/switch/lib" \
    -lm -lz -lnx -o /tmp/python3-switch/smoke.elf
"$DEVKITPRO/tools/bin/elf2nso" \
    /tmp/python3-switch/smoke.elf /tmp/python3-switch/smoke.nso

python3 - <<'PY'
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
library = Path('Lib')
target = Path('/tmp/python3-switch/python39.zip')
with ZipFile(target, 'w', ZIP_DEFLATED) as archive:
    for path in sorted(library.rglob('*.py')):
        if path.relative_to(library).parts[0] in {'test', 'idlelib', 'tkinter'}:
            continue
        archive.write(path, path.relative_to(library).as_posix())
print(target, target.stat().st_size)
PY

mkdir -p /tmp/python3-switch/romfs/Contents
cp /tmp/python3-switch/python39.zip /tmp/python3-switch/romfs/Contents/
"$DEVKITPRO/tools/bin/elf2nro" \
    /tmp/python3-switch/smoke.elf /tmp/python3-switch/smoke.nro \
    --romfsdir=/tmp/python3-switch/romfs

# Probe one generated pygame_sdl2 extension against the Python 3 headers and
# the existing Switch SDL2 portlibs before porting the complete module set.
pygame_archive=/tmp/python3-switch/pygame_sdl2-2.1.0+renpy8.3.7.tar.gz
curl -fL --retry 3 \
    'https://www.renpy.org/dl/8.3.7/pygame_sdl2-2.1.0+renpy8.3.7.tar.gz' \
    -o "$pygame_archive"
echo '4630b82d7e9ff3e5a864cd3693b4ef093a8ae9e87c3c7cb9ff5ca7e69299febf  /tmp/python3-switch/pygame_sdl2-2.1.0+renpy8.3.7.tar.gz' | sha256sum -c -
tar -xf "$pygame_archive" -C /tmp/python3-switch
pygame_source=/tmp/python3-switch/pygame_sdl2-2.1.0+renpy8.3.7
"$CC" -O2 -fPIC -D__SWITCH__ \
    -IInclude -I. \
    -I"$pygame_source/src" -I"$pygame_source/gen3" \
    -I"$DEVKITPRO/libnx/include" \
    -I"$DEVKITPRO/portlibs/switch/include" \
    -I"$DEVKITPRO/portlibs/switch/include/SDL2" \
    -c "$pygame_source/gen3/pygame_sdl2.color.c" \
    -o /tmp/python3-switch/pygame_sdl2.color.o
