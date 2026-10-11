import artwork from "@/data/surface-art.json";

type Mark = {
  op: string;
  x: number;
  y: number;
  x2?: number;
  y2?: number;
  w?: number;
  h?: number;
  r?: number;
  stroke: string;
  width: number;
  fill?: string;
  dash?: number[];
};
const surfaces: Record<string, Mark[]> = artwork;

/** The PDF generator consumes these same millimetre-based marks. */
export function SurfaceArt({ name }: { name: string }) {
  return surfaces[name]?.map((a, i) => {
    const style = {
      stroke: a.stroke,
      strokeWidth: a.width,
      fill: a.fill ?? "none",
    };
    if (a.op === "line")
      return (
        <line
          key={i}
          x1={a.x}
          y1={a.y}
          x2={a.x2}
          y2={a.y2}
          {...style}
          strokeDasharray={a.dash?.join(" ")}
        />
      );
    if (a.op === "rect")
      return (
        <rect key={i} x={a.x} y={a.y} width={a.w} height={a.h} {...style} />
      );
    return <circle key={i} cx={a.x} cy={a.y} r={a.r} {...style} />;
  });
}
