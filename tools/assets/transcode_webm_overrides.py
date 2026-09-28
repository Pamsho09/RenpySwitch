"""Create lightweight loose WebM files that override videos in an RPA.

Example:
  python3 tools/transcode_webm_overrides.py original-copy/game/images.rpa \
      diagnostic/optimized-webm --ffmpeg /path/to/ffmpeg

The output mirrors archive paths (for example, images/Personajes/...). Copy
those paths into the game's directory; Ren'Py checks loose files before RPA.
No archive or original asset is modified.
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from rpa_audit import index


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--ffmpeg", required=True, type=Path)
    parser.add_argument("--only", action="append", help="Exact archive path to convert")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--bitrate", default="1500k")
    args = parser.parse_args()
    if min(args.width, args.height, args.fps) <= 0:
        parser.error("Width, height and fps must be positive")

    video_filter = (
        "fps=%d,scale=w='min(iw,%d)':h='min(ih,%d)':"
        "force_original_aspect_ratio=decrease:force_divisible_by=2"
    ) % (args.fps, args.width, args.height)

    archive_index = index(args.archive)
    names = sorted(name for name in archive_index if name.lower().endswith(".webm"))
    if args.only:
        missing = set(args.only) - set(names)
        if missing:
            parser.error("Not present in archive: " + ", ".join(sorted(missing)))
        names = sorted(set(args.only))

    args.output.mkdir(parents=True, exist_ok=True)
    manifest = []
    with args.archive.open("rb") as archive, tempfile.TemporaryDirectory() as temp_dir:
        source = Path(temp_dir) / "source.webm"
        for number, name in enumerate(names, 1):
            target = args.output / name
            if not target.resolve().is_relative_to(args.output.resolve()):
                raise ValueError("Unsafe archive path: " + name)
            target.parent.mkdir(parents=True, exist_ok=True)
            with source.open("wb") as extracted:
                for offset, size, prefix in archive_index[name]:
                    if isinstance(prefix, str):
                        prefix = prefix.encode("latin1")
                    archive.seek(offset)
                    extracted.write(prefix)
                    extracted.write(archive.read(size - len(prefix)))

            command = [
                str(args.ffmpeg), "-hide_banner", "-loglevel", "error", "-nostdin",
                "-i", str(source), "-map", "0:v:0", "-map", "0:a?",
                "-vf", video_filter, "-c:v", "libvpx", "-c:a", "copy",
                "-deadline", "good", "-cpu-used", "5", "-b:v", args.bitrate,
                "-crf", "20", "-y", str(target),
            ]
            subprocess.run(command, check=True)
            manifest.append({
                "path": name,
                "source_bytes": source.stat().st_size,
                "output_bytes": target.stat().st_size,
                "output_sha256": sha256(target),
            })
            print("%d/%d %s %d -> %d bytes" % (
                number, len(names), name, source.stat().st_size,
                target.stat().st_size), flush=True)

    (args.output / "transcode-manifest.json").write_text(
        json.dumps({"filter": video_filter, "bitrate": args.bitrate,
                    "videos": manifest}, indent=2)
    )


if __name__ == "__main__":
    main()
