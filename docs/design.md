# Paper Craft / INS Vikramaditya

A practical shipyard workbench: a large paper model on the left, the current task on the right. Navigation switches between the assembled model, an assembly guide, and actual printable sheets. Content is left aligned; the ship is centered on its work surface.

Palette: paper #ffffff, workbench #f3f6f9, ink #202c3f, muted #68778b, fold blue #315eea, glue lavender #eeebf7. Avenir Next/system sans for the interface; Georgia for the vessel name. The model and its usable paper pieces provide the identity. No stock imagery, simulated controls, or invented build-time claims.

The physical kit controls the illustration. Version 0.3 has 24 cut pieces on 13 A4 landscape sheets. Four 177.5 mm hull trays meet at full-height end walls; four deck panels butt together over three 20 mm-wide joining strips. Four internal transverse supports brace the deck between those seams. Overall dimensions are 710 x 150 mm, approximately 1:400 using the official 284 m length and approximately 60 m maximum beam. Individual shapes remain simplified; the larger scale does not establish greater historical accuracy. Small fittings, the underwater hull, and weapons are omitted.

The 14-degree straight ramp substitutes for the curved ski jump. The island occupies the starboard side, with the windowed bridge forward of the funnel. A gallery projects 7 mm beyond either side of the island. The bridge sits on it with a 3.5 mm perimeter rim. The foremast carries a 31.5 x 28 mm platform and a single folded radar screen; a separate aft tower sits behind the island. These are buildable approximations, not surveyed ship dimensions. Future aircraft should use the same nominal scale. No aircraft are included yet.

The Anatomy projection and solid tools, restrained shading, and object-first composition are used. Physical buildability supersedes the skill's decorative part counts, mechanical detail, and idle motion. Views change only on user action. A physical build cannot have details absent from its paper patterns.

Validation includes exact A4 page dimensions, printable bounds, face/tab intersections, separate-piece bounds, matching hull/deck seams, overall scale, and ramp angle. Page PNGs and desktop browser captures are inspected. The app is desktop-only, with a minimum workspace width of 1100 px and a persistent two-column layout. Real assembly remains unverified: paper thickness, glue and seam stiffness need a physical prototype.

References:

- https://www.pib.gov.in/newsite/PrintRelease.aspx?lang=3&reg=3&relid=100633
- https://commons.wikimedia.org/wiki/File:INS_Vikramaditya_with_full_air_asset_loadout.jpg
- https://github.com/wheresryan22/anatomy (MIT; vendored license preserved)

## Version 0.2 (previous 1:700 edition)

Four new cut pieces, six sheets, eleven assembly steps. A close-up view reveals shared deck tie-downs, edge lights, lift outlines, hull portholes and access panels, windows, vents, ladders, and radar grids. `scripts/surface_art.py` generates the same millimetre artwork used by PDF and SVG. Geometry checks include mounting elevations, supported footprints, and intentional overhangs. The progress storage key includes the kit version.

## Version 0.3 (selected 1:400 edition)

The user chose a 71 cm model on 12 October 2026. Physical geometry is stored at 1:400, while artwork uses a stable 1:700 illustration coordinate system and is transformed into millimetres by the generator. Hull/deck segmentation and guide visibility come from shared part groups, rather than assuming that part number implies assembly order. Twelve steps cover all 24 pieces. The four 42 mm-high support webs have folded BASE and DECK tabs. They are construction supports, not representations of the real ship's interior.

The first four sheets use compact headers to accommodate complete tray nets within a 10 mm cut margin; later pages use the standard header. Every page retains the unscaled 50 mm calibration line. PDF generation is deterministic. Exact paper thickness, stiffness and glue tolerances remain unverified.

## Next session

The current desktop prototype is the baseline. The next iteration should deepen the INS Vikramaditya model further while keeping every visible feature physically printable and buildable. Explore a more faithful hull and flight-deck outline, layered island structures, deck-edge structures, radar and antenna assemblies, and finer printed surface details. Add aircraft at a compatible scale after the carrier details are established. Keep printable nets, part numbers, assembly instructions, and the on-screen model synchronized. User preference: desktop only.
