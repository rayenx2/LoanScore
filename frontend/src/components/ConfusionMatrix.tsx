type ConfusionMatrixProps = {
  matrix: number[][];
};

export function ConfusionMatrix({ matrix }: ConfusionMatrixProps) {
  return (
    <div className="matrix" aria-label="Confusion matrix">
      <div className="matrix-cell heading" />
      <div className="matrix-cell heading">Predicted 0</div>
      <div className="matrix-cell heading">Predicted 1</div>
      <div className="matrix-cell heading">Actual 0</div>
      <div className="matrix-cell">{matrix[0]?.[0] ?? 0}</div>
      <div className="matrix-cell">{matrix[0]?.[1] ?? 0}</div>
      <div className="matrix-cell heading">Actual 1</div>
      <div className="matrix-cell">{matrix[1]?.[0] ?? 0}</div>
      <div className="matrix-cell">{matrix[1]?.[1] ?? 0}</div>
    </div>
  );
}
