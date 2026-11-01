from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from .config import DISCLAIMER

FINANCIAL_TEMPLATE = '''Monthly income: {monthly_income}; total expenses: {total_expenses}; remaining income: {remaining_income}; savings: {savings}; savings ratio: {savings_ratio}%; expense ratio: {expense_ratio}%; goal: {financial_goal}; expense breakdown: {expense_breakdown}.'''
FINANCIAL_PROMPT = PromptTemplate.from_template(FINANCIAL_TEMPLATE)
SYSTEM_TEXT = '''You are FinWise AI, an educational budgeting assistant. {disclaimer}
Never recommend particular investments, promise returns, execute transactions, or request sensitive financial credentials.
Only use the user's supplied figures. Never change the deterministic calculations.
Return a single JSON object with EXACTLY these keys and types:
{{"financial_summary":"string","financial_health_score":0,"spending_analysis":[{{"category":"string","observation":"string","recommendation":"string"}}],"risk_level":"LOW","top_priorities":["string"],"budget_recommendations":["string"],"savings_strategy":["string"],"next_month_action_plan":["string"]}}.
financial_health_score MUST equal the preliminary_score supplied. risk_level MUST equal the supplied risk_level. Avoid currency conversion. Use constructive practical language. Output JSON only.'''
CHAT_PROMPT = ChatPromptTemplate.from_messages([('system',SYSTEM_TEXT),('human',FINANCIAL_TEMPLATE+'\nPreliminary score: {preliminary_score}; rule-based risk level: {risk_level}; currency: {currency}.')]).partial(disclaimer=DISCLAIMER)
NARRATIVE_CHAT_TEMPLATE = ChatPromptTemplate.from_messages([('system','You are an educational budgeting coach. '+DISCLAIMER+' Keep advice actionable, cautious and concise. No investment product advice.'),('human',FINANCIAL_TEMPLATE+'\nRule-based score: {preliminary_score}; risk: {risk_level}; currency: {currency}. Provide 4 short practical next-month steps.')])
