# website-portfolio

Personal portfolio for **Facundo Humphreys — AI Lead Engineer**.

A single static page, no build step and no dependencies:

| File | Purpose |
| --- | --- |
| `index.html` | Markup, metadata, JSON-LD, and the pre-paint theme script |
| `styles.css` | Design tokens and both themes — every colour goes through a custom property |
| `main.js` | Theme toggle, scroll reveals, the pinned `#method` animation, YouTube facade |
| `assets/` | CV PDF, favicons, social card, and the "Beyond coding" photographs |
| `tools/` | One-off generators — not part of the deployed page |

### tools/

Run from the repo root:

| Script | Purpose |
| --- | --- |
| `make_og.py` | Regenerates `assets/og-card.png`. Rerun after changing the headline or the proof numbers. |
| `make_icons.py` | Regenerates `favicon.ico` and `apple-touch-icon.png` to match `assets/favicon.svg`. |
| `heic_stitch.py` | Decodes an iPhone HEIC. ffmpeg exposes each 512×512 tile as its own stream but won't assemble the grid — left alone it picks the largest stream, which is the HDR gain map (a dim greyscale ghost of the photo). This pulls every tile and lays them out row-major. |

## Run locally

```bash
python3 -m http.server 8000
open http://localhost:8000
```

Opening `index.html` via `file://` mostly works, but a real server is needed for
the CV download link and correct relative asset paths.

## Design notes

- **Dark by default.** The theme is resolved by an inline script in `<head>` so
  the page never paints white before switching. OS *light* opts into light;
  anything else — including no signal — lands on dark. An explicit choice is
  stored in `localStorage` under `theme` and wins over the OS from then on.
- **Motion is opt-in.** Reveal styles are gated behind a `.js` class set by
  `main.js`, so the page is fully readable with JavaScript disabled.
  `prefers-reduced-motion: reduce` disables the scroll observers entirely.
- **No third-party requests** beyond the Inter webfont. The talk thumbnail is a
  facade — nothing is fetched from YouTube until someone clicks play.

## Deployment

Deploys to Vercel from `master` via Vercel's git integration. There is no CI
workflow in this repository; pushing to `master` is what triggers a build.
