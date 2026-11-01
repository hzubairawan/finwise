"""Deterministic financial calculations; never calls an AI model."""
from dataclasses import dataclass, asdict

@dataclass
class FinancialMetrics:
    monthly_income: float
    total_expenses: float
    remaining_income: float
    savings: float
    savings_ratio: float
    expense_ratio: float
    debt_ratio: float
    preliminary_score: int
    risk_level: str

def calculate(income: float, expenses: dict[str,float], savings: float) -> dict:
    if income < 0 or savings < 0 or any(v < 0 for v in expenses.values()):
        raise ValueError('Income, savings and expenses must be non-negative.')
    total = round(sum(expenses.values()), 2)
    remaining = round(income-total, 2)
    savings_ratio = savings/income*100 if income else 0
    expense_ratio = total/income*100 if income else (100 if total else 0)
    debt_ratio = expenses.get('Loan / Debt',0)/income*100 if income else (100 if expenses.get('Loan / Debt',0) else 0)
    # Transparent weighted heuristic: savings 30, expense load 30, remaining 20, debt burden 20.
    savings_component = min(savings_ratio/20, 1)*30
    expense_component = max(0, 1-expense_ratio/100)*30
    remaining_component = max(0, min(remaining/income,1))*20 if income else 0
    debt_component = max(0, 1-debt_ratio/40)*20 if income else 0
    score = round(max(0,min(100,savings_component+expense_component+remaining_component+debt_component)))
    if income == 0 or remaining < 0 or expense_ratio > 100 or debt_ratio >= 50:
        risk = 'HIGH'
    elif remaining == 0 or expense_ratio >= 90 or debt_ratio >= 30 or score < 40:
        risk = 'HIGH' if score < 40 else 'MEDIUM'
    elif score < 60 or debt_ratio >= 20 or expense_ratio >= 75:
        risk = 'MEDIUM'
    else:
        risk = 'LOW'
    return asdict(FinancialMetrics(income,total,remaining,savings,round(savings_ratio,2),round(expense_ratio,2),round(debt_ratio,2),score,risk))

def score_band(score: int) -> str:
    if score >= 80: return 'Strong'
    if score >= 60: return 'Generally healthy'
    if score >= 40: return 'Needs improvement'
    return 'High attention'
