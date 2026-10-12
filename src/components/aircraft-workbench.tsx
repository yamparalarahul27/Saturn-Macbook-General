"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import models from "@/data/aircraft.json";

const pdf = "/kits/aircraft/aircraft-a4.pdf";
type Part = (typeof models)[number]["parts"][number];
const guides = {
  mig: [
    {
      title: "Prepare one fighter",
      ids: ["M1", "M2", "M3", "M4", "M5", "M6", "M7"],
      text: "Print page 1 at 100% on 160–200 gsm card. Check the 50 mm ruler. Start with one of the six numbered sets. Score blue dashed lines with a blunt tool before cutting; the blue lines on M1 are placement guides, not folds.",
    },
    {
      title: "Cut the wing and tailplane",
      ids: ["M1"],
      text: "Cut around the complete M1 silhouette, keeping the nose, both wings and the rear tailplanes connected. Leave this piece flat, printed side up. Its nose-to-tail length is 43.25 mm.",
    },
    {
      title: "Fold the fuselage",
      ids: ["M2"],
      text: "Cut M2 as one connected piece. Fold both long dashed hinges down 90° from the narrow roof, with the printed sides facing out. This makes an open-bottom body. Apply a fine bead of glue to its lower edges between the front and rear ends of the roof. Seat these edges on the two central dashed rails on M1, with both noses pointing the same way. Hold upright until set; leave the underside and ends open.",
    },
    {
      title: "Fold the twin engine housings",
      ids: ["M5", "M6"],
      text: "Cut M5 and M6 around their outside outlines. Score the four edges of each long central roof, then fold both side panels and both dark end panels down 90°. Each piece forms an open-bottom housing, 1.5 mm high. Glue the lower edges onto the outer blue rails of M1, with the dark exhaust ends flush with the aircraft tail. M5 goes on the left and M6 on the right when viewed from behind. Do not cut the fine printed nozzle bands or roof markings.",
    },
    {
      title: "Raise the cockpit canopy",
      ids: ["M7"],
      text: "Fold all four panels down from M7’s blue-glazed roof to make a 1.1 mm-high open-bottom cap. The smaller glazed panel faces the nose. Glue its lower edges to M2’s narrow roof: the canopy begins exactly at the front of that roof, 8 mm behind the nose, centred across it. Keep the pale canopy frames intact; they are printed detail, not cuts.",
    },
    {
      title: "Stand up the twin fins",
      ids: ["M3", "M4"],
      text: "Fold each lilac foot 90° from its fin. Place M3 on the left engine-roof guide and M4 on the right engine-roof guide, looking from the tail toward the nose. Glue the feet flat onto M5 and M6 respectively, pointing outward toward their nearest wingtip, away from the fuselage; the fins stand vertically. Their sloping leading edges point forward. The striped fins are single-layer, with white backs.",
    },
    {
      title: "Park on the carrier",
      ids: ["M1", "M2", "M3", "M4", "M5", "M6", "M7"],
      text: "Let the first fighter dry and check its silhouette before making the other five. This miniature rests on its flat underside, with landing gear omitted. Place it loose on the 71 cm carrier first so you can adjust your deck arrangement. The wings remain spread in this first edition.",
    },
  ],
  hind: [
    {
      title: "Prepare one helicopter",
      ids: ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9"],
      text: "Print page 2 at 100% on 160–200 gsm card. Check the 50 mm ruler. Cut only one nine-piece set first. Keep the long rotor blades supported on your cutting mat as you cut. The Mi-24 is a custom display addition, not part of Vikramaditya’s normal air group.",
    },
    {
      title: "Shape the tandem-cockpit body",
      ids: ["H1"],
      text: "Cut H1 as one connected piece. Fold the two straight roof hinges down 90°, leaving the 3 mm roof between them flat. Both printed cockpit sides face out. Keep the body open underneath; do not glue the two sides together. The roof holds them parallel, 3 mm apart. Rest the lower cabin edges on the table while the folds settle.",
    },
    {
      title: "Attach the stub wings",
      ids: ["H2", "H3"],
      text: "Fold each lilac root tab up 90°. Glue the tab of H2 to the left side of H1 and H3 to the right, viewed from the tail toward the nose. Use the marked wing-root guides on the body: the long straight root runs from 14 to 20 mm behind the nose, 5 mm below the roof. The printed wings face up and project horizontally outward; keep both at the same height.",
    },
    {
      title: "Add the tailplane",
      ids: ["H4"],
      text: "Keep H4 flat, printed side up. Centre it across the underside of the tail boom at the small lower-tail guide, 35 mm behind the nose. Glue its central 3 mm band to the bottom edges of the boom. The long span runs across the helicopter and the 4 mm chord runs nose to tail.",
    },
    {
      title: "Fit the twin engine covers",
      ids: ["H8", "H9"],
      text: "Score the four edges of each cover’s central vented roof. Fold the two sides and two dark end panels down 90° to make an open-bottom cap. Glue H8 and H9 onto the fuselage roof side by side, starting 8 mm behind the nose. Leave 0.4 mm between them and a small gap before the rotor-mast guide. The intake ends face forward. The vent stripes are printed; do not cut them out.",
    },
    {
      title: "Build the rotor mast",
      ids: ["H6"],
      text: "Score the four hinges around H6’s central square. Fold all four sides down 90° to form a tiny open-bottom cap. Apply glue to its four lower edges and place it on the square roof guide on H1. Keep the 2 mm top square level and let it dry before adding the rotor.",
    },
    {
      title: "Fit both rotors",
      ids: ["H5", "H7"],
      text: "Leave the five-blade H5 flat. Glue only its central hub to the top of H6; do not bend the blades. The rotor’s swept diameter is 43.25 mm. Glue the centre of the smaller three-blade H7 to the right side of the tail at the small upper-tail guide. Both rotors are fixed paper details, not moving mechanisms.",
    },
    {
      title: "Check the finished silhouette",
      ids: ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9"],
      text: "Check that the main rotor is level, both stub wings match, and the tail rotor clears the tailplane. Let everything dry before lifting by the body. This simplified model rests on its lower cabin edges; landing gear is omitted. Build the second copy once the first fits, then choose its place in your custom display.",
    },
  ],
};

function Pattern({ part }: { part: Part }) {
  const points = part.faces.flatMap((f) => f.points);
  const xs = points.map((p) => p[0]),
    ys = points.map((p) => p[1]);
  const x = Math.min(...xs) - 2,
    y = Math.min(...ys) - 2;
  return (
    <svg
      viewBox={`${x} ${y} ${Math.max(...xs) - x + 2} ${Math.max(...ys) - y + 2}`}
      role="img"
      aria-label={`${part.id}: ${part.name} cutting pattern`}
    >
      {part.faces.map((f, i) => (
        <polygon
          key={i}
          points={f.points.map((p) => p.join(",")).join(" ")}
          fill={f.fill}
        />
      ))}
      {part.faces.flatMap((f, i) =>
        f.points.map((a, j) => {
          const b = f.points[(j + 1) % f.points.length];
          if (
            part.folds.some(
              ([u, v]) =>
                (a.toString() === u.toString() &&
                  b.toString() === v.toString()) ||
                (a.toString() === v.toString() &&
                  b.toString() === u.toString()),
            )
          )
            return null;
          return (
            <line
              key={`${i}-${j}`}
              x1={a[0]}
              y1={a[1]}
              x2={b[0]}
              y2={b[1]}
              stroke="#334155"
              strokeWidth=".16"
            />
          );
        }),
      )}
      {part.folds.map(([a, b], i) => (
        <line
          key={i}
          x1={a[0]}
          y1={a[1]}
          x2={b[0]}
          y2={b[1]}
          stroke="#315eea"
          strokeWidth=".16"
          strokeDasharray=".8 .55"
        />
      ))}
      {part.art.map((f, i) => (
        <polygon
          key={`art${i}`}
          points={f.points.map((p) => p.join(",")).join(" ")}
          fill={f.fill}
        />
      ))}
    </svg>
  );
}

function Aircraft({
  model,
  exploded,
  highlight,
  visible,
}: {
  model: (typeof models)[number];
  exploded: boolean;
  highlight: string[];
  visible?: string[];
}) {
  const project = ([x, y, z]: number[]) => [
    300 + (x - 22) * 7 + y * 5,
    230 + (x - 22) * 2 - y * 3 - z * 8,
  ];
  const order: Record<string, number> = {
    M1: 0,
    M2: 10,
    M3: 20,
    M4: 8,
    M5: 15,
    M6: 6,
    M7: 25,
    H4: 0,
    H3: 5,
    H1: 10,
    H2: 20,
    H6: 30,
    H8: 26,
    H9: 25,
    H5: 40,
    H7: 50,
  };
  const faces = model.parts
    .filter((p) => !visible || visible.includes(p.id))
    .flatMap((p) =>
      p.mesh.map((f, j) => ({
        ...f,
        id: p.id,
        layer: order[p.id],
        index: j,
        points: f.points.map(([x, y, z]) => [
          x,
          y,
          z +
            (exploded
              ? model.parts.findIndex((part) => part.id === p.id) * 2
              : 0),
        ]),
      })),
    )
    .filter(
      (f) => !(["M2", "H1"].includes(f.id) && f.points.every((p) => p[1] > 0)),
    )
    .sort((a, b) => a.layer - b.layer || a.index - b.index);
  return (
    <svg
      className="aircraft-drawing"
      viewBox={exploded ? "70 -70 460 420" : "70 55 460 285"}
      role="img"
      aria-label={`${model.name}, ${exploded ? "parts separated vertically" : "assembled"}; enlarged illustration`}
    >
      <ellipse cx="300" cy="290" rx="175" ry="24" fill="#e4eaf0" opacity=".6" />
      {faces.map((f, i) => (
        <polygon
          key={i}
          points={f.points.map((p) => project(p).join(",")).join(" ")}
          fill={highlight.includes(f.id) && !f.detail ? "#9ab6fb" : f.fill}
          stroke={highlight.includes(f.id) ? "#315eea" : "#7a8d9b"}
          strokeWidth={f.detail ? 0 : 0.65}
          strokeLinejoin="round"
        />
      ))}
    </svg>
  );
}

export default function AircraftWorkbench() {
  const [selected, setSelected] = useState(0);
  const [mode, setMode] = useState<"model" | "guide" | "print">("model");
  const [exploded, setExploded] = useState(false);
  const [step, setStep] = useState(0);
  const model = models[selected];
  const instructions = guides[model.id as keyof typeof guides];
  const current = instructions[step];
  function select(index: number) {
    setSelected(index);
    setStep(0);
    setExploded(false);
  }
  return (
    <>
      <a className="skip-link" href="#aircraft-workspace">
        Skip to aircraft workspace
      </a>
      <header className="site-header">
        <Link href="/" className="brand">
          Paper Craft<span className="brand-period">.</span>
        </Link>
        <span className="header-note">A little paper. A whole new world.</span>
        <a className="header-download" href={pdf} download>
          Download aircraft pack ↓
        </a>
      </header>
      <main className="workbench" id="aircraft-workspace">
        <nav className="air-collection" aria-label="Model collection">
          <Link href="/">← INS Vikramaditya</Link>
          <span>Aircraft collection / 1:400</span>
        </nav>
        <section className="intro">
          <div>
            <div className="model-label">SMALL AIRCRAFT. A FULLER DECK.</div>
            <h1>Ready for the flight deck.</h1>
            <p>Two new builds, at the same scale as your 71 cm carrier.</p>
          </div>
          <div className="air-pack-note">
            6 fighters + 2 helicopters
            <br />
            <span>2 A4 sheets · 60 cut pieces</span>
          </div>
        </section>
        <div className="air-selector" aria-label="Choose an aircraft">
          {models.map((m, i) => (
            <button
              key={m.id}
              aria-pressed={selected === i}
              onClick={() => select(i)}
            >
              <span className="panel-eyebrow">
                0{i + 1} / {m.label}
              </span>
              <strong>{m.name}</strong>
              <span>{m.size}</span>
            </button>
          ))}
        </div>
        <div className="workspace-navigation">
          <div className="tabs" aria-label="Aircraft workspace">
            {(
              [
                ["model", "The model"],
                ["guide", "Assembly guide"],
                ["print", "Print sheets"],
              ] as const
            ).map(([id, label]) => (
              <button
                key={id}
                aria-pressed={mode === id}
                onClick={() => setMode(id)}
              >
                {label}
              </button>
            ))}
          </div>
          <span className="paper-spec">1:400 · Print at actual size</span>
        </div>
        <div className="air-workspace">
          <section className="air-stage" aria-label="Aircraft preview">
            <div className="stage-top">
              <span>
                {mode === "print" ? `Sheet ${selected + 1} of 2` : model.name}
              </span>
              <span>
                {mode === "print"
                  ? "A4 landscape"
                  : "Enlarged illustration · not print scale"}
              </span>
            </div>
            {mode === "print" ? (
              <Image
                className="air-sheet"
                src={`/kits/aircraft/sheet-${selected + 1}.svg`}
                width={891}
                height={630}
                alt={`A4 sheet with ${model.count} ${model.name} models`}
                unoptimized
              />
            ) : (
              <Aircraft
                model={model}
                exploded={exploded}
                highlight={mode === "guide" ? current.ids : []}
                visible={
                  mode === "guide" && step > 0 && step < instructions.length - 1
                    ? instructions.slice(1, step + 1).flatMap((s) => s.ids)
                    : undefined
                }
              />
            )}
            <div className="stage-footer">
              {mode === "print" ? (
                <span>
                  One sheet makes {model.count}{" "}
                  {selected === 0 ? "fighters" : "helicopters"}.
                </span>
              ) : (
                <div className="view-switch">
                  <button
                    aria-pressed={!exploded}
                    onClick={() => setExploded(false)}
                  >
                    Assembled
                  </button>
                  <button
                    aria-pressed={exploded}
                    onClick={() => setExploded(true)}
                  >
                    Exploded
                  </button>
                </div>
              )}
              <span className="scale-label">
                {model.parts.length} pieces per model
              </span>
            </div>
          </section>
          <aside className="air-panel" aria-live="polite">
            <span className="panel-eyebrow">
              {mode === "guide"
                ? `STEP ${step + 1} OF ${instructions.length}`
                : model.label}
            </span>
            <h2>
              {mode === "guide"
                ? current.title
                : mode === "print"
                  ? "A small fleet. Two sheets."
                  : model.name}
            </h2>
            <p>
              {mode === "guide"
                ? current.text
                : mode === "print"
                  ? "The PDF includes six seven-piece fighters and two nine-piece helicopters. Print only the page you need, or both to make the full display pack."
                  : selected === 0
                    ? "Twin engine housings, a raised framed canopy and striped fins, with panel lines, nozzle bands and wing roundels. Seven cut pieces build a small fighter with more depth."
                    : "A framed tandem cockpit, camouflage, cabin doors and windows, twin engine covers and marked rotor tips. Nine cut pieces build your custom display helicopter."}
            </p>
            {mode === "guide" ? (
              <div className="air-step-actions">
                <button
                  className="button secondary"
                  disabled={step === 0}
                  onClick={() => setStep(step - 1)}
                >
                  Previous
                </button>
                <button
                  className="button primary"
                  onClick={() =>
                    step === instructions.length - 1
                      ? setMode("model")
                      : setStep(step + 1)
                  }
                >
                  {step === instructions.length - 1
                    ? "Finish guide"
                    : "Next step →"}
                </button>
              </div>
            ) : (
              <>
                <dl className="spec-list">
                  <div>
                    <dt>Scale</dt>
                    <dd>1:400</dd>
                  </div>
                  <div>
                    <dt>Print quantity</dt>
                    <dd>{model.count} models</dd>
                  </div>
                  <div>
                    <dt>Construction</dt>
                    <dd>Cut, fold & glue</dd>
                  </div>
                </dl>
                <a className="button primary" href={pdf} download>
                  Download A4 aircraft pack ↓
                </a>
                <button
                  className="button secondary"
                  onClick={() => {
                    setStep(0);
                    setMode("guide");
                  }}
                >
                  Start building →
                </button>
              </>
            )}
            <p className="air-note">
              160–200 gsm card · Print at 100%. These are detailed paper
              miniatures; physical assembly has not yet been
              tested. Trial-build one before making the fleet.
            </p>
          </aside>
        </div>
        {mode === "guide" && (
          <nav className="air-steps" aria-label="Assembly steps">
            {instructions.map((s, i) => (
              <button
                key={s.title}
                aria-current={step === i ? "step" : undefined}
                onClick={() => setStep(i)}
              >
                {i + 1}. {s.title}
              </button>
            ))}
          </nav>
        )}
        <section className="air-parts">
          <div className="section-title">
            <h2>
              {mode === "guide"
                ? "Parts for this step"
                : "Every piece, before you cut."}
            </h2>
            <span>
              Enlarged patterns · outer outline = cut · dashed = fold · fine
              grey = detail
            </span>
          </div>
          <div className="air-parts-grid">
            {model.parts
              .filter((p) => mode !== "guide" || current.ids.includes(p.id))
              .map((p) => (
                <article key={p.id}>
                  <Pattern part={p} />
                  <strong>
                    {p.id} / {p.name}
                  </strong>
                </article>
              ))}
          </div>
        </section>
        <details className="air-sources">
          <summary>Scale references & construction notes</summary>
          <p>
            MiG-29K: nominal 17.3 m length and 11.99 m span. Mi-24: 17.5 m
            fuselage and 17.3 m rotor diameter. Small shapes, heights and joints
            are simplified for paper construction; these are original craft
            patterns, not aircraft blueprints. Rotor diameter is the swept
            circle, not the distance between two blade tips.
          </p>
          <p>
            <a
              href="https://www.pib.gov.in/newsite/erelcontent.aspx?lang=2&reg=48&relid=98416"
              target="_blank"
              rel="noreferrer"
            >
              MiG-29K carrier association: Government of India ↗
            </a>{" "}
            ·{" "}
            <a
              href="https://vertipedia.vtol.org/aircraft/getAircraft/aircraftID/478"
              target="_blank"
              rel="noreferrer"
            >
              Mi-24: Vertical Flight Society ↗
            </a>
          </p>
        </details>
      </main>
      <footer className="site-footer">
        <span>Made to leave the screen.</span>
        <Link href="/">Back to the 71 cm carrier →</Link>
      </footer>
    </>
  );
}
