"""
Builds LoanScore's credit_risk_sample.csv / credit_risk_production.csv from the
REAL UCI Statlog German Credit Data (Prof. Hans Hofmann, Univ. Hamburg; numeric-coded
version produced by Strathclyde University) instead of a synthetic generator.

Source: https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data
Mirror used: raw.githubusercontent.com/rohan18joseph/germancreditdata/master/german_credit.csv
(same 1000-row dataset, numeric-coded columns in the documented A1x/A2x/... order)

German Credit Data does not have every field our app's schema wants. Where a direct
column exists, we use it as-is. Where it doesn't, we DERIVE a proxy from real
correlated fields using an explicit, documented formula below — this is disclosed,
not fabricated ground truth:

  - credit_score  : no FICO-style score in the source data. Derived via a classic
                    credit-scorecard formula (point weights per risk category,
                    the same style real bureaus used pre-ML) from Account Balance,
                    Savings, and Credit History. NOT an observed value.
  - income        : no income field in the source data. Derived from Occupation
                    (job skill tier) and Type of apartment (rent/own/free) as a
                    rough income proxy. NOT an observed value.

Everything else below is a real, direct, or well-defined bucket-midpoint mapping
from the actual German Credit attributes (see german.doc attribute list).

DRIFT SIMULATION (disclosed): a random 70/30 split of the same 1000 real rows would
have near-identical feature distributions, making the app's drift-detection feature
show ~0 drift and defeating its purpose. To demonstrate meaningful drift, the
production (30%) slice has a documented perturbation applied to its FEATURE columns
only (loan amounts up, age slightly older, debt-to-income up) — a standard drift-
simulation technique (perturb real covariates to model population shift). The
`defaulted` outcome for each row is left untouched — it's the real historical label
for that real applicant, not synthesized.
"""

import numpy as np
import pandas as pd

RAW_PATH = "data/external/german_credit_raw.csv"
BASELINE_OUT = "data/sample_data/credit_risk_sample.csv"
PRODUCTION_OUT = "data/sample_data/credit_risk_production.csv"
RANDOM_STATE = 42

# Attribute 4 — Purpose (A40..A410) -> our loan_purpose categories
PURPOSE_MAP = {
    0: "auto",              # A40 car (new)
    1: "auto",              # A41 car (used)
    2: "home_improvement",  # A42 furniture/equipment
    3: "home_improvement",  # A43 radio/television
    4: "home_improvement",  # A44 domestic appliances
    5: "home_improvement",  # A45 repairs
    6: "education",         # A46 education
    7: "medical",           # A47 vacation (rare/absent in this sample) - no clean fit, treated as discretionary/personal
    8: "education",         # A48 retraining
    9: "small_business",    # A49 business
    10: "debt_consolidation",  # A410 others - closest catch-all for "other financial need"
}

# Attribute 7 — Present employment since (A71..A75) -> employment_years bucket midpoint
EMPLOYMENT_YEARS_MAP = {1: 0.0, 2: 0.5, 3: 2.5, 4: 5.5, 5: 10.0}

# Attribute 3 — Credit history (A30..A34) -> previous_defaults count
PREVIOUS_DEFAULTS_MAP = {0: 0, 1: 0, 2: 0, 3: 1, 4: 2}

# Attribute 8 — Installment rate as % of disposable income (1..4 bucket) -> ratio midpoint
DEBT_TO_INCOME_MAP = {1: 0.15, 2: 0.25, 3: 0.35, 4: 0.45}

# --- credit_score: scorecard-style derivation (documented proxy, not observed) ---
ACCOUNT_BALANCE_POINTS = {1: 0, 2: 60, 3: 100, 4: 130}  # A11(worst)..A14(no checking acct)
SAVINGS_POINTS = {1: 0, 2: 30, 3: 60, 4: 90, 5: 50}      # A61(worst)..A65(unknown/none)
CREDIT_HISTORY_POINTS = {0: 40, 1: 60, 2: 80, 3: 20, 4: 0}  # A30..A34

# --- income: rough proxy from job tier + housing (documented proxy, not observed) ---
OCCUPATION_BASE_INCOME = {1: 18000, 2: 24000, 3: 34000, 4: 52000}  # A171(worst)..A174(best)
APARTMENT_ADJUST = {1: 0.9, 2: 1.15, 3: 0.8}  # A151 rent, A152 own, A153 for free


def _credit_score(row: pd.Series) -> int:
    score = (
        300
        + ACCOUNT_BALANCE_POINTS[row["Account Balance"]]
        + SAVINGS_POINTS[row["Value Savings/Stocks"]]
        + CREDIT_HISTORY_POINTS[row["Payment Status of Previous Credit"]]
        + min(row["Age (years)"], 70) * 2
    )
    return int(np.clip(score, 300, 850))


def _income(row: pd.Series, rng: np.random.Generator) -> float:
    base = OCCUPATION_BASE_INCOME[row["Occupation"]] * APARTMENT_ADJUST[row["Type of apartment"]]
    age_factor = 1.0 + min(max(row["Age (years)"] - 25, 0), 30) * 0.01
    noise = rng.normal(1.0, 0.08)
    return round(base * age_factor * noise, 2)


def build() -> pd.DataFrame:
    raw = pd.read_csv(RAW_PATH)
    rng = np.random.default_rng(RANDOM_STATE)

    out = pd.DataFrame()
    out["age"] = raw["Age (years)"]
    out["income"] = raw.apply(lambda r: _income(r, rng), axis=1)
    out["credit_score"] = raw.apply(_credit_score, axis=1)
    out["loan_amount"] = raw["Credit Amount"].astype(float)
    out["loan_term_months"] = raw["Duration of Credit (month)"].astype(int)
    out["employment_years"] = raw["Length of current employment"].map(EMPLOYMENT_YEARS_MAP)
    out["debt_to_income_ratio"] = raw["Instalment per cent"].map(DEBT_TO_INCOME_MAP)
    out["previous_defaults"] = raw["Payment Status of Previous Credit"].map(PREVIOUS_DEFAULTS_MAP)
    out["number_of_open_accounts"] = raw["No of Credits at this Bank"].astype(int)
    out["loan_purpose"] = raw["Purpose"].map(PURPOSE_MAP)
    # Creditability: 1 = Good (700 rows), 0 = Bad (300 rows) in this source file.
    out["defaulted"] = (raw["Creditability"] == 0).astype(int)

    return out


def _apply_drift_simulation(production: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """
    Disclosed synthetic drift layer applied to the production slice's FEATURE
    columns only — simulates ~6-12 months of portfolio drift (larger loans,
    slightly older/more indebted applicant mix) so the app's drift-detection
    and model-health features have something real to detect. The `defaulted`
    label is untouched (real historical outcome for that row).
    """
    production = production.copy()
    n = len(production)
    production["loan_amount"] = production["loan_amount"] * rng.normal(1.18, 0.05, n)
    production["age"] = (production["age"] - rng.integers(0, 4, n)).clip(lower=18)
    production["debt_to_income_ratio"] = (production["debt_to_income_ratio"] * rng.normal(1.25, 0.08, n)).clip(upper=0.9)
    production["previous_defaults"] = (production["previous_defaults"] + rng.choice([0, 0, 0, 1], n)).clip(upper=3)
    production["employment_years"] = (production["employment_years"] * rng.normal(0.75, 0.1, n)).clip(lower=0)
    return production


def main() -> None:
    df = build()
    rng = np.random.default_rng(RANDOM_STATE + 1)

    # 70/30 split: "baseline" = original training-era distribution,
    # "production" = held-out slice standing in for newer applicants, with a
    # disclosed drift simulation applied (see _apply_drift_simulation docstring).
    shuffled = df.sample(frac=1.0, random_state=RANDOM_STATE).reset_index(drop=True)
    split_idx = int(len(shuffled) * 0.7)
    baseline, production = shuffled.iloc[:split_idx], shuffled.iloc[split_idx:]
    production = _apply_drift_simulation(production, rng)

    baseline.to_csv(BASELINE_OUT, index=False)
    production.to_csv(PRODUCTION_OUT, index=False)

    print(f"Baseline:   {len(baseline)} rows -> {BASELINE_OUT}")
    print(f"Production: {len(production)} rows -> {PRODUCTION_OUT}")
    print(f"Overall default rate: {df['defaulted'].mean():.1%}")
    print(f"credit_score range: {df['credit_score'].min()}-{df['credit_score'].max()}, "
          f"mean {df['credit_score'].mean():.0f}")
    print(f"income range: {df['income'].min():.0f}-{df['income'].max():.0f}, "
          f"mean {df['income'].mean():.0f}")


if __name__ == "__main__":
    main()
