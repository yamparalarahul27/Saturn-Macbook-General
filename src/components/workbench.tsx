"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useBuildProgress } from "@/lib/build-progress";
import { kit, kitUrl, ship, steps } from "@/lib/ship";
import { ShipModel, type ModelView } from "./ship-model";

function Icon({
  name,
  size = 20,
}: {
  name:
    | "download"
    | "arrow"
    | "check"
    | "print"
    | "paper"
    | "scissors"
    | "layers"
    | "ruler";
  size?: number;
}) {
  const paths = {
    download: (
      <>
        <path d="M12 3v12m-5-5 5 5 5-5" />
        <path d="M4 15v5h16v-5" />
      </>
    ),
    arrow: <path d="m9 5 7 7-7 7" />,
    check: <path d="m5 12 4 4L19 6" />,
    print: (
      <>
        <path d="M7 8V3h10v5M7 17H3V8h18v9h-4" />
        <path d="M7 14h10v7H7zM17 11h1" />
      </>
    ),
    paper: (
      <>
        <path d="m4 3 16 5-5 13-3-8-8-10Z" />
        <path d="m4 3 8 10 8-5M4 3v14l8-4" />
      </>
    ),
    scissors: (
      <>
        <circle cx="5" cy="6" r="3" />
        <circle cx="5" cy="18" r="3" />
        <path d="m7.5 7.5 13 12m-13-3 13-12" />
      </>
    ),
    layers: (
      <>
        <path d="m12 3 10 6-10 6L2 9l10-6Z" />
        <path d="m2 13 10 6 10-6M2 17l10 6 10-6" />
      </>
    ),
    ruler: (
      <>
        <path d="M3 7h18v10H3zM7 7v5m5-5v3m5-3v5" />
      </>
    ),
  };
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name]}
    </svg>
  );
}
const sheetNames = kit.sheetNames;
const pdf = `${kitUrl}/vikramaditya-a4.pdf`;

export default function Workbench() {
  const [tab, setTab] = useState<"overview" | "guide" | "sheets">("overview");
  const [view, setView] = useState<ModelView>("assembled");
  const { step, completed, update } = useBuildProgress();
  const setStep = (next: number) => update({ step: next });
  const [selected, setSelected] = useState(0);
  const [sheet, setSheet] = useState(1);
  const current = steps[step];
  const isGuide = tab === "guide";
  const activePart = isGuide ? current.part : selected;
  function openGuide() {
    setTab("guide");
    setView("assembled");
  }
  function complete() {
    update({
      completed: completed.includes(step) ? completed : [...completed, step],
      step: Math.min(step + 1, steps.length - 1),
    });
  }
  return (
    <>
      <a className="skip-link" href="#workbench">
        Skip to model workspace
      </a>
      <header className="site-header">
        <Link className="brand" href="/" aria-label="Paper Craft home">
          <span className="brand-mark">
            <Icon name="paper" size={25} />
          </span>
          Paper Craft<span className="brand-period">.</span>
        </Link>
        <div className="header-note">A little paper. A whole new world.</div>
        <a className="header-download" href={pdf} download>
          <Icon name="download" size={17} />
          <span>Get the template</span>
        </a>
      </header>
      <main id="workbench" className="workbench">
        <div className="breadcrumb">
          <span>The shipyard</span>
          <span>/</span>
          <span>Build 01</span>
        </div>
        <section className="intro" aria-labelledby="model-title">
          <div>
            <div className="model-label">
              <span className="naval-dot" />
              Indian Navy collection
            </div>
            <h1 id="model-title">
              INS <em>Vikramaditya</em>
            </h1>
            <p>
              A floating airfield, made by you. Print, fold, and bring it to
              life.
            </p>
          </div>
          <div className="edition">
            <span className="edition-number">R33</span>
            <span>
              Aircraft carrier
              <br />
              Paper edition {ship.version}
            </span>
          </div>
        </section>
        <div className="workspace-navigation">
          <div className="tabs" role="tablist" aria-label="Model workspace">
            {(
              [
                ["overview", "The model"],
                ["guide", "Assembly guide"],
                ["sheets", "Print sheets"],
              ] as const
            ).map(([id, label]) => (
              <button
                role="tab"
                tabIndex={tab === id ? 0 : -1}
                onKeyDown={(event) => {
                  const ids = ["overview", "guide", "sheets"] as const;
                  const index = ids.indexOf(id);
                  const next =
                    event.key === "ArrowRight"
                      ? (index + 1) % 3
                      : event.key === "ArrowLeft"
                        ? (index + 2) % 3
                        : event.key === "Home"
                          ? 0
                          : event.key === "End"
                            ? 2
                            : -1;
                  if (next < 0) return;
                  event.preventDefault();
                  setTab(ids[next]);
                  document.getElementById(`tab-${ids[next]}`)?.focus();
                }}
                aria-selected={tab === id}
                aria-controls="workspace-panel"
                id={`tab-${id}`}
                key={id}
                onClick={() => {
                  setTab(id);
                  if (id === "guide") setView("assembled");
                }}
              >
                {id === "overview" ? (
                  <Icon name="layers" size={17} />
                ) : id === "guide" ? (
                  <Icon name="scissors" size={17} />
                ) : (
                  <Icon name="print" size={17} />
                )}{" "}
                {label}
                {id === "sheets" && (
                  <span className="count">{ship.sheets}</span>
                )}
              </button>
            ))}
          </div>
          <span className="paper-spec">
            A4 paper <span /> Approx. 1:{kit.scale}
          </span>
        </div>
        <div
          id="workspace-panel"
          role="tabpanel"
          aria-labelledby={`tab-${tab}`}
        >
          {isGuide && (
            <nav className="step-strip" aria-label="Assembly steps">
              {steps.map((s, i) => (
                <button
                  key={s.short}
                  aria-current={step === i ? "step" : undefined}
                  onClick={() => setStep(i)}
                >
                  <span
                    className={
                      completed.includes(i) ? "step-number done" : "step-number"
                    }
                  >
                    {completed.includes(i) ? (
                      <Icon name="check" size={13} />
                    ) : (
                      i + 1
                    )}
                  </span>
                  <span>{s.short}</span>
                </button>
              ))}
            </nav>
          )}
          <div
            className={`workspace-grid ${tab === "sheets" ? "print-layout" : ""}`}
          >
            <section
              className="model-stage"
              aria-label={
                tab === "sheets"
                  ? "Printable sheet preview"
                  : "Paper ship preview"
              }
            >
              <div className="stage-header">
                <span className="figure-label">
                  {tab === "sheets"
                    ? `Sheet ${String(sheet).padStart(2, "0")}`
                    : isGuide
                      ? `Step ${String(step + 1).padStart(2, "0")}`
                      : "The finished build"}
                </span>
                <span className="stage-small">
                  {tab === "sheets"
                    ? "297 × 210 mm"
                    : activePart
                      ? ship.parts[activePart - 1].name
                      : "A simplified waterline model"}
                </span>
              </div>
              {tab === "sheets" ? (
                <div className="sheet-large">
                  <Image
                    src={`${kitUrl}/sheet-${sheet}.svg`}
                    width={1188}
                    height={840}
                    unoptimized
                    alt={`A4 cut and fold template, sheet ${sheet}: ${sheetNames[sheet - 1]}`}
                  />
                </div>
              ) : (
                <div className="model-art">
                  <ShipModel
                    view={view}
                    selected={activePart}
                    visible={isGuide ? current.visible : undefined}
                  />
                </div>
              )}
              <div className="stage-footer">
                {tab === "sheets" ? (
                  <div className="sheet-pagination">
                    {Array.from({ length: ship.sheets }, (_, i) => i + 1).map(
                      (n) => (
                        <button
                          key={n}
                          aria-label={`Preview sheet ${n}`}
                          aria-pressed={sheet === n}
                          onClick={() => setSheet(n)}
                        >
                          {n}
                        </button>
                      ),
                    )}
                  </div>
                ) : (
                  <div className="view-switch" aria-label="Model view">
                    {(
                      [
                        ["assembled", "Assembled"],
                        ["exploded", "Exploded"],
                        ["top", "Top view"],
                        ["detail", "Close-up"],
                      ] as const
                    ).map(([id, label]) => (
                      <button
                        key={id}
                        aria-pressed={view === id}
                        onClick={() => setView(id)}
                      >
                        {label}
                      </button>
                    ))}
                  </div>
                )}
                <span className="scale-label">
                  {tab === "sheets"
                    ? "Print the PDF at 100%"
                    : view === "detail"
                      ? "Island & radar detail"
                      : "71 cm from stern to bow"}
                </span>
              </div>
            </section>
            <aside className="task-panel">
              {tab === "overview" ? (
                <>
                  <div className="panel-eyebrow">The 71 cm edition</div>
                  <h2>
                    From flat sheets
                    <br />
                    to flight deck.
                  </h2>
                  <p className="panel-description">
                    Build a reinforced four-section hull, signature ski jump,
                    starboard island, and broad landing deck of India’s aircraft
                    carrier, with a layered bridge and separate radar assembly.
                  </p>
                  <dl className="spec-list">
                    <div>
                      <dt>Print pack</dt>
                      <dd>{ship.sheets} A4 sheets</dd>
                    </div>
                    <div>
                      <dt>Cut-out pieces</dt>
                      <dd>{ship.parts.length} pieces</dd>
                    </div>
                    <div>
                      <dt>Finished size</dt>
                      <dd>71 × 15 cm</dd>
                    </div>
                    <div>
                      <dt>Build style</dt>
                      <dd>Cut, fold & glue</dd>
                    </div>
                  </dl>
                  <a className="button primary" href={pdf} download>
                    <Icon name="download" size={18} />
                    Download A4 template
                  </a>
                  <button className="button secondary" onClick={openGuide}>
                    Start building <Icon name="arrow" size={16} />
                  </button>
                  <div className="print-hint">
                    <Icon name="print" size={17} />
                    <span>
                      Print single-sided, at actual size.
                      <br />
                      Use printer-compatible 200 gsm cardstock.
                    </span>
                  </div>
                </>
              ) : tab === "sheets" ? (
                <>
                  <div className="panel-eyebrow">
                    A little check before you cut
                  </div>
                  <h2>
                    Print it right.
                    <br />
                    Everything fits.
                  </h2>
                  <p className="panel-description">
                    Download the PDF for full-size patterns. The on-screen
                    previews are for reference.
                  </p>
                  <dl className="spec-list">
                    <div>
                      <dt>Paper</dt>
                      <dd>A4, landscape</dd>
                    </div>
                    <div>
                      <dt>Scale</dt>
                      <dd>100% / Actual size</dd>
                    </div>
                    <div>
                      <dt>Printing</dt>
                      <dd>Single-sided</dd>
                    </div>
                    <div>
                      <dt>Fit to page</dt>
                      <dd>Off</dd>
                    </div>
                  </dl>
                  <div className="ruler-check">
                    <Icon name="ruler" />
                    <div>
                      <strong>Measure the test line</strong>
                      <p>
                        The line at the bottom of each sheet must measure
                        exactly 50 mm.
                      </p>
                    </div>
                  </div>
                  <a className="button primary" href={pdf} download>
                    <Icon name="download" size={18} />
                    Download all {ship.sheets} sheets
                  </a>
                  <a
                    className="button secondary"
                    href={pdf}
                    target="_blank"
                    rel="noreferrer"
                  >
                    <Icon name="print" size={17} />
                    Open PDF to print
                  </a>
                </>
              ) : (
                <>
                  <div className="panel-eyebrow">
                    Step {step + 1} of {steps.length}
                    {current.sheets.length > 0 && (
                      <span>
                        Sheet{current.sheets.length > 1 ? "s" : ""}{" "}
                        {current.sheets.join(" & ")}
                      </span>
                    )}
                  </div>
                  <h2>{current.title}</h2>
                  <p className="panel-description">{current.intro}</p>
                  <ol className="instructions">
                    {current.tasks.map((task, i) => (
                      <li key={task}>
                        <span>{i + 1}</span>
                        <p>{task}</p>
                      </li>
                    ))}
                  </ol>
                  <div className="step-tip">{current.tip}</div>
                  {step === 0 && (
                    <a className="text-download" href={pdf} download>
                      <Icon name="download" size={16} />
                      Download the print pack
                    </a>
                  )}
                  <div className="step-actions">
                    <button
                      className="button back"
                      disabled={step === 0}
                      onClick={() => setStep(step - 1)}
                      aria-label="Previous step"
                    >
                      <span className="reverse-arrow">
                        <Icon name="arrow" size={16} />
                      </span>
                    </button>
                    <button className="button primary" onClick={complete}>
                      {step === steps.length - 1
                        ? completed.includes(step)
                          ? "Build completed"
                          : "Mark build complete"
                        : "Done, next step"}
                      <Icon
                        name={step === steps.length - 1 ? "check" : "arrow"}
                        size={16}
                      />
                    </button>
                  </div>
                  <p className="completion" role="status">
                    {completed.length} of {steps.length} steps completed ·
                    Progress saved on this device
                  </p>
                </>
              )}
            </aside>
          </div>
          {isGuide && current.part > 0 ? (
            <section className="guide-parts" aria-label="Pieces for this step">
              {current.parts.map((id) => {
                const part = ship.parts[id - 1];
                return (
                  <article className="part-help" key={id}>
                    <div className="part-preview">
                      <Image
                        src={`${kitUrl}/part-${id}.svg`}
                        width={500}
                        height={250}
                        unoptimized
                        alt={`Flat printable pattern for ${part.name}`}
                      />
                    </div>
                    <div>
                      <span className="panel-eyebrow">
                        Piece {String(id).padStart(2, "0")}
                      </span>
                      <h3>{part.name}</h3>
                      <button
                        className="text-button"
                        onClick={() => {
                          setSheet(part.sheet);
                          setTab("sheets");
                        }}
                      >
                        View sheet {part.sheet}
                        <Icon name="arrow" size={15} />
                      </button>
                    </div>
                  </article>
                );
              })}
            </section>
          ) : tab === "overview" ? (
            <section className="parts-section" aria-labelledby="parts-heading">
              <div className="section-title">
                <h3 id="parts-heading">A ship, piece by piece.</h3>
                <span>Select a part to find it on the model</span>
              </div>
              <div className="parts-grid">
                {[
                  { id: 1, title: "Four-section hull", sub: "Sheets 1–4" },
                  { id: 3, title: "Four-panel deck", sub: "Sheets 5–8" },
                  { id: 6, title: "Ski jump", sub: "Sheet 12" },
                  { id: 7, title: "The island", sub: "Sheet 9" },
                  { id: 8, title: "Bridge & gallery", sub: "Sheets 10 & 12" },
                  { id: 9, title: "Funnel", sub: "Sheet 10" },
                  { id: 10, title: "Foremast & radar", sub: "Sheets 11 & 12" },
                  { id: 14, title: "Aft signal tower", sub: "Sheet 11" },
                  {
                    id: 21,
                    title: "Internal supports",
                    sub: "Sheet 13 · See exploded view",
                  },
                ].map((part) => (
                  <button
                    className="part-card"
                    key={part.id}
                    aria-pressed={selected === part.id}
                    onClick={() => {
                      setSelected(selected === part.id ? 0 : part.id);
                      if (part.id === 21) setView("exploded");
                    }}
                  >
                    <span className="part-thumb">
                      <Image
                        src={`${kitUrl}/part-${part.id}.svg`}
                        width={200}
                        height={100}
                        style={{ width: "auto", height: "auto" }}
                        alt=""
                        unoptimized
                      />
                    </span>
                    <strong>{part.title}</strong>
                    <span>{part.sub}</span>
                  </button>
                ))}
              </div>
            </section>
          ) : null}
        </div>
        <section className="bench-notes">
          <div className="legend">
            <span>
              <i className="cut-line" />
              Cut
            </span>
            <span>
              <i className="fold-line" />
              Fold away
            </span>
            <span>
              <i className="glue-swatch" />
              Glue tab
            </span>
            <span>
              <i className="guide-line" />
              Placement guide
            </span>
          </div>
          <p>Next on deck: aircraft, at the same scale.</p>
        </section>
        <details className="build-notes">
          <summary>About this paper edition</summary>
          <p>
            This is an original, simplified paper interpretation of INS
            Vikramaditya, with overall dimensions at approximately 1:{kit.scale}
            . Small fittings, the underwater hull, and weapons are omitted. The
            ski jump uses a straight wedge for easier assembly. Aircraft are
            planned and are not included in this pack.
          </p>
          <p>
            Version {ship.version}: printable dimensions and joins have been
            checked digitally. A physical test build is still needed to confirm
            fit with real paper and glue.
          </p>
          <p>
            Reference:{" "}
            <a
              href="https://www.pib.gov.in/newsite/PrintRelease.aspx?lang=3&reg=3&relid=100633"
              target="_blank"
              rel="noreferrer"
            >
              Ministry of Defence’s commissioning report
            </a>
            . Illustration tools adapted from{" "}
            <a
              href="https://github.com/wheresryan22/anatomy"
              target="_blank"
              rel="noreferrer"
            >
              Anatomy
            </a>
            .
          </p>
        </details>
      </main>
      <footer className="site-footer">
        <span>
          <Icon name="paper" size={17} />
          Made to leave the screen.
        </span>
        <span>Paper Craft · Build something real.</span>
      </footer>
    </>
  );
}
