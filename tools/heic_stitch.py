"""Decode an iPhone HEIC by stitching its tile grid.

ffmpeg exposes each 512x512 tile of a HEIF grid as its own stream but will not
assemble them — left to itself it picks the largest stream, which is the HDR
gain map (a dim greyscale ghost of the photo). So: pull every tile, lay them
out row-major, crop to the real dimensions.

Usage: python3 heic_stitch.py <in.heic> <out.jpg> [rotate_degrees_ccw]
"""

import os
import re
import subprocess
import sys
import tempfile

from PIL import Image

TILE = 512


def dimensions(path):
    """Real image size, from sips metadata (read-only, so it works sandboxed)."""
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path],
                         capture_output=True, text=True).stdout
    w = int(re.search(r"pixelWidth:\s*(\d+)", out).group(1))
    h = int(re.search(r"pixelHeight:\s*(\d+)", out).group(1))
    return w, h


def tile_streams(path):
    """Indices of the 512x512 tile streams, in order."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=index,width,height",
         "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    idx = []
    for line in out.strip().splitlines():
        parts = line.split(",")
        if len(parts) >= 3 and parts[1] == str(TILE) and parts[2] == str(TILE):
            idx.append(int(parts[0]))
    return idx


def stitch(src, dst, rotate=0, max_edge=1400, quality=84):
    w, h = dimensions(src)
    cols, rows = -(-w // TILE), -(-h // TILE)
    streams = tile_streams(src)

    expected = cols * rows
    if len(streams) < expected:
        raise SystemExit(f"{src}: found {len(streams)} tiles, need {expected}")
    streams = streams[:expected]

    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR", "/tmp")) as tmp:
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", src]
        for n, s in enumerate(streams):
            cmd += ["-map", f"0:{s}", "-frames:v", "1", f"{tmp}/t{n:03d}.png"]
        subprocess.run(cmd, check=True)

        canvas = Image.new("RGB", (cols * TILE, rows * TILE))
        for n in range(expected):
            canvas.paste(Image.open(f"{tmp}/t{n:03d}.png"),
                         ((n % cols) * TILE, (n // cols) * TILE))

    img = canvas.crop((0, 0, w, h))
    if rotate:
        img = img.rotate(rotate, expand=True)
    img.thumbnail((max_edge, max_edge))
    img.save(dst, quality=quality, optimize=True, progressive=True)
    print(f"{dst}  {img.size}  ({cols}x{rows} tiles)")


if __name__ == "__main__":
    stitch(sys.argv[1], sys.argv[2],
           rotate=int(sys.argv[3]) if len(sys.argv) > 3 else 0)
