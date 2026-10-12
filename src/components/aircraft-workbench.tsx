"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import models from "@/data/aircraft.json";

const pdf = "/kits/aircraft/aircraft-a4.pdf";
type Part = (typeof models)[number]["parts"][number];
const guides = { mig: models[0].steps, hind: models[1].steps };

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
          stroke={
            part.faces.some(
              (f) =>
                f.fill === "#ece7f5" &&
                JSON.stringify(f.points.slice(0, 2)) === JSON.stringify([a, b]),
            )
              ? "#315eea"
              : "#98a6ad"
          }
          strokeWidth=".12"
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
  camera,
}: {
  model: (typeof models)[number];
  exploded: boolean;
  highlight: string[];
  visible?: string[];
  camera: "iso" | "top" | "side";
}) {
  const eye =
    camera === "top"
      ? [0, 0, 1]
      : camera === "side"
        ? [0, -1, 0]
        : [40, -56, 31];
  const project = ([x, y, z]: number[]) =>
    camera === "top"
      ? [300 + (x - 22) * 8, 165 + y * 8]
      : camera === "side"
        ? [300 + (x - 22) * 8, 230 - z * 14]
        : [300 + (x - 22) * 7 + y * 5, 230 + (x - 22) * 2 - y * 3 - z * 8];
  const depth = (pts: number[][]) =>
    pts.reduce((sum, p) => sum + p.reduce((d, v, i) => d + v * eye[i], 0), 0) /
    pts.length;
  const faces = model.parts
    .filter((p) => !visible || visible.includes(p.id))
    .flatMap((p) =>
      p.mesh.map((f) => ({
        ...f,
        id: p.id,
        points: f.points.map(([x, y, z]) => [
          x,
          y,
          z +
            (exploded
              ? p.id.startsWith("C")
                ? 6
                : p.id === "H15"
                  ? 7
                  : (model.parts.indexOf(p) % 3) * 1.6
              : 0),
        ]),
      })),
    )
    .filter((f) => {
      if (!f.cull) return true;
      const [a, b, c] = f.points;
      const u = b.map((v, i) => v - a[i]),
        v = c.map((v, i) => v - a[i]);
      const n = [
        u[1] * v[2] - u[2] * v[1],
        u[2] * v[0] - u[0] * v[2],
        u[0] * v[1] - u[1] * v[0],
      ];
      return n.reduce((d, v, i) => d + v * eye[i], 0) > 0;
    })
    .sort((a, b) => depth(a.points) - depth(b.points));
  return (
    <svg
      className="aircraft-drawing"
      viewBox={
        camera === "top"
          ? "0 -30 600 390"
          : camera === "side"
            ? "70 30 460 270"
            : "70 0 460 340"
      }
      role="img"
      aria-label={`${model.name}, ${camera} view, ${exploded ? "exploded" : "assembled"}; faceted paper geometry`}
    >
      {camera === "iso" && (
        <ellipse
          cx="300"
          cy="290"
          rx="175"
          ry="24"
          fill="#e4eaf0"
          opacity=".6"
        />
      )}
      {faces.map((f, i) => (
        <polygon
          key={i}
          points={f.points.map((p) => project(p).join(",")).join(" ")}
          fill={highlight.includes(f.id) && !f.detail ? "#9ab6fb" : f.fill}
          stroke={highlight.includes(f.id) ? "#315eea" : "#84959c"}
          strokeWidth={f.detail ? 0 : 0.3}
          strokeLinejoin="round"
        />
      ))}
    </svg>
  );
}

export default function AircraftWorkbench() {
  const [selected, setSelected] = useState(0);
  const [sheet, setSheet] = useState(1);
  const [camera, setCamera] = useState<"iso" | "top" | "side">("iso");
  const [mode, setMode] = useState<"model" | "guide" | "print">("model");
  const [exploded, setExploded] = useState(false);
  const [step, setStep] = useState(0);
  const model = models[selected];
  const instructions = guides[model.id as keyof typeof guides];
  const current = instructions[step];
  function select(index: number) {
    setSelected(index);
    setSheet(models[index].sheets[0]);
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
            <span>4 A4 sheets · 160 cut pieces</span>
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
                {mode === "print" ? `Sheet ${sheet} of 4` : model.name}
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
                src={`/kits/aircraft/sheet-${sheet}.svg`}
                width={891}
                height={630}
                alt={`A4 sheet ${sheet} with two ${model.name} models`}
                unoptimized
              />
            ) : (
              <Aircraft
                model={model}
                camera={camera}
                exploded={exploded}
                highlight={mode === "guide" ? current.ids : []}
                visible={
                  mode === "guide" && step > 0 && step < instructions.length - 1
                    ? instructions.slice(1, step + 1).flatMap((s) => s.ids)
                    : undefined
                }
              />
            )}
            {mode === "print" && (
              <nav
                className="sheet-pagination"
                aria-label="Aircraft print pages"
              >
                {model.sheets.map((n) => (
                  <button
                    key={n}
                    aria-current={sheet === n ? "page" : undefined}
                    onClick={() => setSheet(n)}
                  >
                    Sheet {n}
                  </button>
                ))}
              </nav>
            )}
            <div className="stage-footer">
              {mode === "print" ? (
                <span>
                  One sheet makes 2{" "}
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
                  {(
                    [
                      ["iso", "Perspective"],
                      ["top", "Top"],
                      ["side", "Side"],
                    ] as const
                  ).map(([id, label]) => (
                    <button
                      key={id}
                      aria-pressed={camera === id}
                      onClick={() => setCamera(id)}
                    >
                      {label}
                    </button>
                  ))}
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
                  ? "A small fleet. Four sheets."
                  : model.name}
            </h2>
            <p>
              {mode === "guide"
                ? current.text
                : mode === "print"
                  ? "The PDF includes six 20-piece fighters and two 20-piece helicopters. Print only the page you need, or all four to make the full display pack."
                  : selected === 0
                    ? "A tapered fuselage, rounded canopy, separate swept wings and stabilizers, canted fins and open engine pods. Twenty pieces replace the earlier flat-sided approximation."
                    : "A stepped tandem cockpit flows into a fuller cabin, then a narrow rising tail boom. Drooping stub wings and a swept tail fin complete the revised 20-piece silhouette."}
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
              100–120 gsm paper · Print at 100%. These are detailed paper
              miniatures; physical assembly has not yet been tested. Trial-build
              one before making the fleet.
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
              Enlarged patterns · outline = cut · grey dashes = facets · blue
              dashes = tabs
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
            Shape references:{" "}
            <a
              href="https://commons.wikimedia.org/wiki/File:Mil_Mi-24_1-view_line_drawing.svg"
              target="_blank"
              rel="noreferrer"
            >
              US Army Hind recognition profile ↗
            </a>{" "}
            ·{" "}
            <a
              href="https://commons.wikimedia.org/wiki/File:A_MiG-29K_performs_a_touch_and_go_landing_on_INS_Vikramaditya_during_Narendra_Modi%27s_visit.jpg"
              target="_blank"
              rel="noreferrer"
            >
              Indian Navy MiG-29K photograph ↗
            </a>
            . Cross-sections are inferred modelling choices; these are not
            verified production blueprints.
          </p>
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
