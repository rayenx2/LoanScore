type LoadingStateProps = {
  label?: string;
};

export function LoadingState({ label = "Loading dashboard data..." }: LoadingStateProps) {
  return (
    <div className="state-card">
      <div className="loader" />
      <p>{label}</p>
    </div>
  );
}
