import data from "@/data/vikramaditya.json";
import type { Plane } from "@/lib/anatomy/iso-kit";

/** The JSON is physical millimetres; the illustration keeps a stable camera space. */
export const kit = data;
const k = data.illustrationScale / data.scale;
const geometry = <
  T extends {
    x: number;
    y: number;
    z: number;
    w: number;
    d: number;
    h: number;
  },
>(
  p: T,
): T => ({
  ...p,
  x: p.x / k,
  y: p.y / k,
  z: p.z / k,
  w: p.w / k,
  d: p.d / k,
  h: p.h / k,
});
export const ship = {
  ...data,
  length: data.length / k,
  beam: data.beam / k,
  split: data.split / k,
  hull: {
    ...data.hull,
    height: data.hull.height / k,
    outline: data.hull.outline.map((pt) => pt.map((v) => v / k)),
  },
  deck: {
    ...data.deck,
    outline: data.deck.outline.map((pt) => pt.map((v) => v / k)),
  },
  ramp: geometry(data.ramp),
  parts: data.parts.map(geometry),
};
export const kitUrl = "/kits/vikramaditya";

export function sectionOutline(
  points: number[][],
  lo: number,
  hi: number,
): Plane[] {
  let result = points.map(([x, y]) => [x, y] as Plane);
  for (const [boundary, sign] of [
    [lo, 1],
    [hi, -1],
  ]) {
    const clipped: Plane[] = [];
    result.forEach((a, i) => {
      const b = result[(i + 1) % result.length];
      const da = (a[0] - boundary) * sign,
        db = (b[0] - boundary) * sign;
      if (da >= -1e-8) clipped.push(a);
      if ((da < 0 && db > 0) || (db < 0 && da > 0)) {
        const t = da / (da - db);
        clipped.push([a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])]);
      }
    });
    result = clipped;
  }
  return result;
}

const instructions = [
  {
    title: "Prepare for the 71 cm build",
    short: "Prepare",
    parts: [],
    intro:
      "A larger carrier, built from thirteen A4 sheets. Clear a flat workspace at least 80 cm long.",
    tasks: [
      "Download this version’s 13-sheet PDF. Print A4 landscape, single-sided, at 100% / Actual size. Do not enlarge it again or use Fit to page.",
      "Measure the 50 mm calibration line. The PDF is already scaled for a 710 mm model; do not mix in pieces from the older 1:700 kit.",
      "Use 200 gsm cardstock if your printer supports it, a ruler, scissors, a blunt scoring tool and a little PVA glue. Test folds on a spare scrap.",
      "Score every blue dashed fold before cutting the bold outer outlines. Keep all pale tabs. Fine grey marks are detail or placement guides.",
    ],
    tip: "This is the 1:400 edition. All blue folds go away from the printed face; actual paper thickness and glue fit still need a test build.",
  },
  {
    title: "Fold the stern hull",
    short: "Stern hull",
    parts: [1],
    intro:
      "The first of four 177.5 mm hull sections forms a square-backed open tray.",
    tasks: [
      "Cut and score part 1 from sheet 1. Before folding, transfer the support centreline to the unprinted inside: 88.75 mm from either end of the base.",
      "Lay the printed base face down. Fold all four walls upward, then fold each lettered corner tab inside.",
      "Apply glue to the printed face of each corner tab and attach it behind its matching letter on the next wall. Keep the base flat.",
      "Fold the DECK rim tabs inward, level with the top edges. Leave them unglued until the deck is ready.",
    ],
    tip: "The wall marked JOIN 2 faces the bow. The printed base and hull decoration belong on the outside.",
  },
  {
    title: "Join all four hull sections",
    short: "Join hull",
    parts: [2, 15, 16],
    intro: "The hull runs from stern to bow in the order 1 → 2 → 15 → 16.",
    tasks: [
      "Cut and score parts 2, 15 and 16 from sheets 2–4. Transfer each support line to the inside, 88.75 mm from the end of its base.",
      "Build each open tray as before: printed base down, walls up, matching lettered tabs inside and DECK tabs folded inward.",
      "Dry-fit the numbered JOIN walls back-to-back: 1 to 2, 2 to 15, then 15 to 16. Part 16 is the narrow bow.",
      "Glue the mating end walls together on a flat surface. Check the hull stays straight and all four bottoms remain level as the joins dry.",
    ],
    tip: "The four sections total 710 mm before paper-thickness effects. Do not overlap their bases or shorten the end walls.",
  },
  {
    title: "Fit the internal deck supports",
    short: "Supports",
    parts: [21, 22, 23, 24],
    intro:
      "Four transverse supports reduce the unsupported deck span inside the long hull.",
    tasks: [
      "Cut and score supports 21–24 from sheet 13. The large rectangles stay flat; fold both small tabs away from the printed face through 90°.",
      "Match support 21 to hull 1, 22 to hull 2, 23 to hull 15, and 24 to hull 16. Their different widths follow the hull taper.",
      "Stand each support across the hull on its transferred centreline. Glue the printed face of its BASE tab to the inside hull floor; keep the web upright.",
      "Check that each DECK tab is level with the hull rim and that all tabs point toward the stern. Let the base glue dry; leave the DECK tabs unglued.",
    ],
    tip: "The supports are 42 mm high. Their printed top-tab faces point upward to contact the underside of the deck.",
  },
  {
    title: "Assemble the four-panel deck",
    short: "Flight deck",
    parts: [3, 4, 17, 18, 5, 19, 20],
    intro:
      "Make one flat deck from four panels, with three joining strips underneath.",
    tasks: [
      "Cut deck panels 3, 4, 17 and 18 from sheets 5–8. Cut joining strips 5, 19 and 20; all seven pieces remain flat.",
      "Arrange the deck printed-side down in stern-to-bow order 3 → 4 → 17 → 18. Butt the matching edges together; do not overlap them.",
      "Centre strip 5 beneath seam 3/4, strip 19 beneath seam 4/17, and strip 20 beneath seam 17/18, with 10 mm under each panel. Centre each strip across the seam’s width and match its dotted centreline to the seam.",
      "Let the deck dry flat. Dry-fit it on the hull, aligning all three seams. Apply thin glue to the hull rim and support DECK tabs, then attach the deck without bending it.",
    ],
    tip: "The deck is wider than the hull. Its overhang is intentional. Support the entire model on a flat board while the glue sets.",
  },
  {
    title: "Raise the ski jump",
    short: "Ski jump",
    parts: [6],
    intro:
      "The enlarged bow ramp retains the buildable straight-wedge construction.",
    tasks: [
      "Cut and score part 6 from sheet 12, keeping the two triangular sides, end wall and all base tabs.",
      "Fold both triangular sides and the tall end wall down, away from the printed ramp surface.",
      "Fold the three base tabs inward and dry-fit the wedge on deck guide 6.",
      "Glue its base tabs to the deck with the low end toward the stern and the high end toward the bow. Match the yellow centrelines.",
    ],
    tip: "This edition still uses a straight 14° wedge. A more faithful curved ramp needs a separately developed rib and skin pattern.",
  },
  {
    title: "Build the island",
    short: "Island",
    parts: [7],
    intro:
      "The island sits on the starboard side: the right side when looking toward the bow.",
    tasks: [
      "Cut and score island 7 from sheet 9. Fold its walls down from the roof, away from the printed face.",
      "Glue corner tabs 7A–7D behind their matching edges to form a hollow box.",
      "Fold all base tabs inward and apply glue to their printed undersides.",
      "Seat the island on deck guide 7. Roof guide 11 faces the bow and guide 9 faces the stern. Keep it level while drying.",
    ],
    tip: "Allow the large joined deck to dry fully before adding the island.",
  },
  {
    title: "Layer the gallery and bridge",
    short: "Bridge",
    parts: [11, 8],
    intro:
      "The projecting gallery supports the windowed bridge at the forward end of the island.",
    tasks: [
      "Cut gallery 11 from sheet 12 and keep it flat. Glue its underside onto island guide 11 with an even 7 mm side overhang.",
      "Cut and score bridge 8 from sheet 10. Fold its walls down and glue 8A–8D behind their matching edges.",
      "Fold the bridge base tabs inward and glue their printed faces onto gallery guide 8. A 3.5 mm gallery rim remains around the bridge.",
      "Keep guide 10 visible on the bridge roof for the foremast. Let both layers set level before continuing.",
    ],
    tip: "Do not trim the gallery’s projecting edges to the narrower island underneath.",
  },
  {
    title: "Fit the funnel",
    short: "Funnel",
    parts: [9],
    intro: "The funnel mounts behind the bridge on the island roof.",
    tasks: [
      "Cut and score funnel 9 from sheet 10, retaining its corner and base tabs.",
      "Fold its walls down and glue tabs 9A–9D behind the matching edges.",
      "Fold the base tabs inward and apply a little glue to their printed undersides.",
      "Set the funnel on island guide 9 with the dark grille on top. Hold it upright while the glue sets.",
    ],
    tip: "The grille and vents are printed detail; do not cut their fine lines.",
  },
  {
    title: "Build the foremast and radar",
    short: "Radar",
    parts: [10, 12, 13],
    intro:
      "The foremast supports a flat platform and an upright folded radar panel.",
    tasks: [
      "Cut foremast 10 from sheet 11. Fold the walls down, glue matching corners and glue its inward base tabs onto bridge guide 10.",
      "Cut platform 12 from sheet 12. Centre it on the foremast roof: 7 mm overhang at each end and 5.25 mm on either side. Its longer edges run fore-and-aft.",
      "Cut screen 13 from sheet 12. Fold its lavender foot away from the printed screen by 90°, forming an L shape.",
      "Glue the printed foot face onto platform guide 13. The screen stands on the port edge of the guide and its foot points toward starboard.",
    ],
    tip: "Keep the printed radar grid intact. Let the upright screen set before moving the ship.",
  },
  {
    title: "Add the aft signal tower",
    short: "Aft tower",
    parts: [14],
    intro:
      "The separate tower sits behind the island, clear of the printed deck lifts.",
    tasks: [
      "Cut and score tower 14 from sheet 11, retaining its corner and base tabs.",
      "Fold the walls down and glue tabs 14A–14D behind the matching edges.",
      "Fold base tabs inward and glue their printed faces onto deck guide 14.",
      "Keep the tower upright while drying. Handle the ship from underneath, avoiding the radar and platform edges.",
    ],
    tip: "The printed ladders and grille stay on the outside and do not need cutting.",
  },
  {
    title: "Check your 71 cm carrier",
    short: "Final check",
    parts: [],
    intro:
      "A larger paper carrier, ready for future aircraft at the same 1:400 scale.",
    tasks: [
      "Check the four hull bases rest flat and the three deck seams form one continuous surface.",
      "Check the ski jump rises toward the bow and the island is on the starboard side.",
      "Let the glue dry fully. Move the model on a supporting board or with both hands beneath the hull; do not lift by an overhanging deck edge.",
      "Check the overall length against 71 cm. Record any paper-fit or sagging issues before adding the aircraft, which are not yet included.",
    ],
    tip: "This is a larger, reinforced edition of the simplified model. It is not a verified blueprint reconstruction; physical assembly remains untested.",
  },
];

const assembled = new Set<number>();
export const steps = instructions.map((step, index) => {
  step.parts.forEach((id) => assembled.add(id));
  return {
    ...step,
    part: step.parts[0] ?? 0,
    sheets: [...new Set(step.parts.map((id) => ship.parts[id - 1].sheet))].sort(
      (a, b) => a - b,
    ),
    visible:
      index === 0 || index === instructions.length - 1
        ? ship.parts.map((p) => p.id)
        : [...assembled],
  };
});
