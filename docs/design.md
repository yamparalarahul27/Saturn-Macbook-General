# Paper Craft / INS Vikramaditya

A practical shipyard workbench: a large paper model on the left, the current task on the right. Navigation switches between the assembled model, an assembly guide, and actual printable sheets. Content is left aligned; the ship is centered on its work surface.

Palette: paper #ffffff, workbench #f3f6f9, ink #202c3f, muted #68778b, fold blue #315eea, glue lavender #eeebf7. Avenir Next/system sans for the interface; Georgia for the vessel name. The model and its usable paper pieces provide the identity. No stock imagery, simulated controls, or invented build-time claims.

The physical kit controls the illustration. Fourteen pieces, six A4 landscape sheets. Aft and forward hulls meet at full-height bulkheads; deck halves meet edge-to-edge over a 20 mm joining strip. Overall dimensions are 405.714 x 85.714 mm, approximately 1:700 using the official 284 m length and approximately 60 m maximum beam. Other shapes are simplified for paper construction. Small fittings, the underwater hull, and weapons are omitted.

The 14-degree straight ramp substitutes for the curved ski jump. The island occupies the starboard side, with the windowed bridge forward of the funnel. A gallery projects 4 mm beyond either side of the island. The bridge sits on it with a 2 mm perimeter rim. The foremast carries an 18 x 16 mm platform and a single folded radar screen; a separate aft tower sits behind the island. These are buildable approximations, not surveyed ship dimensions. Future aircraft should use the same nominal scale. No aircraft are included yet.

The Anatomy projection and solid tools, restrained shading, and object-first composition are used. Physical buildability supersedes the skill's decorative part counts, mechanical detail, and idle motion. Views change only on user action. A physical build cannot have details absent from its paper patterns.

Validation includes exact A4 page dimensions, printable bounds, face/tab intersections, separate-piece bounds, matching hull/deck seams, overall scale, and ramp angle. Page PNGs and desktop browser captures are inspected. The app is desktop-only, with a minimum workspace width of 1100 px and a persistent two-column layout. Real assembly remains unverified: paper thickness, glue and seam stiffness need a physical prototype.

References:

- https://www.pib.gov.in/newsite/PrintRelease.aspx?lang=3&reg=3&relid=100633
- https://commons.wikimedia.org/wiki/File:INS_Vikramaditya_with_full_air_asset_loadout.jpg
- https://github.com/wheresryan22/anatomy (MIT; vendored license preserved)

## Version 0.2

Four new cut pieces, six sheets, eleven assembly steps. A close-up view reveals shared deck tie-downs, edge lights, lift outlines, hull portholes and access panels, windows, vents, ladders, and radar grids. `scripts/surface_art.py` generates the same millimetre artwork used by PDF and SVG. Geometry checks include mounting elevations, supported footprints, and intentional overhangs. The progress storage key includes the kit version.

## Next session

The current desktop prototype is the baseline. The next iteration should deepen the INS Vikramaditya model further while keeping every visible feature physically printable and buildable. Explore a more faithful hull and flight-deck outline, layered island structures, deck-edge structures, radar and antenna assemblies, and finer printed surface details. Add aircraft at a compatible scale after the carrier details are established. Keep printable nets, part numbers, assembly instructions, and the on-screen model synchronized. User preference: desktop only.
