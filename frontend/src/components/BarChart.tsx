type BarDatum = {
  label: string;
  value: number;
  tone?: "success" | "warning" | "danger" | "neutral";
};

type BarChartProps = {
  data: BarDatum[];
  valueFormatter?: (value: number) => string;
};

export function BarChart({ data, valueFormatter = (value) => String(value) }: BarChartProps) {
  const maxValue = Math.max(...data.map((item) => item.value), 1);

  return (
    <div className="bar-chart">
      {data.map((item) => (
        <div className="bar-row" key={item.label}>
          <div className="bar-meta">
            <span>{item.label}</span>
            <strong>{valueFormatter(item.value)}</strong>
          </div>
          <div className="bar-track">
            <div
              className={`bar-fill ${item.tone ?? "neutral"}`}
              style={{ width: `${Math.max(4, (item.value / maxValue) * 100)}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
