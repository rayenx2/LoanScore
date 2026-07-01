import { useEffect, useState } from "react";

import { Badge } from "../components/Badge";
import { BarChart } from "../components/BarChart";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { ProgressRing } from "../components/ProgressRing";
import { api } from "../services/api";
import type { MonitoringReportResponse } from "../types/api";

function statusTone(status: string): "success" | "warning" | "danger" {
  if (status === "Healthy") return "success";
  if (status === "Warning") return "warning";
  return "danger";
}

function formatPercent(value: number): string {
  return `${Math.round(value * 1000) / 10}%`;
}

export function MonitoringReportPage() {
  const [report, setReport] = useState<MonitoringReportResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    api
      .monitoringReport()
      .then(setReport)
      .catch((err: Error) => setError(err.message));
  }, []);

  async function refreshReport() {
    setIsGenerating(true);
    setError(null);
    try {
      setReport(await api.generateMonitoringReport());
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setIsGenerating(false);
    }
  }

  if (error) return <ErrorState message={error} />;
  if (!report) return <LoadingState label="Loading monitoring report..." />;

  const tone = statusTone(report.model_status);

  return (
    <section>
      <PageHeader
        title="Monitoring Report"
        subtitle="A business-friendly governance view of model health, drift, retraining risk, and next steps."
        eyebrow="AI governance report"
      />

      <div className="report-actions">
        <span>Generated {new Date(report.generated_at).toLocaleString()}</span>
        <button className="primary-button" disabled={isGenerating} onClick={refreshReport} type="button">
          {isGenerating ? "Generating..." : "Generate fresh report"}
        </button>
      </div>

      <article className="panel report-summary">
        <Badge tone={tone}>{report.model_status}</Badge>
        <h3>Executive summary</h3>
        <p>{report.executive_summary}</p>
      </article>

      <div className="overview-grid">
        <article className="hero-panel">
          <ProgressRing value={report.model_health_score} label="Health score" tone={tone} />
          <div>
            <Badge tone={tone}>{report.model_status}</Badge>
            <h3>Model status</h3>
            <p>
              This score reflects production drift, label-based performance risk, and high-risk prediction movement.
            </p>
          </div>
        </article>
        <div className="metric-grid compact">
          <MetricCard label="High drift features" value={String(report.drift_summary.high_drift_features)} status="alert" />
          <MetricCard label="Medium drift features" value={String(report.drift_summary.medium_drift_features)} status="watch" />
          <MetricCard label="High-risk predictions" value={formatPercent(report.high_risk_prediction_percentage)} status="watch" />
          <MetricCard
            label="Retraining priority"
            value={report.retraining_recommendation.priority}
            status={report.retraining_recommendation.priority === "High" ? "alert" : "watch"}
          />
        </div>
      </div>

      <div className="content-grid">
        <article className="panel">
          <h3>Top drifted features</h3>
          <BarChart
            data={report.top_drifted_features.map((feature) => ({
              label: feature.feature_name,
              value: Math.abs(feature.percentage_change ?? feature.distribution_change ?? 0),
              tone: feature.status === "high" ? "danger" : feature.status === "medium" ? "warning" : "success",
            }))}
            valueFormatter={formatPercent}
          />
        </article>
        <article className="panel decision-panel">
          <Badge tone={report.retraining_recommendation.priority === "High" ? "danger" : "warning"}>
            {report.retraining_recommendation.priority} priority
          </Badge>
          <h3>Retraining recommendation</h3>
          <p>{report.retraining_recommendation.recommended_action}</p>
        </article>
      </div>

      <div className="content-grid">
        <article className="panel">
          <h3>Key business risks</h3>
          <ul className="reason-list">
            {report.key_business_risks.map((risk) => (
              <li key={risk}>{risk}</li>
            ))}
          </ul>
        </article>
        <article className="panel">
          <h3>Recommended next steps</h3>
          <ul className="reason-list">
            {report.recommended_next_steps.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ul>
        </article>
      </div>
    </section>
  );
}
