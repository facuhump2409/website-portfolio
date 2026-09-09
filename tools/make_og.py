"""Generate assets/og-card.png — the social preview card.

Regenerate after changing the headline or the proof numbers:
    python3 make_og.py
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG, TEXT, MUTED, FAINT, LINE = "#0A0A0A", "#FFFFFF", "#8A8A8E", "#5A5A5E", "#232323"

HEADLINE = ("Production AI, built by", "someone who’s run", "production.")
STATS = (
    ("100M+", "users served"),
    ("50k+", "daily txns <200ms"),
    ("40%", "latency removed"),
    ("6+", "years in production"),
)


def font(size, weight=400):
    ft = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", size)
    try:
        ft.set_variation_by_axes([weight])
    except Exception:
        pass  # static fallback face
    return ft


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    pad = 80

    d.text((pad, 70), "/ AI LEAD ENGINEER", font=font(22, 500), fill=FAINT)

    y = 138
    for line in HEADLINE:
        d.text((pad, y), line, font=font(64, 700), fill=TEXT)
        y += 80

    d.line([(pad, 432), (W - pad, 432)], fill=LINE, width=1)

    x = pad
    for value, label in STATS:
        d.text((x, 464), value, font=font(38, 700), fill=TEXT)
        d.text((x, 518), label, font=font(18, 400), fill=MUTED)
        x += 262

    d.text((pad, 578), "Facundo Humphreys · Buenos Aires, Argentina",
           font=font(19, 400), fill=FAINT)

    img.save("assets/og-card.png", optimize=True)
    print("wrote assets/og-card.png")


if __name__ == "__main__":
    main()
