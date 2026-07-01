import { useEffect, useState } from "react";

import { Badge } from "../components/Badge";
import { BarChart } from "../components/BarChart";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { PageHeader } from "../components/PageHeader";
import { api } from "../services/api";
import type { DriftFeature, DriftResponse } from "../types/api";

function driftTone(status: DriftFeature["status"]): "success" | "warning" | "danger" {
  if (status === "high") return "danger";
  if (status === "medium") return "warning";
  return "success";
}

function formatNumber(value: number | null): string {
  if (value === null) return "-";
  return Math.abs(value) < 0.001 && value !== 0 ? value.toExponential(2) : String(Math.round(value * 10000) / 10000);
}

function formatPercent(value: number | null): string {
  if (value === null) return "-";
  return `${Math.round(value * 1000) / 10}%`;
}

export function DriftMonitoringPage() {
  const [data, setData] = useState<DriftResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .drift()
      .then(setData)
      .catch((err: Error) => setError(err.message));
  }, []);

  if (error) return <ErrorState message={error} />;
  if (!data) return <LoadingState label="Running drift detection..." />;

  return (
    <section>
      <PageHeader
        title="Drift Monitoring"
        subtitle="Compare baseline training data with production-style data to catch model reliability risk."
      />

      <div className="content-grid">
        <article className="panel">
          <h3>Drift summary</h3>
          <BarChart
            data={[
              { label: "High", value: data.drift_summary.high_drift_features, tone: "danger" },
              { label: "Medium", value: data.drift_summary.medium_drift_features, tone: "warning" },
              { label: "Low", value: data.drift_summary.low_drift_features, tone: "success" },
            ]}
          />
        </article>
        <article className="panel">
          <h3>Datasets</h3>
          <dl className="definition-list">
            <div>
              <dt>Baseline</dt>
              <dd>{data.baseline_dataset}</dd>
            </div>
            <div>
              <dt>Production</dt>
              <dd>{data.production_dataset}</dd>
            </div>
          </dl>
        </article>
      </div>

      <article className="panel table-panel">
        <h3>Feature drift details</h3>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Feature</th>
                <th>Type</th>
                <th>Status</th>
                <th>Mean difference</th>
                <th>Percent change</th>
                <th>KS p-value</th>
                <th>Distribution change</th>
              </tr>
            </thead>
            <tbody>
              {data.features.map((feature) => (
                <tr key={feature.feature_name}>
                  <td>
                    <strong>{feature.feature_name}</strong>
                    {feature.important ? <span className="important-tag">Important</span> : null}
                  </td>
                  <td>{feature.feature_type}</td>
                  <td>
                    <Badge tone={driftTone(feature.status)}>{feature.status}</Badge>
                  </td>
                  <td>{formatNumber(feature.mean_difference)}</td>
                  <td>{formatPercent(feature.percentage_change)}</td>
                  <td>{formatNumber(feature.ks_p_value)}</td>
                  <td>{formatNumber(feature.distribution_change)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>
    </section>
  );
}
