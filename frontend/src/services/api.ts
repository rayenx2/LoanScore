import type {
  ActivityResponse,
  DriftRequest,
  DriftResponse,
  HealthResponse,
  MetricsHistoryResponse,
  ModelHealthResponse,
  ModelMetricsResponse,
  MonitoringReportResponse,
  PredictionRequest,
  PredictionResponse,
  RetrainingRecommendationResponse,
  RetrainingRunResponse,
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<HealthResponse>("/health"),
  predict: (payload: PredictionRequest) =>
    request<PredictionResponse>("/api/v1/predict", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  modelMetrics: () => request<ModelMetricsResponse>("/api/v1/model-metrics"),
  modelMetricsHistory: () => request<MetricsHistoryResponse>("/api/v1/model-metrics/history"),
  drift: (payload: DriftRequest = {}) =>
    request<DriftResponse>("/api/v1/drift", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  modelHealth: () => request<ModelHealthResponse>("/api/v1/model-health"),
  retrainingRecommendation: () =>
    request<RetrainingRecommendationResponse>("/api/v1/retraining-recommendation"),
  createRetrainingRecommendation: (payload: DriftRequest = {}) =>
    request<RetrainingRecommendationResponse>("/api/v1/retraining-recommendation", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  monitoringReport: () => request<MonitoringReportResponse>("/api/v1/monitoring-report"),
  generateMonitoringReport: () =>
    request<MonitoringReportResponse>("/api/v1/monitoring-report/generate", {
      method: "POST",
    }),
  activity: (limit = 20) => request<ActivityResponse>(`/api/v1/activity?limit=${limit}`),
  runRetraining: () =>
    request<RetrainingRunResponse>("/api/v1/retraining/run", {
      method: "POST",
    }),
};
