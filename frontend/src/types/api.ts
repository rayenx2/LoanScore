export type HealthResponse = {
  status: string;
  service: string;
};

export type ApplicantFeatures = {
  age: number;
  income: number;
  credit_score: number;
  loan_amount: number;
  loan_term_months: number;
  employment_years: number;
  debt_to_income_ratio: number;
  previous_defaults: number;
  number_of_open_accounts: number;
  loan_purpose: string;
};

export type PredictionRequest = {
  applicant_id: string;
  features: ApplicantFeatures;
};

export type PredictionResponse = {
  applicant_id: string;
  default_probability: number;
  risk_class: "Low" | "Medium" | "High";
  reason_codes: string[];
  explanation_text: string;
  top_risk_factors: TopRiskFactor[];
  model_version: string;
};

export type TopRiskFactor = {
  factor: string;
  severity: "low" | "medium" | "high";
  value: number | string | null;
  message: string;
};

export type CurvePoint = {
  x: number;
  y: number;
};

export type ClassificationMetrics = {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc: number;
  confusion_matrix: number[][];
  roc_curve: CurvePoint[];
  pr_curve: CurvePoint[];
};

export type MetricsHistoryEntry = {
  timestamp: string;
  selected_model: string;
  training_rows: number;
  test_rows: number | null;
  roc_auc: number;
  f1_score: number;
  accuracy: number;
  event: string;
  promoted: boolean | null;
};

export type MetricsHistoryResponse = {
  history: MetricsHistoryEntry[];
};

export type RetrainingRunResponse = {
  promoted: boolean;
  reason: string;
  challenger_model_name: string;
  training_rows: number;
  champion_metrics: ClassificationMetrics | null;
  challenger_metrics: ClassificationMetrics;
};

export type ModelMetricsResponse = {
  model_version: string;
  selected_model: string;
  selection_metric: string;
  training_rows: number;
  test_rows: number;
  models: Record<string, ClassificationMetrics>;
};

export type DriftRequest = {
  baseline_dataset_uri?: string;
  production_dataset_uri?: string;
};

export type DriftFeature = {
  feature_name: string;
  feature_type: "numeric" | "categorical";
  baseline_mean: number | null;
  production_mean: number | null;
  mean_difference: number | null;
  percentage_change: number | null;
  ks_p_value: number | null;
  distribution_change: number | null;
  status: "low" | "medium" | "high";
  important: boolean;
};

export type DriftSummary = {
  total_features: number;
  high_drift_features: number;
  medium_drift_features: number;
  low_drift_features: number;
};

export type RiskSummary = {
  total_records: number;
  average_default_probability: number;
  low_risk_percentage: number;
  medium_risk_percentage: number;
  high_risk_percentage: number;
};

export type ModelHealth = {
  score: number;
  status: "Healthy" | "Warning" | "Critical";
  high_drift_features: number;
  medium_drift_features: number;
  performance_drop: number | null;
  high_risk_increase: number;
};

export type DriftResponse = {
  baseline_dataset: string;
  production_dataset: string;
  drift_detected: boolean;
  drift_summary: DriftSummary;
  features: DriftFeature[];
};

export type ModelHealthResponse = {
  health: ModelHealth;
  drift_summary: DriftSummary;
  risk_summary: RiskSummary;
};

export type RetrainingRecommendationResponse = {
  retraining_needed: boolean;
  priority: "Low" | "Medium" | "High";
  reasons: string[];
  recommended_action: string;
};

export type MonitoringReportResponse = {
  generated_at: string;
  executive_summary: string;
  model_status: "Healthy" | "Warning" | "Critical";
  model_health_score: number;
  model_metrics: ModelMetricsResponse;
  drift_summary: DriftSummary;
  model_health: ModelHealth;
  risk_summary: RiskSummary;
  high_risk_prediction_percentage: number;
  top_drifted_features: ReportDriftFeature[];
  retraining_recommendation: RetrainingRecommendationResponse;
  key_business_risks: string[];
  recommended_next_steps: string[];
};

export type ReportDriftFeature = {
  feature_name: string;
  feature_type: string;
  status: "low" | "medium" | "high";
  important: boolean;
  percentage_change: number | null;
  distribution_change: number | null;
  ks_p_value: number | null;
};

export type ActivityEvent = {
  timestamp: string;
  event_type: "prediction" | "drift_check" | "model_health" | "monitoring_report" | "retraining_run";
  applicant_id: string | null;
  risk_class: string | null;
  default_probability: number | null;
  drift_detected: boolean | null;
  model_health_score: number | null;
  promoted: boolean | null;
};

export type ActivitySummary = {
  total_predictions: number;
  total_drift_checks: number;
  total_reports_generated: number;
  high_risk_predictions: number;
  average_default_probability: number | null;
  last_drift_detected: boolean | null;
  last_model_health_score: number | null;
};

export type ActivityResponse = {
  summary: ActivitySummary;
  recent_events: ActivityEvent[];
};
