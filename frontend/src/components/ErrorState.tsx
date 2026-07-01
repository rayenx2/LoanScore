type ErrorStateProps = {
  message: string;
};

export function ErrorState({ message }: ErrorStateProps) {
  return (
    <div className="state-card error-state">
      <strong>Unable to load backend data</strong>
      <p>{message}</p>
    </div>
  );
}
