import { FormEvent, useEffect, useState } from "react";

import { Badge } from "../components/Badge";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { api } from "../services/api";
import type { ApplicantFeatures, PredictionResponse } from "../types/api";

const loanPurposes = ["auto", "debt_consolidation", "education", "home_improvement", "medical", "small_business"];

const initialFeatures: ApplicantFeatures = {
  age: 38,
  income: 72000,
  credit_score: 680,
  loan_amount: 22000,
  loan_term_months: 60,
  employment_years: 4,
  debt_to_income_ratio: 0.32,
  previous_defaults: 0,
  number_of_open_accounts: 7,
  loan_purpose: "auto",
};

const highRiskDemoFeatures: ApplicantFeatures = {
  age: 42,
  income: 48000,
  credit_score: 575,
  loan_amount: 42000,
  loan_term_months: 60,
  employment_years: 1,
  debt_to_income_ratio: 0.52,
  previous_defaults: 1,
  number_of_open_accounts: 11,
  loan_purpose: "debt_consolidation",
};

function reasonLabel(code: string): string {
  return code.replaceAll("_", " ");
}

function riskTone(riskClass: PredictionResponse["risk_class"]): "success" | "warning" | "danger" {
  if (riskClass === "High") return "danger";
  if (riskClass === "Medium") return "warning";
  return "success";
}

function generateApplicantId(): string {
  return `applicant-${Date.now()}`;
}

export function PredictionPage() {
  const [features, setFeatures] = useState<ApplicantFeatures>(initialFeatures);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("demo") !== "high-risk") {
      return;
    }

    setFeatures(highRiskDemoFeatures);
    setError(null);
    setIsLoading(true);
    api
      .predict({ applicant_id: "high-risk-demo-001", features: highRiskDemoFeatures })
      .then(setPrediction)
      .catch((err: Error) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, []);

  function updateField<K extends keyof ApplicantFeatures>(field: K, value: ApplicantFeatures[K]) {
    setFeatures((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      const response = await api.predict({ applicant_id: generateApplicantId(), features });
      setPrediction(response);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section>
      <PageHeader
        title="Loan Default Prediction"
        subtitle="Score an applicant with the trained credit risk model and inspect the business-facing risk signals."
      />

      <div className="prediction-layout">
        <form className="panel prediction-form" onSubmit={handleSubmit}>
          <h3>Applicant input</h3>
          <div className="form-grid">
            <label>
              Age
              <input
                min={18}
                type="number"
                value={features.age}
                onChange={(event) => updateField("age", Number(event.target.value))}
              />
            </label>
            <label>
              Income
              <input
                min={0}
                type="number"
                value={features.income}
                onChange={(event) => updateField("income", Number(event.target.value))}
              />
            </label>
            <label>
              Credit score
              <input
                max={850}
                min={300}
                type="number"
                value={features.credit_score}
                onChange={(event) => updateField("credit_score", Number(event.target.value))}
              />
            </label>
            <label>
              Loan amount
              <input
                min={0}
                type="number"
                value={features.loan_amount}
                onChange={(event) => updateField("loan_amount", Number(event.target.value))}
              />
            </label>
            <label>
              Loan term
              <input
                min={1}
                type="number"
                value={features.loan_term_months}
                onChange={(event) => updateField("loan_term_months", Number(event.target.value))}
              />
            </label>
            <label>
              Employment years
              <input
                min={0}
                step="0.1"
                type="number"
                value={features.employment_years}
                onChange={(event) => updateField("employment_years", Number(event.target.value))}
              />
            </label>
            <label>
              Debt-to-income ratio
              <input
                min={0}
                step="0.01"
                type="number"
                value={features.debt_to_income_ratio}
                onChange={(event) => updateField("debt_to_income_ratio", Number(event.target.value))}
              />
            </label>
            <label>
              Previous defaults
              <input
                min={0}
                type="number"
                value={features.previous_defaults}
                onChange={(event) => updateField("previous_defaults", Number(event.target.value))}
              />
            </label>
            <label>
              Open accounts
              <input
                min={0}
                type="number"
                value={features.number_of_open_accounts}
                onChange={(event) => updateField("number_of_open_accounts", Number(event.target.value))}
              />
            </label>
            <label>
              Loan purpose
              <select
                value={features.loan_purpose}
                onChange={(event) => updateField("loan_purpose", event.target.value)}
              >
                {loanPurposes.map((purpose) => (
                  <option key={purpose} value={purpose}>
                    {purpose.replaceAll("_", " ")}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <button className="primary-button" disabled={isLoading} type="submit">
            {isLoading ? "Scoring..." : "Score applicant"}
          </button>
        </form>

        <div className="prediction-result">
          {isLoading ? <LoadingState label="Scoring applicant..." /> : null}
          {error ? <ErrorState message={error} /> : null}
          {prediction ? (
            <>
              <div className="metric-grid compact">
                <MetricCard
                  label="Default probability"
                  value={`${Math.round(prediction.default_probability * 1000) / 10}%`}
                  status={prediction.risk_class === "High" ? "alert" : prediction.risk_class === "Medium" ? "watch" : "healthy"}
                />
                <MetricCard label="Risk class" value={prediction.risk_class} status={prediction.risk_class === "High" ? "alert" : "healthy"} />
              </div>
              <article className="panel decision-panel">
                <Badge tone={riskTone(prediction.risk_class)}>{prediction.risk_class} risk</Badge>
                <h3>Business explanation</h3>
                <p>{prediction.explanation_text}</p>
                <div className="reason-chips">
                  {prediction.reason_codes.map((code) => (
                    <span key={code}>{reasonLabel(code)}</span>
                  ))}
                </div>
              </article>
              <article className="panel">
                <h3>Top risk factors</h3>
                <ul className="factor-list">
                  {prediction.top_risk_factors.map((factor) => (
                    <li key={factor.factor}>
                      <Badge tone={factor.severity === "high" ? "danger" : factor.severity === "medium" ? "warning" : "success"}>
                        {factor.severity}
                      </Badge>
                      <div>
                        <strong>{reasonLabel(factor.factor)}</strong>
                        <p>{factor.message}</p>
                      </div>
                    </li>
                  ))}
                </ul>
              </article>
            </>
          ) : !isLoading && !error ? (
            <article className="panel empty-panel">
              <h3>Ready to score</h3>
              <p>Submit the applicant profile to receive probability, risk class, and reason codes.</p>
            </article>
          ) : null}
        </div>
      </div>
    </section>
  );
}
