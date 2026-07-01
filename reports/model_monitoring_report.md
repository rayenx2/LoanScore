# LoanScore Monitoring Report

Generated at: 2026-07-01T19:10:57.422076+00:00

## Executive Summary

Model health is Critical with a score of 27/100. 5 features show high drift, and 19.0% of production applicants are predicted high risk. Retraining priority is High.

## Model Status

- Status: Critical
- Health score: 27/100
- High-risk prediction percentage: 19.0%

## Drift Summary

- High drift features: 5
- Medium drift features: 1
- Low drift features: 4

## Top Drifted Features

- previous_defaults: high drift
- debt_to_income_ratio: high drift
- loan_amount: high drift
- employment_years: high drift
- age: high drift

## Retraining Recommendation

- Retraining needed: True
- Priority: High
- Recommended action: Start retraining analysis with the latest production data and compare challenger models.

## Key Business Risks

- Model reliability is critical and should be reviewed before expanding automated use.
- Important borrower characteristics have shifted from the training baseline.
- Retraining is recommended before treating the current model as stable.

## Recommended Next Steps

- Review high-drift features with credit risk and data owners.
- Create a retraining dataset from recent production records.
- Train challenger models and compare fairness, recall, precision, and ROC-AUC.
- Keep enhanced monitoring active until production data stabilizes.
