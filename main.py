"""Copy the finished front page to the output directory.

This entry is a newspaper front page that sums up the world news of
Tuesday 24 November 2026 in one image. The image itself is shipped in
this repository as ``entry.png``; this program only checks that it is
a whole, in-limits PNG and then copies it, byte for byte, to the
output directory.

Run it with::

    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

``MAKEFUN_OUTPUT_DIR`` defaults to ``/output``. The program uses
only the Python standard library, needs no network, and writes the
same bytes on every run.
"""

import hashlib
import os
import shutil
import struct
import sys
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576
MAX_WIDTH = 1024
MAX_HEIGHT = 1024


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_png(path: Path) -> None:
    """Raise if the file is not a whole PNG within the size limits."""
    data = path.read_bytes()
    if len(data) > MAX_BYTES:
        raise SystemExit(f"entry.png is {len(data)} bytes, over the {MAX_BYTES} limit")
    if data[:8] != PNG_SIGNATURE:
        raise SystemExit("entry.png does not start with the PNG signature")
    if len(data) < 33 or data[12:16] != b"IHDR":
        raise SystemExit("entry.png has no IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        raise SystemExit(f"entry.png is {width}x{height}, over the {MAX_WIDTH}x{MAX_HEIGHT} limit")
    print(f"Checked entry.png: PNG, {width}x{height}, {len(data)} bytes")


def main() -> None:
    source = Path(__file__).resolve().parent / "entry.png"
    if not source.is_file():
        raise SystemExit(f"entry.png not found next to main.py: {source}")
    check_png(source)
    before = sha256_of(source)

    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / "entry.png"
    shutil.copyfile(source, destination)

    after = sha256_of(destination)
    if before != after:
        raise SystemExit("copy mismatch: sha256 differs after copying")
    print(f"Copied entry.png to {destination}")
    print(f"sha256: {after}")


if __name__ == "__main__":
    main()
