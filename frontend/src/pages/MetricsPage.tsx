import { useEffect, useState } from "react";

import { Badge } from "../components/Badge";
import { BarChart } from "../components/BarChart";
import { ConfusionMatrix } from "../components/ConfusionMatrix";
import { CurveChart } from "../components/CurveChart";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { TrendLine } from "../components/TrendLine";
import { api } from "../services/api";
import type {
  ClassificationMetrics,
  MetricsHistoryEntry,
  ModelHealthResponse,
  ModelMetricsResponse,
} from "../types/api";

function metricPercent(value: number): string {
  return `${Math.round(value * 1000) / 10}%`;
}

function healthTone(status: string): "success" | "warning" | "danger" {
  if (status === "Healthy") return "success";
  if (status === "Warning") return "warning";
  return "danger";
}

export function MetricsPage() {
  const [data, setData] = useState<ModelMetricsResponse | null>(null);
  const [health, setHealth] = useState<ModelHealthResponse | null>(null);
  const [history, setHistory] = useState<MetricsHistoryEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const [nowTick, setNowTick] = useState(Date.now());

  const refresh = () => {
    Promise.all([api.modelMetrics(), api.modelHealth(), api.modelMetricsHistory()])
      .then(([metrics, healthResponse, historyResponse]) => {
        setData(metrics);
        setHealth(healthResponse);
        setHistory(historyResponse.history);
        setError(null);
        setLastChecked(new Date());
      })
      .catch((err: Error) => setError(err.message));
  };

  useEffect(() => {
    refresh();
    const poll = setInterval(refresh, 12000);
    const clock = setInterval(() => setNowTick(Date.now()), 1000);
    return () => {
      clearInterval(poll);
      clearInterval(clock);
    };
  }, []);

  if (error) return <ErrorState message={error} />;
  if (!data) return <LoadingState label="Loading model metrics..." />;

  const secsAgo = lastChecked ? Math.max(0, Math.round((nowTick - lastChecked.getTime()) / 1000)) : null;

  const selectedMetrics = data.models[data.selected_model] as ClassificationMetrics | undefined;

  return (
    <section>
      <PageHeader
        title="Model Metrics"
        subtitle="Evaluate the selected production model against baseline and challenger training results."
      />

      <div className="live-status-row">
        <span className="live-dot" />
        <span>Auto-checks every 12s{secsAgo !== null ? ` · last checked ${secsAgo}s ago` : ""}</span>
        <button className="live-refresh-btn" onClick={refresh}>
          ↻ Check now
        </button>
      </div>

      <div className="summary-strip">
        <div>
          <span>Selected model</span>
          <strong>{data.selected_model.replaceAll("_", " ")}</strong>
        </div>
        <Badge tone="neutral">{data.model_version}</Badge>
        <Badge tone="neutral">{data.selection_metric}</Badge>
        {health ? (
          <>
            <div>
              <span>Deployment health</span>
              <strong>{health.health.score}/100</strong>
            </div>
            <Badge tone={healthTone(health.health.status)}>{health.health.status}</Badge>
          </>
        ) : null}
      </div>

      {selectedMetrics ? (
        <>
          <div className="metric-grid">
            <MetricCard label="Accuracy" value={metricPercent(selectedMetrics.accuracy)} status="healthy" />
            <MetricCard label="Precision" value={metricPercent(selectedMetrics.precision)} status="watch" />
            <MetricCard label="Recall" value={metricPercent(selectedMetrics.recall)} status="watch" />
            <MetricCard label="F1 score" value={metricPercent(selectedMetrics.f1_score)} status="watch" />
            <MetricCard label="ROC-AUC" value={metricPercent(selectedMetrics.roc_auc)} status="healthy" />
          </div>

          <div className="content-grid">
            <article className="panel">
              <h3>Selected model metrics</h3>
              <BarChart
                data={[
                  { label: "Accuracy", value: selectedMetrics.accuracy, tone: "success" },
                  { label: "Precision", value: selectedMetrics.precision, tone: "warning" },
                  { label: "Recall", value: selectedMetrics.recall, tone: "warning" },
                  { label: "F1", value: selectedMetrics.f1_score, tone: "neutral" },
                  { label: "ROC-AUC", value: selectedMetrics.roc_auc, tone: "success" },
                ]}
                valueFormatter={metricPercent}
              />
            </article>
            <article className="panel">
              <h3>Confusion matrix</h3>
              <ConfusionMatrix matrix={selectedMetrics.confusion_matrix} />
            </article>
          </div>

          <div className="content-grid">
            <article className="panel">
              <h3>ROC curve</h3>
              <CurveChart points={selectedMetrics.roc_curve} color="#1f6f78" xLabel="False positive rate" yLabel="True positive rate" />
            </article>
            <article className="panel">
              <h3>Precision-recall curve</h3>
              <CurveChart points={selectedMetrics.pr_curve} color="#f2cb66" xLabel="Recall" yLabel="Precision" />
            </article>
          </div>

          {history.length > 0 ? (
            <article className="panel">
              <h3>ROC-AUC trend across retraining runs</h3>
              <TrendLine values={history.map((h) => h.roc_auc)} />
              <div className="table-wrap" style={{ marginTop: "1rem" }}>
                <table>
                  <thead>
                    <tr>
                      <th>Run</th>
                      <th>Model</th>
                      <th>Rows</th>
                      <th>ROC-AUC</th>
                      <th>F1</th>
                      <th>Outcome</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map((entry) => (
                      <tr key={entry.timestamp}>
                        <td>{new Date(entry.timestamp).toLocaleString()}</td>
                        <td>{entry.selected_model.replaceAll("_", " ")}</td>
                        <td>{entry.training_rows}</td>
                        <td>{metricPercent(entry.roc_auc)}</td>
                        <td>{metricPercent(entry.f1_score)}</td>
                        <td>
                          {entry.promoted === null ? (
                            <span className="important-tag">training run</span>
                          ) : entry.promoted ? (
                            <Badge tone="success">Promoted</Badge>
                          ) : (
                            <Badge tone="neutral">Not promoted</Badge>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </article>
          ) : null}

          <article className="panel table-panel">
            <h3>Model comparison</h3>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Model</th>
                    <th>Accuracy</th>
                    <th>Precision</th>
                    <th>Recall</th>
                    <th>F1</th>
                    <th>ROC-AUC</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(data.models).map(([name, metrics]) => (
                    <tr key={name}>
                      <td>
                        <strong>{name.replaceAll("_", " ")}</strong>
                        {name === data.selected_model ? <span className="important-tag">Selected</span> : null}
                      </td>
                      <td>{metricPercent(metrics.accuracy)}</td>
                      <td>{metricPercent(metrics.precision)}</td>
                      <td>{metricPercent(metrics.recall)}</td>
                      <td>{metricPercent(metrics.f1_score)}</td>
                      <td>{metricPercent(metrics.roc_auc)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </article>
        </>
      ) : (
        <ErrorState message="The selected model was not found in the metrics payload." />
      )}
    </section>
  );
}
