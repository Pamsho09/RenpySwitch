"""Verify NRO embedded RomFS files against their build inputs."""
import argparse
import hashlib
from pathlib import Path
import struct


def verify(nro, source):
    data = nro.read_bytes()
    if data[16:20] != b"NRO0":
        raise ValueError("Missing NRO header")
    asset = struct.unpack_from("<I", data, 24)[0]
    if data[asset:asset + 4] != b"ASET":
        raise ValueError("Missing NRO asset section: RomFS was not embedded")
    offset, size = struct.unpack_from("<QQ", data, asset + 40)
    start = asset + offset
    if not offset or size < 80 or start + size > len(data):
        raise ValueError("Invalid RomFS section bounds")
    rom = data[start:start + size]
    header = struct.unpack_from("<10Q", rom)
    if header[0] != 80:
        raise ValueError("Invalid RomFS header")
    directories, files, files_size, payload = header[3], header[7], header[8], header[9]

    def directory_name(offset, seen=None):
        seen = set() if seen is None else seen
        if offset in seen:
            raise ValueError("RomFS directory cycle")
        seen.add(offset)
        parent, _, _, _, _, length = struct.unpack_from("<6I", rom, directories + offset)
        name = rom[directories + offset + 24:directories + offset + 24 + length].decode()
        if offset == 0:
            return ""
        prefix = directory_name(parent, seen)
        return prefix + name + "/"

    found = {}
    cursor = 0
    while cursor < files_size:
        position = files + cursor
        parent, _, offset, size, _, length = struct.unpack_from("<IIQQII", rom, position)
        name = directory_name(parent) + rom[position + 32:position + 32 + length].decode()
        content = rom[payload + offset:payload + offset + size]
        if len(content) != size or name in found:
            raise ValueError("Invalid or duplicate RomFS file: " + name)
        found[name] = hashlib.sha256(content).hexdigest()
        cursor += (32 + length + 3) & ~3
    expected = {p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in source.rglob("*") if p.is_file()}
    if not expected or found != expected:
        raise ValueError("Embedded RomFS does not match input files")
    print(f"Verified {nro.name}: {len(found)} embedded files match inputs")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("nro", type=Path)
    parser.add_argument("romfs", type=Path)
    args = parser.parse_args()
    verify(args.nro, args.romfs)
