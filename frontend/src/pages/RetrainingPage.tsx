import { useEffect, useState } from "react";

import { Badge } from "../components/Badge";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { api } from "../services/api";
import type { RetrainingRecommendationResponse, RetrainingRunResponse } from "../types/api";

function priorityTone(priority: string): "success" | "warning" | "danger" {
  if (priority === "High") return "danger";
  if (priority === "Medium") return "warning";
  return "success";
}

function metricPercent(value: number): string {
  return `${Math.round(value * 1000) / 10}%`;
}

export function RetrainingPage() {
  const [data, setData] = useState<RetrainingRecommendationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [runResult, setRunResult] = useState<RetrainingRunResponse | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);

  useEffect(() => {
    api
      .retrainingRecommendation()
      .then(setData)
      .catch((err: Error) => setError(err.message));
  }, []);

  async function handleRunRetraining() {
    setIsRunning(true);
    setRunError(null);
    try {
      const result = await api.runRetraining();
      setRunResult(result);
      // Recommendation may have changed now that a new champion could be deployed.
      const updated = await api.retrainingRecommendation();
      setData(updated);
    } catch (err) {
      setRunError((err as Error).message);
    } finally {
      setIsRunning(false);
    }
  }

  if (error) return <ErrorState message={error} />;
  if (!data) return <LoadingState label="Loading retraining recommendation..." />;

  return (
    <section>
      <PageHeader
        title="Retraining Recommendation"
        subtitle="Translate monitoring signals into a clear action for model governance and model owners."
      />

      <div className="metric-grid">
        <MetricCard
          label="Retraining needed"
          value={data.retraining_needed ? "Yes" : "No"}
          status={data.retraining_needed ? "alert" : "healthy"}
        />
        <MetricCard label="Priority" value={data.priority} status={data.priority === "High" ? "alert" : "watch"} />
      </div>

      <div className="content-grid">
        <article className="panel decision-panel">
          <Badge tone={priorityTone(data.priority)}>{data.priority} priority</Badge>
          <h3>{data.retraining_needed ? "Retraining should be planned" : "Monitoring can continue"}</h3>
          <p>{data.recommended_action}</p>
        </article>
        <article className="panel">
          <h3>Business explanation</h3>
          <p>
            Retraining is recommended when production data no longer resembles training data, the health score drops, or
            the model starts assigning a much larger share of customers to the high-risk segment.
          </p>
        </article>
      </div>

      <article className="panel">
        <h3>Reasons</h3>
        <ul className="reason-list">
          {data.reasons.map((reason) => (
            <li key={reason}>{reason}</li>
          ))}
        </ul>
      </article>

      <article className="panel">
        <h3>Run retraining</h3>
        <p>
          Trains a challenger model on baseline + production data combined (not just the original training set), and only
          promotes it to production if it actually beats the current champion on ROC-AUC (then F1 as a tiebreaker).
        </p>
        <button className="primary-button" disabled={isRunning} onClick={handleRunRetraining}>
          {isRunning ? "Training challenger..." : "Run retraining now"}
        </button>

        {runError ? <ErrorState message={runError} /> : null}

        {runResult ? (
          <div className="retrain-result">
            <Badge tone={runResult.promoted ? "success" : "neutral"}>
              {runResult.promoted ? "Challenger promoted" : "Challenger not promoted"}
            </Badge>
            <p>{runResult.reason}</p>

            <div className="content-grid">
              <div>
                <h4>Champion (before)</h4>
                {runResult.champion_metrics ? (
                  <ul className="reason-list">
                    <li>ROC-AUC: {metricPercent(runResult.champion_metrics.roc_auc)}</li>
                    <li>F1: {metricPercent(runResult.champion_metrics.f1_score)}</li>
                    <li>Accuracy: {metricPercent(runResult.champion_metrics.accuracy)}</li>
                  </ul>
                ) : (
                  <p>No champion was deployed yet.</p>
                )}
              </div>
              <div>
                <h4>Challenger ({runResult.challenger_model_name.replaceAll("_", " ")})</h4>
                <ul className="reason-list">
                  <li>ROC-AUC: {metricPercent(runResult.challenger_metrics.roc_auc)}</li>
                  <li>F1: {metricPercent(runResult.challenger_metrics.f1_score)}</li>
                  <li>Accuracy: {metricPercent(runResult.challenger_metrics.accuracy)}</li>
                  <li>Trained on {runResult.training_rows} rows (baseline + production)</li>
                </ul>
              </div>
            </div>
          </div>
        ) : null}
      </article>
    </section>
  );
}
