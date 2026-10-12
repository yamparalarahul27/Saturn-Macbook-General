# Paper Craft

A Next.js workbench for printing and assembling paper models. The first kit is a simplified **INS Vikramaditya** waterline carrier, approximately 1:400 scale: 71 cm long, 15 cm wide, twenty-four cut-out pieces on thirteen A4 landscape sheets.

## Run

Use Node.js 20.9+ and npm.

```sh
npm install
npm run dev
```

Open http://localhost:3000. No environment variables or external services are needed.

```sh
npm run lint
npm run typecheck
npm run build
npm start
```

## Included

- Assembled, exploded, top, and island close-up views, with part highlighting.
- Twelve on-screen assembly steps, numbered to match the printable parts, with progress saved on the device.
- Thirteen sheet previews and an actual-size, vector PDF download.
- Matching hull/deck seams, glue tabs, fold lines, mounting guides, and a 50 mm print calibration line.
- Desktop-only workspace (1100 px minimum), keyboard-operable controls, and reduced-motion support.

Version 0.3 enlarges the model to 71 cm and replaces the two hull/deck halves with four sections, three deck joining strips, and four internal transverse deck supports. It retains the bridge gallery, foremast platform and folded radar screen, separate aft signal tower, and shared surface artwork. Assembly steps show every required piece and sheet. Progress is stored per kit version so an older step sequence cannot mark new work complete.

Aircraft are planned for the same scale and **are not included** in this first pack. This is a simplified interpretation, not an engineering model or an official Indian Navy product. Digital geometry is validated; real-paper assembly has not yet been tested.

## Print

Download `public/kits/vikramaditya/vikramaditya-a4.pdf`. Use **A4 landscape, Actual size / 100%, single-sided**. Disable Fit to page. Check the 50 mm line before cutting. Use printer-compatible 200 gsm cardstock. The PDF is already 1:400: do not enlarge it again or mix in pieces from the old 1:700 edition.

## Regenerate the printable kit

The checked-in PDF and SVG files are ready to use; Python is only needed when changing the templates.

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/generate-kit.py
```

This writes the PDF into `output/pdf/` and copies it, along with sheet and part SVG previews, into `public/kits/vikramaditya/`. The generator checks exact A4 media boxes, printable margins, face/tab overlap, separate-piece overlap, all three matching hull/deck seams, total 710 mm length, support widths/heights, ramp angle, and contact between the stacked structures. It does not establish real-world assembly tolerances.

## Main files

- `src/data/vikramaditya.json` — physical model dimensions in millimetres, part IDs, sheet assignments and section groups.
- `src/lib/ship.ts` — assembly instructions, section clipping and conversion to stable illustration coordinates.
- `src/components/ship-model.tsx` — interactive SVG illustration.
- `src/components/workbench.tsx` — model, guide, and print workspace.
- `scripts/surface_art.py` — schematic deck and wall artwork; exported to `src/data/surface-art.json` for the browser.
- `scripts/generate-kit.py` — dimensioned paper nets, PDF/SVG export, geometric assertions.
- `docs/design.md` — design rationale, scope, and references.

## Construction

Hull order is **1 → 2 → 15 → 16**; each section is 177.5 mm long. Deck order is **3 → 4 → 17 → 18** with strips **5, 19, 20** underneath the three seams. Supports **21–24** fit their matching hull sections at the midpoint, before the deck is glued on. Their webs are 42 mm high, with separate BASE and DECK tabs. Consult the on-screen guide for folding and glue orientation.

Physical source dimensions live in the JSON. `illustrationScale / scale` converts artwork coordinates to print millimetres; the browser applies the inverse conversion to geometry so the PDF and illustration stay aligned. A 50 mm calibration line is never scaled. The larger kit retains schematic exterior shapes: it is not a new blueprint reconstruction.

## Attribution

Isometric geometry helpers in `src/lib/anatomy/` come from [Anatomy](https://github.com/wheresryan22/anatomy), revision `dbf697a527bbf7d358668e1557cb1e35ff725d46`. Its license is preserved alongside the source. The skill is adapted to prioritize physically printable parts over decorative mechanical detail.

Overall dimensions use the [Ministry of Defence commissioning report](https://www.pib.gov.in/newsite/PrintRelease.aspx?lang=3&reg=3&relid=100633). Deck layout was informed by [Ministry of Defence reference photography](https://commons.wikimedia.org/wiki/File:INS_Vikramaditya_with_full_air_asset_loadout.jpg); no photograph is embedded in the product.
