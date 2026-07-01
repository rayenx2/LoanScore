import { useEffect, useState } from "react";

import { api } from "../services/api";
import type { ModelHealthResponse, RetrainingRecommendationResponse } from "../types/api";
import { Badge } from "../components/Badge";
import { BarChart } from "../components/BarChart";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { ProgressRing } from "../components/ProgressRing";

type OverviewData = {
  health: ModelHealthResponse;
  recommendation: RetrainingRecommendationResponse;
};

function healthTone(status: string): "success" | "warning" | "danger" {
  if (status === "Healthy") return "success";
  if (status === "Warning") return "warning";
  return "danger";
}

export function OverviewPage() {
  const [data, setData] = useState<OverviewData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const [nowTick, setNowTick] = useState(Date.now());

  const refresh = () => {
    Promise.all([api.modelHealth(), api.retrainingRecommendation()])
      .then(([health, recommendation]) => {
        setData({ health, recommendation });
        setError(null);
        setLastChecked(new Date());
      })
      .catch((err: Error) => setError(err.message));
  };

  useEffect(() => {
    refresh();
    const poll = setInterval(refresh, 10000);
    const clock = setInterval(() => setNowTick(Date.now()), 1000);
    return () => {
      clearInterval(poll);
      clearInterval(clock);
    };
  }, []);

  if (error) return <ErrorState message={error} />;
  if (!data) return <LoadingState />;

  const secsAgo = lastChecked ? Math.max(0, Math.round((nowTick - lastChecked.getTime()) / 1000)) : null;

  const { health, recommendation } = data;
  const tone = healthTone(health.health.status);
  const highRiskPercent = Math.round(health.risk_summary.high_risk_percentage * 1000) / 10;

  return (
    <section>
      <PageHeader
        title="Model Reliability Overview"
        subtitle="A live summary of credit risk model health, production drift, and retraining readiness."
      />

      <div className="live-status-row">
        <span className="live-dot" />
        <span>Auto-checks every 10s{secsAgo !== null ? ` · last checked ${secsAgo}s ago` : ""}</span>
        <button className="live-refresh-btn" onClick={refresh}>
          ↻ Check now
        </button>
      </div>

      <div className="overview-grid">
        <article className="hero-panel">
          <ProgressRing value={health.health.score} label="Health score" tone={tone} />
          <div>
            <Badge tone={tone}>{health.health.status}</Badge>
            <h3>Production model reliability</h3>
            <p>
              The score combines drift severity, observed default-rate movement, and changes in predicted high-risk
              customer share.
            </p>
          </div>
        </article>

        <div className="metric-grid compact">
          <MetricCard
            label="High drift features"
            value={String(health.health.high_drift_features)}
            status={health.health.high_drift_features > 0 ? "alert" : "healthy"}
          />
          <MetricCard
            label="Medium drift features"
            value={String(health.health.medium_drift_features)}
            status={health.health.medium_drift_features > 0 ? "watch" : "healthy"}
          />
          <MetricCard label="High-risk predictions" value={`${highRiskPercent}%`} status="watch" />
          <MetricCard
            label="Retraining needed"
            value={recommendation.retraining_needed ? "Yes" : "No"}
            status={recommendation.retraining_needed ? "alert" : "healthy"}
          />
        </div>
      </div>

      <div className="content-grid">
        <article className="panel">
          <h3>Drift summary</h3>
          <BarChart
            data={[
              { label: "High", value: health.drift_summary.high_drift_features, tone: "danger" },
              { label: "Medium", value: health.drift_summary.medium_drift_features, tone: "warning" },
              { label: "Low", value: health.drift_summary.low_drift_features, tone: "success" },
            ]}
          />
        </article>
        <article className="panel">
          <h3>Prediction risk distribution</h3>
          <BarChart
            data={[
              { label: "Low risk", value: health.risk_summary.low_risk_percentage, tone: "success" },
              { label: "Medium risk", value: health.risk_summary.medium_risk_percentage, tone: "warning" },
              { label: "High risk", value: health.risk_summary.high_risk_percentage, tone: "danger" },
            ]}
            valueFormatter={(value) => `${Math.round(value * 1000) / 10}%`}
          />
        </article>
      </div>
    </section>
  );
}
