"use client";

import { useId } from "react";
import {
  extrude,
  fitProjection,
  iso,
  pathOf,
  sideMatrix,
  topMatrix,
  type Plane,
  type Point3,
  type Projection,
  towardViewer,
} from "@/lib/anatomy/iso-kit";
import { ship, splitOutline } from "@/lib/ship";

export type ModelView = "assembled" | "exploded" | "top";
function Solid({
  ring,
  z,
  h,
  p,
  selected,
  color = "#c3cdd7",
}: {
  ring: Plane[];
  z: number;
  h: number;
  p: Projection;
  selected?: boolean;
  color?: string;
}) {
  const art = extrude(ring, z, h, p, { convex: false });
  return (
    <g strokeLinejoin="round">
      <path d={art.fill} fill={selected ? "#c5d5ff" : color} />
      <path d={art.top} fill={selected ? "#e0e9ff" : "#e4e9ed"} />
      {art.shades.map((d, i) => (
        <path
          key={i}
          d={d}
          fill="#42556b"
          opacity={[0.27, 0.18, 0.1, 0.03][i]}
        />
      ))}
      <path
        d={art.outline + art.crease}
        fill="none"
        stroke={selected ? "#315eea" : "#8090a2"}
        strokeWidth={selected ? 1.6 : 0.75}
      />
    </g>
  );
}
function plane(x: number, y: number, w: number, d: number): Plane[] {
  return [
    [x, y],
    [x + w, y],
    [x + w, y + d],
    [x, y + d],
  ];
}

export function ShipModel({
  view,
  selected = 0,
  visible = 10,
}: {
  view: ModelView;
  selected?: number;
  visible?: number;
}) {
  const uid = useId().replaceAll(":", "");
  const exploded = view === "exploded";
  const height = exploded ? 176 : 86;
  const p = fitProjection(
    [
      [0, 0, 0],
      [ship.length, 0, 0],
      [ship.length, ship.beam, 0],
      [0, ship.beam, 0],
      [185, 15, height],
    ] as Point3[],
    880,
    470,
    { pad: 64, azimuth: 62, elevation: view === "top" ? 89 : 28 },
  );
  const offset = (id: number) =>
    exploded
      ? ({
          1: 0,
          2: 0,
          3: 25,
          4: 25,
          5: 13,
          6: 50,
          7: 55,
          8: 83,
          9: 83,
          10: 112,
        }[id] ?? 0)
      : 0;
  const highlight = (id: number) =>
    selected === id ||
    (selected === 1 && id === 2) ||
    (selected === 3 && [3, 4, 5].includes(id)) ||
    (selected === 9 && id === 10);
  const deckZ = 24 + offset(3);
  const deckPath = pathOf(
    ship.deck.outline.map(([x, y]) => iso([x, y, deckZ], p)),
    true,
  );
  const box = (id: number) => {
    const part = ship.parts[id - 1];
    const z = part.z + offset(id);
    return (
      <g key={id}>
        <Solid
          ring={plane(part.x, part.y, part.w, part.d)}
          z={z}
          h={part.h}
          p={p}
          selected={highlight(id)}
        />
        {[7, 8].includes(id) && (
          <g
            transform={sideMatrix(
              [part.x, part.y + part.d],
              z + part.h,
              p,
              "left",
            )}
            fill="#5e748c"
          >
            {Array.from({ length: Math.floor((part.w - 6) / 8) }, (_, i) => (
              <rect key={i} x={3 + i * 8} y={4} width={5} height={3} />
            ))}
          </g>
        )}
        {id === 8 && (
          <g
            transform={sideMatrix(
              [part.x + part.w, part.y + part.d],
              z + part.h,
              p,
              "right",
            )}
            fill="#5e748c"
          >
            {[0, 1, 2].map((i) => (
              <rect key={i} x={3 + i * 6} y={4} width={4} height={3} />
            ))}
          </g>
        )}
        {id === 9 && (
          <>
            <g transform={topMatrix([part.x + 2, part.y + 2], z + part.h, p)}>
              <rect width={part.w - 4} height={part.d - 4} fill="#73818d" />
            </g>
            <g
              transform={sideMatrix(
                [part.x, part.y + part.d],
                z + part.h,
                p,
                "left",
              )}
            >
              <text
                x={part.w / 2}
                y={12}
                textAnchor="middle"
                fill="#f5f7f9"
                fontSize={5}
                fontWeight={600}
              >
                R33
              </text>
            </g>
          </>
        )}
        {id === 10 && (
          <g
            transform={sideMatrix(
              [part.x, part.y + part.d],
              z + part.h,
              p,
              "left",
            )}
          >
            <rect
              x={1}
              y={5}
              width={8}
              height={10}
              fill="#a3b2c3"
              stroke="#70839a"
              strokeWidth={0.2}
            />
            {[2, 4, 6, 8].map((n) => (
              <path
                key={n}
                d={`M1 ${5 + n}h8`}
                fill="none"
                stroke="#70839a"
                strokeWidth={0.2}
              />
            ))}
            {[2, 4, 6].map((n) => (
              <path
                key={n}
                d={`M${1 + n} 5v10`}
                fill="none"
                stroke="#70839a"
                strokeWidth={0.2}
              />
            ))}
          </g>
        )}
      </g>
    );
  };
  const ramp = ship.ramp;
  const rz = ramp.z + offset(6);
  const rp = (coords: Point3[]) =>
    pathOf(
      coords.map((pt) => iso(pt, p)),
      true,
    );
  return (
    <svg
      className="ship-svg"
      viewBox="0 0 880 470"
      role="img"
      aria-label={`${exploded ? "Exploded" : view === "top" ? "Top" : "Assembled"} view of the printable INS Vikramaditya carrier${selected ? `, highlighting ${ship.parts[selected - 1].name}` : ""}`}
    >
      <defs>
        <filter
          id={`${uid}-shadow`}
          x="-40%"
          y="-100%"
          width="180%"
          height="300%"
        >
          <feGaussianBlur stdDeviation="11" />
        </filter>
        <clipPath id={`${uid}-deck`}>
          <path d={deckPath} />
        </clipPath>
      </defs>
      <path
        d={pathOf(
          ship.deck.outline.map(([x, y]) => iso([x, y, -9], p)),
          true,
        )}
        fill="#7a8a9b"
        opacity=".12"
        filter={`url(#${uid}-shadow)`}
      />
      {[1, 2]
        .filter((id) => id <= visible)
        .map((id) => {
          const ring = splitOutline(ship.hull.outline, id === 2);
          if (visible > 2 && !exploded)
            return (
              <Solid
                key={id}
                ring={ring}
                z={0}
                h={24}
                p={p}
                selected={highlight(id)}
                color="#b6c2ce"
              />
            );
          const [vx, vy] = towardViewer(p);
          const sides = ring.map((a, i) => {
            const b = ring[(i + 1) % ring.length];
            const front = (b[1] - a[1]) * vx - (b[0] - a[0]) * vy > 0;
            return {
              front,
              d: pathOf(
                [
                  iso([a[0], a[1], 0], p),
                  iso([b[0], b[1], 0], p),
                  iso([b[0], b[1], 24], p),
                  iso([a[0], a[1], 24], p),
                ],
                true,
              ),
            };
          });
          return (
            <g
              key={id}
              stroke={highlight(id) ? "#315eea" : "#8090a2"}
              strokeWidth=".75"
            >
              {sides
                .filter((s) => !s.front)
                .map((s, i) => (
                  <path
                    key={i}
                    d={s.d}
                    fill={highlight(id) ? "#d2dfff" : "#e2e7ed"}
                  />
                ))}
              <path
                d={pathOf(
                  ring.map(([x, y]) => iso([x, y, 0], p)),
                  true,
                )}
                fill="#c3cdd7"
              />
              {sides
                .filter((s) => s.front)
                .map((s, i) => (
                  <path
                    key={i}
                    d={s.d}
                    fill={highlight(id) ? "#b7cafa" : "#b6c2ce"}
                  />
                ))}
            </g>
          );
        })}
      {visible >= 3 && (
        <>
          {exploded && (
            <Solid
              ring={plane(192.857, 8, 20, 70)}
              z={23.8 + offset(5)}
              h={0.2}
              p={p}
              selected={highlight(5)}
            />
          )}
          {[3, 4].map((id) => (
            <Solid
              key={id}
              ring={splitOutline(ship.deck.outline, id === 4)}
              z={deckZ}
              h={0.4}
              p={p}
              selected={highlight(id)}
            />
          ))}
          <g clipPath={`url(#${uid}-deck)`}>
            <g transform={topMatrix([0, 0], deckZ + 0.4, p)} fill="none">
              {[30, 57].map((y) => (
                <path
                  key={y}
                  d={`M3 ${y}L245 ${y + 12}`}
                  stroke="white"
                  strokeWidth=".85"
                />
              ))}
              <path
                d="M3 43.5L245 55.5"
                stroke="white"
                strokeWidth=".5"
                strokeDasharray="5 3"
              />
              <path
                d="M82 54L335 36L403 36"
                stroke="#b9a464"
                strokeWidth="1"
                strokeDasharray="3 2"
              />
              {[48, 64, 80].map((x) => (
                <path
                  key={x}
                  d={`M${x} ${31 + x * 0.044}V${58 + x * 0.044}`}
                  stroke="#8593a2"
                  strokeWidth=".45"
                />
              ))}
              {[15, 100, 150, 280, 310].map((x) => (
                <path
                  key={x}
                  d={`M${x} 19V13h18`}
                  stroke="#b48572"
                  strokeWidth=".4"
                />
              ))}
              {[105, 156].map((x) => (
                <rect
                  key={x}
                  x={x}
                  y={x === 105 ? 9 : 7}
                  width={17}
                  height={15}
                  stroke="#9eabb8"
                  strokeWidth=".4"
                />
              ))}
              <text
                x={36}
                y={19}
                fill="#8997a5"
                fontSize={4}
                textAnchor="middle"
              >
                R33
              </text>
              {visible < 7 && (
                <rect
                  x={175}
                  y={8}
                  width={85}
                  height={18}
                  stroke="#315eea"
                  strokeWidth=".5"
                  strokeDasharray="1 2"
                />
              )}
            </g>
          </g>
        </>
      )}
      {visible >= 6 && (
        <g
          stroke={highlight(6) ? "#315eea" : "#8c9cad"}
          strokeWidth={highlight(6) ? 1.6 : 0.75}
          strokeLinejoin="round"
        >
          <path
            d={rp([
              [ramp.x, ramp.y + ramp.d, rz],
              [ramp.x + ramp.w, ramp.y + ramp.d, rz],
              [ramp.x + ramp.w, ramp.y + ramp.d, rz + ramp.h],
            ])}
            fill={highlight(6) ? "#b9cafa" : "#b7c3cf"}
          />
          <path
            d={rp([
              [ramp.x + ramp.w, ramp.y, rz],
              [ramp.x + ramp.w, ramp.y + ramp.d, rz],
              [ramp.x + ramp.w, ramp.y + ramp.d, rz + ramp.h],
              [ramp.x + ramp.w, ramp.y, rz + ramp.h],
            ])}
            fill="#b0bdca"
          />
          <path
            d={rp([
              [ramp.x, ramp.y, rz],
              [ramp.x + ramp.w, ramp.y, rz + ramp.h],
              [ramp.x + ramp.w, ramp.y + ramp.d, rz + ramp.h],
              [ramp.x, ramp.y + ramp.d, rz],
            ])}
            fill={highlight(6) ? "#d2dfff" : "#e0e6ec"}
          />
          <path
            d={pathOf([
              iso([ramp.x, 36, rz], p),
              iso([ramp.x + ramp.w, 36, rz + ramp.h], p),
            ])}
            stroke="#b9a464"
            strokeWidth="1.4"
            strokeDasharray="5 3"
          />
        </g>
      )}
      {visible >= 7 && box(7)}
      {visible >= 9 && box(9)}
      {visible >= 8 && box(8)}
      {visible >= 10 && box(10)}
    </svg>
  );
}
