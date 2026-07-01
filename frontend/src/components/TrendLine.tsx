type TrendLineProps = {
  values: number[];
  color?: string;
  width?: number;
  height?: number;
};

export function TrendLine({ values, color = "#1f6f78", width = 280, height = 60 }: TrendLineProps) {
  if (!values || values.length < 2) {
    return <p className="curve-empty">Not enough retraining runs yet to show a trend.</p>;
  }

  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const step = width / (values.length - 1);

  const points = values
    .map((v, i) => `${(i * step).toFixed(1)},${(height - ((v - min) / range) * height).toFixed(1)}`)
    .join(" ");

  return (
    <svg width={width} height={height} className="curve-chart">
      <polyline points={points} fill="none" stroke={color} strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
    </svg>
  );
}
