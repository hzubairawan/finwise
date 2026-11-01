import json
import re
from pydantic import BaseModel, Field, ConfigDict, ValidationError

class SpendingItem(BaseModel):
    model_config = ConfigDict(extra='forbid')
    category: str
    observation: str
    recommendation: str

class Analysis(BaseModel):
    model_config = ConfigDict(extra='forbid')
    financial_summary: str
    financial_health_score: int = Field(ge=0,le=100)
    spending_analysis: list[SpendingItem]
    risk_level: str
    top_priorities: list[str]
    budget_recommendations: list[str]
    savings_strategy: list[str]
    next_month_action_plan: list[str]

def parse_analysis(text: str, expected_score: int, expected_risk: str) -> dict:
    cleaned = re.sub(r'^```(?:json)?\s*|\s*```$', '', text.strip(), flags=re.I)
    result = Analysis.model_validate(json.loads(cleaned))
    if result.financial_health_score != expected_score or result.risk_level != expected_risk:
        raise ValueError('AI score or risk disagrees with deterministic calculations.')
    return result.model_dump()
