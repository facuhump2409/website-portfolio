"""Generate the raster favicon fallbacks from the same design as favicon.svg.

Safari's tab bar and the iOS home screen want PNG/ICO, so the SVG alone is not
enough. Run from the repo root:

    python3 tools/make_icons.py
"""

from PIL import Image, ImageDraw, ImageFont

BG, FG = "#0a0a0a", "#ffffff"
SUPERSAMPLE = 4  # draw big, downsample — gives clean rounded corners


def font(size, weight=600):
    ft = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", size)
    try:
        ft.set_variation_by_axes([weight])
    except Exception:
        pass
    return ft


def icon(size, radius_ratio=0.22):
    """One rounded-square 'FH' mark at the given edge length."""
    s = size * SUPERSAMPLE
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * radius_ratio), fill=BG)

    ft = font(int(s * 0.46))
    box = d.textbbox((0, 0), "FH", font=ft)
    x = (s - box[2] - box[0]) / 2
    y = (s - box[3] - box[1]) / 2 - s * 0.01
    d.text((x, y), "FH", font=ft, fill=FG)

    return img.resize((size, size), Image.LANCZOS)


def main():
    # Multi-resolution .ico for legacy browsers and bookmark bars.
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icon(256).convert("RGB").save("assets/favicon.ico", sizes=sizes)

    # iOS home screen: opaque and unrounded — the OS applies its own mask.
    icon(180, radius_ratio=0).convert("RGB").save(
        "assets/apple-touch-icon.png", optimize=True
    )

    print("wrote assets/favicon.ico and assets/apple-touch-icon.png")


if __name__ == "__main__":
    main()
