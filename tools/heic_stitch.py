"""Decode an iPhone HEIC by stitching its tile grid.

ffmpeg exposes each tile of a HEIF grid as its own stream but will not assemble
them - left to itself it picks the largest stream, which is the HDR gain map (a
dim greyscale ghost of the photo). So: pull every tile, lay them out row-major,
crop to the real dimensions.

Tile size varies by capture device (512x512 on older iPhones, 640x896 on 48MP
sensors), so it is detected rather than assumed.

Usage: python3 tools/heic_stitch.py <in.heic> <out.jpg> [rotate_degrees_ccw]
"""

import os
import re
import subprocess
import sys
import tempfile
from collections import Counter

from PIL import Image


def dimensions(path):
    """Real image size, from sips metadata (read-only, so it works sandboxed)."""
    out = subprocess.run(
        ["sips", "-g", "pixelWidth", "-g", "pixelHeight", path],
        capture_output=True, text=True).stdout
    w = int(re.search(r"pixelWidth:\s*(\d+)", out).group(1))
    h = int(re.search(r"pixelHeight:\s*(\d+)", out).group(1))
    return w, h


def streams(path):
    """[(index, width, height)] for every video stream in the file."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=index,width,height",
         "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    rows = []
    for line in out.strip().splitlines():
        parts = [p for p in line.split(",") if p != ""]
        if len(parts) >= 3:
            rows.append((int(parts[0]), int(parts[1]), int(parts[2])))
    return rows


def layout(w, h, tw, th, n):
    """Smallest cols x rows of tw x th tiles covering w x h, within n tiles."""
    cols = -(-w // tw)
    rows = -(-h // th)
    if cols * rows > n:
        raise SystemExit(
            "cannot cover %dx%d with %d tiles of %dx%d" % (w, h, n, tw, th))
    return cols, rows


def stitch(src, dst, rotate=0, max_edge=1400, quality=84):
    w, h = dimensions(src)
    all_streams = streams(src)

    # The tile size is whichever stream shape dominates the file.
    shape = Counter((sw, sh) for _, sw, sh in all_streams).most_common(1)[0][0]
    tw, th = shape
    tiles = [i for i, sw, sh in all_streams if (sw, sh) == shape]

    cols, rows = layout(w, h, tw, th, len(tiles))
    tiles = tiles[: cols * rows]

    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR", "/tmp")) as tmp:
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", src]
        for n, s in enumerate(tiles):
            cmd += ["-map", "0:%d" % s, "-frames:v", "1",
                    "%s/t%03d.png" % (tmp, n)]
        subprocess.run(cmd, check=True)

        canvas = Image.new("RGB", (cols * tw, rows * th))
        for n in range(len(tiles)):
            canvas.paste(Image.open("%s/t%03d.png" % (tmp, n)),
                         ((n % cols) * tw, (n // cols) * th))

    img = canvas.crop((0, 0, w, h))
    if rotate:
        img = img.rotate(rotate, expand=True)
    img.thumbnail((max_edge, max_edge))
    img.save(dst, quality=quality, optimize=True, progressive=True)
    print("%s %s (%dx%d tiles of %dx%d)" % (dst, img.size, cols, rows, tw, th))


if __name__ == "__main__":
    stitch(sys.argv[1], sys.argv[2],
           rotate=int(sys.argv[3]) if len(sys.argv) > 3 else 0)
