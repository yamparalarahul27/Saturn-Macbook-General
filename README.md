# Paper Craft

A Next.js workbench for printing and assembling paper models. The first kit is a simplified **INS Vikramaditya** waterline carrier, approximately 1:700 scale: 40.6 cm long, 8.6 cm wide, ten cut-out pieces on five A4 landscape sheets.

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

- Assembled, exploded, and top views, with part highlighting.
- Nine on-screen assembly steps, numbered to match the printable parts, with progress saved on the device.
- Five sheet previews and an actual-size, vector PDF download.
- Matching hull/deck seams, glue tabs, fold lines, mounting guides, and a 50 mm print calibration line.
- Desktop-only workspace (1100 px minimum), keyboard-operable controls, and reduced-motion support.

Aircraft are planned for the same scale and **are not included** in this first pack. This is a simplified interpretation, not an engineering model or an official Indian Navy product. Digital geometry is validated; real-paper assembly has not yet been tested.

## Print

Download `public/kits/vikramaditya/vikramaditya-a4.pdf`. Use **A4 landscape, Actual size / 100%, single-sided**. Disable Fit to page. Check the 50 mm line before cutting. Use 160–200 gsm paper if supported by your printer.

## Regenerate the printable kit

The checked-in PDF and SVG files are ready to use; Python is only needed when changing the templates.

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/generate-kit.py
```

This writes the PDF into `output/pdf/` and copies it, along with sheet and part SVG previews, into `public/kits/vikramaditya/`. The generator checks exact A4 media boxes, printable margins, face/tab overlap, separate-piece overlap, matching middle seams, overall scale, and ramp angle. It does not establish real-world assembly tolerances.

## Main files

- `src/data/vikramaditya.json` — shared model dimensions, part IDs, sheet assignments.
- `src/lib/ship.ts` — assembly instructions and split-outline geometry.
- `src/components/ship-model.tsx` — interactive SVG illustration.
- `src/components/workbench.tsx` — model, guide, and print workspace.
- `scripts/generate-kit.py` — dimensioned paper nets, PDF/SVG export, geometric assertions.
- `docs/design.md` — design rationale, scope, and references.

## Attribution

Isometric geometry helpers in `src/lib/anatomy/` come from [Anatomy](https://github.com/wheresryan22/anatomy), revision `dbf697a527bbf7d358668e1557cb1e35ff725d46`. Its license is preserved alongside the source. The skill is adapted to prioritize physically printable parts over decorative mechanical detail.

Overall dimensions use the [Ministry of Defence commissioning report](https://www.pib.gov.in/newsite/PrintRelease.aspx?lang=3&reg=3&relid=100633). Deck layout was informed by [Ministry of Defence reference photography](https://commons.wikimedia.org/wiki/File:INS_Vikramaditya_with_full_air_asset_loadout.jpg); no photograph is embedded in the product.
