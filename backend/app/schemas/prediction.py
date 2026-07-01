from pydantic import BaseModel, Field


class ApplicantFeatures(BaseModel):
    age: int = Field(..., ge=18, le=100)
    income: float = Field(..., ge=0)
    credit_score: int = Field(..., ge=300, le=850)
    loan_amount: float = Field(..., ge=0)
    loan_term_months: int = Field(..., ge=1)
    employment_years: float = Field(..., ge=0)
    debt_to_income_ratio: float = Field(..., ge=0)
    previous_defaults: int = Field(..., ge=0)
    number_of_open_accounts: int = Field(..., ge=0)
    loan_purpose: str


class PredictionRequest(BaseModel):
    applicant_id: str
    features: ApplicantFeatures


class TopRiskFactor(BaseModel):
    factor: str
    severity: str
    value: float | int | str | None = None
    message: str


class PredictionResponse(BaseModel):
    applicant_id: str
    default_probability: float
    risk_class: str
    reason_codes: list[str]
    explanation_text: str
    top_risk_factors: list[TopRiskFactor]
    model_version: str
