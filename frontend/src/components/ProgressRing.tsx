type ProgressRingProps = {
  value: number;
  label: string;
  tone: "success" | "warning" | "danger";
};

export function ProgressRing({ value, label, tone }: ProgressRingProps) {
  const clamped = Math.max(0, Math.min(100, value));

  return (
    <div
      className={`progress-ring ${tone}`}
      style={{ background: `conic-gradient(var(--ring-color) ${clamped * 3.6}deg, #e8edf2 0deg)` }}
    >
      <div>
        <strong>{clamped}</strong>
        <span>{label}</span>
      </div>
    </div>
  );
}
