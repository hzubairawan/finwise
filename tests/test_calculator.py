from src.financial_calculator import calculate, score_band
from src.utils import parse_analysis
import json
import pytest

def test_five_assignment_scenarios():
    scenarios=[(8000,{'Food':2000},1000,'LOW'),(2000,{'Food':2600},0,'HIGH'),(5000,{'Loan / Debt':2500},100,'HIGH'),(4000,{'Food':800},1200,'LOW'),(3000,{'Food':3000},0,'HIGH')]
    for income,expenses,savings,risk in scenarios:
        result=calculate(income,expenses,savings)
        assert result['total_expenses']==sum(expenses.values())
        assert result['remaining_income']==income-sum(expenses.values())
        assert result['risk_level']==risk
        assert 0<=result['preliminary_score']<=100

def test_zero_income_and_validation():
    assert calculate(0,{},0)['savings_ratio']==0
    assert calculate(0,{'Food':100},0)['risk_level']=='HIGH'
    with pytest.raises(ValueError): calculate(100,{'Food':-1},0)

def test_json_validation():
    payload={'financial_summary':'Example','financial_health_score':50,'spending_analysis':[],'risk_level':'MEDIUM','top_priorities':[],'budget_recommendations':[],'savings_strategy':[],'next_month_action_plan':[]}
    assert parse_analysis(json.dumps(payload),50,'MEDIUM')['financial_health_score']==50
    with pytest.raises(ValueError): parse_analysis(json.dumps(payload),70,'MEDIUM')
