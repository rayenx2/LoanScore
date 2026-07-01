import { ActivityPage } from "./pages/ActivityPage";
import { DashboardLayout } from "./components/DashboardLayout";
import { DriftMonitoringPage } from "./pages/DriftMonitoringPage";
import { MetricsPage } from "./pages/MetricsPage";
import { MonitoringReportPage } from "./pages/MonitoringReportPage";
import { OverviewPage } from "./pages/OverviewPage";
import { PredictionPage } from "./pages/PredictionPage";
import { RetrainingPage } from "./pages/RetrainingPage";

const pages = [
  { id: "overview", label: "Overview", component: <OverviewPage /> },
  { id: "prediction", label: "Prediction", component: <PredictionPage /> },
  { id: "drift", label: "Drift Monitoring", component: <DriftMonitoringPage /> },
  { id: "metrics", label: "Model Metrics", component: <MetricsPage /> },
  { id: "retraining", label: "Retraining", component: <RetrainingPage /> },
  { id: "report", label: "Monitoring Report", component: <MonitoringReportPage /> },
  { id: "activity", label: "Activity", component: <ActivityPage /> },
] as const;

export function App() {
  return <DashboardLayout pages={pages} />;
}
