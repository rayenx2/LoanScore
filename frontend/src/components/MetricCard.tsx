type MetricCardProps = {
  label: string;
  value: string;
  status?: "healthy" | "watch" | "alert" | "neutral";
  detail?: string;
};

export function MetricCard({ label, value, status = "neutral", detail }: MetricCardProps) {
  return (
    <article className="metric-card">
      <span className={`status-dot ${status}`} />
      <p>{label}</p>
      <strong>{value}</strong>
      {detail ? <small>{detail}</small> : null}
    </article>
  );
}
