import data from "@/data/vikramaditya.json";
import type { Plane } from "@/lib/anatomy/iso-kit";

export const ship = data;
export const kitUrl = "/kits/vikramaditya";
export function splitOutline(points: number[][], forward: boolean): Plane[] {
  const result: Plane[] = [];
  points.forEach((a, i) => {
    const b = points[(i + 1) % points.length];
    const da = (a[0] - data.split) * (forward ? 1 : -1);
    const db = (b[0] - data.split) * (forward ? 1 : -1);
    if (da >= -1e-8) result.push([a[0], a[1]]);
    if ((da < 0 && db > 0) || (db < 0 && da > 0)) {
      const t = da / (da - db);
      result.push([a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])]);
    }
  });
  return result;
}
export const steps = [
  {
    title: "Prepare your workbench",
    short: "Print & prepare",
    part: 0,
    visible: 10,
    sheet: 0,
    intro:
      "Five flat sheets. One small aircraft carrier. Start by checking your print size.",
    tasks: [
      "Download the A4 PDF and print all five sheets in landscape, single-sided, at 100% / Actual size. Turn off Fit to page.",
      "Measure the 50 mm line on the first sheet. Reprint if it is not exactly 50 mm.",
      "Use 160–200 gsm paper, scissors, a ruler, a blunt scoring tool, and a little PVA glue. Check your printer supports the paper weight.",
      "Score the blue dashed folds gently before cutting. Cut only the bold outer outlines and keep every pale glue tab.",
    ],
    tip: "All blue folds go away from the printed face. Dotted grey boxes are placement guides. They are not cuts or folds.",
  },
  {
    title: "Fold the aft hull",
    short: "Aft hull",
    part: 1,
    visible: 1,
    sheet: 1,
    intro: "Make the broad, flat-backed half of the carrier.",
    tasks: [
      "Cut out part 1 as one piece, including the corner and DECK tabs.",
      "Place the printed base face down. Fold the four walls upward to make an open tray.",
      "Fold each lettered corner tab inside. Apply glue to its printed face and attach it behind the matching letter on the next wall.",
      "Fold the DECK rim tabs inward, level with the top edge. Keep the bottom flat while the joins dry.",
    ],
    tip: "The wall marked JOIN will meet the forward hull. Do not glue the DECK tabs yet.",
  },
  {
    title: "Build and join the forward hull",
    short: "Forward hull",
    part: 2,
    visible: 2,
    sheet: 2,
    intro:
      "The tapered half forms the bow. Join both halves on a flat surface.",
    tasks: [
      "Cut and score part 2. Fold the walls up with the printed base down, then glue matching lettered corner tabs inside.",
      "Fold its DECK rim tabs inward, just as you did on the aft hull.",
      "Dry-fit the two full-height walls marked JOIN back-to-back. The tapered bow points away from the aft hull.",
      "Spread a thin layer of glue between those two walls. Press them together with both hull bottoms level and allow to set.",
    ],
    tip: "Check the centre joint from above before the glue sets. Both halves should form one straight, 40.6 cm hull.",
  },
  {
    title: "Join the flight deck",
    short: "Flight deck",
    part: 3,
    visible: 5,
    sheet: 3,
    intro:
      "The deck joins edge-to-edge; the runway should stay perfectly flat.",
    tasks: [
      "Cut out aft deck 3, forward deck 4, and joining strip 5. None of these three pieces needs folding.",
      "Lay the deck halves printed-side down. Butt their straight middle edges together, matching the runway markings.",
      "Glue strip 5 across the underside of the seam: 10 mm beneath each deck half. Its dotted centreline sits directly under the joint.",
      "Let the deck dry flat. Dry-fit it on the hull, align the centre seams and bow, then glue the hull rim tabs to the deck underside.",
    ],
    tip: "The deck overhangs the hull. That is intentional. Do not overlap the deck halves or bend the joining strip.",
  },
  {
    title: "Raise the ski jump",
    short: "Ski jump",
    part: 6,
    visible: 6,
    sheet: 4,
    intro:
      "This little wedge gives the bow its characteristic raised take-off ramp.",
    tasks: [
      "Cut and score part 6. The large rectangle is the ramp surface; the triangles support its sides.",
      "Fold both triangular sides and the tall end wall down, away from the printed surface.",
      "Fold the three base tabs inward. Dry-fit on the dotted rectangle marked 6 at the bow.",
      "Glue the tabs to the deck. Keep the low end facing the stern, the high end facing the bow, and both runway centrelines aligned.",
    ],
    tip: "The paper ramp is a straight 14° wedge: a buildable simplification of the ship’s curved ski jump.",
  },
  {
    title: "Add the island",
    short: "Island",
    part: 7,
    visible: 7,
    sheet: 5,
    intro:
      "The long island sits on the starboard side—the right side when looking toward the bow.",
    tasks: [
      "Cut out part 7. Fold the four walls down from its roof, away from the printed face.",
      "Glue tabs 7A–7D behind their matching wall edges to form a hollow box.",
      "Fold all four base tabs inward. Spread glue on the printed underside of those folded tabs.",
      "Set the island on deck guide 7. Roof guide 8 must be toward the bow; guide 9 must be toward the stern.",
    ],
    tip: "The island crosses the deck seam. Let the joined deck dry completely before attaching it.",
  },
  {
    title: "Build the bridge",
    short: "Bridge",
    part: 8,
    visible: 8,
    sheet: 5,
    intro: "The windowed bridge sits at the forward end of the island.",
    tasks: [
      "Cut and score part 8. Fold its walls down, and glue 8A–8D behind matching edges.",
      "Fold the base tabs inward and apply a little glue to their printed undersides.",
      "Centre the bridge over guide 8 on the island roof. It overhangs the island by 2 mm on each side.",
      "Keep guide 10 visible on top; that is where the radar mast will sit.",
    ],
    tip: "Leave the bridge overhang intact. Do not trim the walls to the narrower island underneath.",
  },
  {
    title: "Fit the funnel and radar mast",
    short: "Funnel & radar",
    part: 9,
    visible: 10,
    sheet: 5,
    intro: "Finish the carrier’s silhouette with the two small folded towers.",
    tasks: [
      "Cut and score funnel 9 and radar mast 10. Fold their walls down and glue each set of matching lettered tabs.",
      "Fold the base tabs inward; put glue on their printed undersides.",
      "Place funnel 9 on island roof guide 9, with its dark opening on top.",
      "Place mast 10 on bridge guide 10. Let the joins dry before moving the ship.",
    ],
    tip: "Tweezers help with the small tabs. Radar details are printed, so there are no fragile antenna pieces to cut.",
  },
  {
    title: "Your carrier is ready",
    short: "Final check",
    part: 0,
    visible: 10,
    sheet: 0,
    intro: "A miniature INS Vikramaditya, ready for a future paper air wing.",
    tasks: [
      "Check that the hull rests flat and the two runway halves form one continuous surface.",
      "Check the ski jump rises toward the bow and the island is on the starboard side.",
      "Allow the glue to dry fully. Lift the model from beneath the hull, rather than by its deck or radar mast.",
      "Keep the landing area clear. We’ll use the same approximately 1:700 scale for the aircraft added to this kit.",
    ],
    tip: "This first edition is a simplified prototype. The digital nets are checked, but a physical test build is still needed.",
  },
];
