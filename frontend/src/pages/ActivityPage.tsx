import { useEffect, useRef, useState } from "react";

import { Badge } from "../components/Badge";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { api } from "../services/api";
import type { ActivityResponse } from "../types/api";

function formatTimestamp(value: string): string {
  return new Date(value).toLocaleString();
}

function eventLabel(eventType: string): string {
  switch (eventType) {
    case "prediction":
      return "Credit risk prediction";
    case "drift_check":
      return "Drift check";
    case "model_health":
      return "Model health check";
    case "monitoring_report":
      return "Monitoring report generated";
    case "retraining_run":
      return "Retraining run";
    default:
      return eventType;
  }
}

export function ActivityPage() {
  const [data, setData] = useState<ActivityResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const [nowTick, setNowTick] = useState(Date.now());
  const seenKeysRef = useRef(new Set<string>());
  const initializedRef = useRef(false);
  const [newKeys, setNewKeys] = useState(new Set<string>());

  const refresh = () => {
    api
      .activity(50)
      .then((response) => {
        const fresh = new Set<string>();
        response.recent_events.forEach((event) => {
          const key = `${event.timestamp}-${event.event_type}`;
          if (!seenKeysRef.current.has(key)) fresh.add(key);
          seenKeysRef.current.add(key);
        });
        if (initializedRef.current) setNewKeys(fresh);
        initializedRef.current = true;
        setData(response);
        setError(null);
        setLastChecked(new Date());
      })
      .catch((err: Error) => setError(err.message));
  };

  useEffect(() => {
    refresh();
    const poll = setInterval(refresh, 8000);
    const clock = setInterval(() => setNowTick(Date.now()), 1000);
    return () => {
      clearInterval(poll);
      clearInterval(clock);
    };
  }, []);

  if (error) return <ErrorState message={error} />;
  if (!data) return <LoadingState label="Loading activity..." />;

  const secsAgo = lastChecked ? Math.max(0, Math.round((nowTick - lastChecked.getTime()) / 1000)) : null;
  const { summary, recent_events: events } = data;

  const averageProbability =
    summary.average_default_probability !== null
      ? `${Math.round(summary.average_default_probability * 1000) / 10}%`
      : "n/a";

  return (
    <section>
      <PageHeader
        title="Activity"
        subtitle="Live overview of predictions, drift checks and reports served by this API instance since it started."
      />

      <div className="live-status-row">
        <span className="live-dot" />
        <span>Auto-refreshes every 8s{secsAgo !== null ? ` · last checked ${secsAgo}s ago` : ""}</span>
        <button className="live-refresh-btn" onClick={refresh}>
          ↻ Refresh now
        </button>
      </div>

      <div className="metric-grid">
        <MetricCard label="Total predictions" value={String(summary.total_predictions)} status="neutral" />
        <MetricCard
          label="High-risk predictions"
          value={String(summary.high_risk_predictions)}
          status={summary.high_risk_predictions > 0 ? "alert" : "healthy"}
        />
        <MetricCard label="Average default probability" value={averageProbability} status="watch" />
        <MetricCard label="Drift checks run" value={String(summary.total_drift_checks)} status="neutral" />
        <MetricCard label="Monitoring reports generated" value={String(summary.total_reports_generated)} status="neutral" />
      </div>

      <div className="summary-strip">
        <div>
          <span>Last drift result</span>
          <strong>
            {summary.last_drift_detected === null
              ? "Not checked yet"
              : summary.last_drift_detected
                ? "Drift detected"
                : "No drift detected"}
          </strong>
        </div>
        <div>
          <span>Last model health score</span>
          <strong>{summary.last_model_health_score ?? "n/a"}</strong>
        </div>
      </div>

      <article className="panel table-panel">
        <h3>Recent events</h3>
        {events.length === 0 ? (
          <p>No activity recorded yet. Use the Prediction and Drift Monitoring pages to generate events.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Event</th>
                  <th>Applicant</th>
                  <th>Risk class</th>
                  <th>Default probability</th>
                  <th>Result</th>
                </tr>
              </thead>
              <tbody>
                {events.map((event) => {
                  const key = `${event.timestamp}-${event.event_type}`;
                  return (
                  <tr key={key} className={newKeys.has(key) ? "activity-row-new" : ""}>
                    <td>{formatTimestamp(event.timestamp)}</td>
                    <td>{eventLabel(event.event_type)}</td>
                    <td>{event.applicant_id ?? "-"}</td>
                    <td>
                      {event.risk_class ? (
                        <Badge
                          tone={
                            event.risk_class.toLowerCase() === "high"
                              ? "danger"
                              : event.risk_class.toLowerCase() === "medium"
                                ? "warning"
                                : "success"
                          }
                        >
                          {event.risk_class}
                        </Badge>
                      ) : (
                        "-"
                      )}
                    </td>
                    <td>
                      {event.default_probability !== null
                        ? `${Math.round(event.default_probability * 1000) / 10}%`
                        : "-"}
                    </td>
                    <td>
                      {event.event_type === "retraining_run"
                        ? event.promoted
                          ? "Challenger promoted"
                          : "Challenger not promoted"
                        : event.drift_detected !== null
                          ? event.drift_detected
                            ? "Drift detected"
                            : "No drift"
                          : event.model_health_score !== null
                            ? `Health score: ${event.model_health_score}`
                            : "-"}
                    </td>
                  </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </article>
    </section>
  );
}
