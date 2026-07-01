import type { CurvePoint } from "../types/api";

type CurveChartProps = {
  points: CurvePoint[];
  color?: string;
  width?: number;
  height?: number;
  xLabel?: string;
  yLabel?: string;
};

export function CurveChart({ points, color = "#1f6f78", width = 320, height = 220, xLabel, yLabel }: CurveChartProps) {
  if (!points || points.length < 2) {
    return <p className="curve-empty">Not enough points to render a curve.</p>;
  }

  const pad = 28;
  const plotW = width - pad * 1.5;
  const plotH = height - pad * 1.5;

  const toSvgX = (x: number) => pad + x * plotW;
  const toSvgY = (y: number) => pad + (1 - y) * plotH;

  const path = points.map((p) => `${toSvgX(p.x).toFixed(1)},${toSvgY(p.y).toFixed(1)}`).join(" ");
  const diagonal = `${toSvgX(0)},${toSvgY(0)} ${toSvgX(1)},${toSvgY(1)}`;

  return (
    <svg width={width} height={height} className="curve-chart">
      <line x1={pad} y1={pad} x2={pad} y2={height - pad / 2} stroke="#d7e0ea" strokeWidth="1" />
      <line x1={pad} y1={height - pad / 2} x2={width - pad / 4} y2={height - pad / 2} stroke="#d7e0ea" strokeWidth="1" />
      <polyline points={diagonal} fill="none" stroke="#e2e8f0" strokeWidth="1" strokeDasharray="4 4" />
      <polyline points={path} fill="none" stroke={color} strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round" />
      {xLabel ? (
        <text x={width / 2} y={height - 4} fontSize="10" fill="#64748b" textAnchor="middle">
          {xLabel}
        </text>
      ) : null}
      {yLabel ? (
        <text x={12} y={height / 2} fontSize="10" fill="#64748b" textAnchor="middle" transform={`rotate(-90, 12, ${height / 2})`}>
          {yLabel}
        </text>
      ) : null}
    </svg>
  );
}
