# FinWise AI — Personal Financial Analysis & Smart Budget Assistant

A modular, Streamlit-based educational FinTech prototype with deterministic financial calculations and LangChain-powered OpenAI insights.

> **Educational use only.** Not financial or investment advice. Consult a qualified financial professional. Never enter banking credentials or other sensitive data.

## Features
- Responsive dark-themed dashboard, ten expense categories, financial goals and six currencies
- Python-computed ratios, weighted score and risk (not determined by the model)
- OpenAI ChatOpenAI, PromptTemplate, ChatPromptTemplate, SystemMessage / HumanMessage / AIMessage demonstration
- Reusable modern LangChain RunnableSequence (the supported successor to the deprecated `LLMChain` class)
- Strict JSON schema validation and streamed recommendations via `.stream()` + `st.write_stream()`
- Selectable in-memory / SQLite / disabled LLM caching
- CSV monthly expense comparisons, charts, goal tracker, JSON and PDF reports
- Docker deployment and pytest scenarios

## Run locally
Requires Python 3.10+ (recommended 3.11).

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# Copy .env.example to .env and set OPENAI_API_KEY
streamlit run app.py
```

Without an API key the financial calculator, charts and report downloads still work; AI analysis requires an OpenAI API key and API billing access.

## Streamlit Community Cloud deployment
1. Create a GitHub repository and upload the contents of this folder.
2. Open https://share.streamlit.io/ and choose **Create app** → repository → branch → `app.py`.
3. Under **Advanced settings / Secrets**, enter `OPENAI_API_KEY = "your_key_here"`.
4. Deploy. Never commit `.env` or `.streamlit/secrets.toml`.
5. Test a sample analysis, streaming, report download and reset button. The deployment URL is supplied by Streamlit after deployment.

**Note:** SQLite cache files on ephemeral Streamlit Cloud storage can disappear after restarts. Use Memory cache for simple cloud deployments. This is a single-user educational prototype, not a secure multi-user finance service.

## Docker
```bash
docker build -t finwise-ai .
docker run --rm -p 8501:8501 -e OPENAI_API_KEY=your_key finwise-ai
```
Open http://localhost:8501.

## Tests
```bash
pytest -q
```
Tests cover the five assignment scenarios, zero income, invalid negatives, and JSON score/risk validation. Live AI calls are not made by automated tests.

## Architecture
- `app.py`: Streamlit UI, visualization, exports and session state
- `src/config.py`: dropdown options, disclaimer, environment loading
- `src/financial_calculator.py`: deterministic totals, ratios, score, risk
- `src/prompts.py`: single-string and chat prompts, strict JSON instructions
- `src/chains.py`: ChatOpenAI, reusable prompt/model/parser chain, streaming, message demo
- `src/cache_manager.py`: LangChain global in-memory or SQLite cache
- `src/utils.py`: Pydantic validation and safe JSON parsing
- `tests/`: deterministic tests

## Calculation details
`total_expenses = sum(categories)`; `remaining = income - expenses`; savings and expense ratios use income as denominator, with zero-income safeguards. Score (0–100) is a transparent heuristic: savings ratio up to 30 points (full at 20%); expense burden up to 30; positive remaining up to 20; low debt burden up to 20. Risk classification also flags deficits, zero income and high debt. The AI receives these numbers but is required to reproduce the score and risk exactly; mismatches are rejected.

**Savings caveat:** Current monthly savings is entered separately and is not added to expense totals; enter consistently to avoid double-counting. Currencies are display labels only; no FX conversion is performed.

## Caching and AI
`set_llm_cache(InMemoryCache())` is fastest and resets with process restarts. `SQLiteCache` persists to `.cache/langchain.db` when disk is persistent. Cache may reduce repeat API calls. The narrative uses live model streaming, so repeat streaming behavior depends on LangChain/model cache support. Structured AI insights are validated against the exact output schema using Pydantic.

## Submission / demo script
1. Show sidebar, disclaimer and configuration.
2. Run a positive-income example; demonstrate financial metrics and charts.
3. Click **Generate structured AI insights**, show tabs, then **Stream live next-month recommendations**.
4. Show CSV history, goal tracker and PDF/JSON export.
5. Demonstrate cache switch, session reset and the negative-income scenario.
6. Record a 2–4 minute screen demo; submit the GitHub repository and deployed app URL.

## Assignment alignment
All 100-mark rubric areas are implemented, with one deliberate modern compatibility choice: `LLMChain` has been deprecated in modern LangChain, so the project implements its reusable equivalent with `ChatPromptTemplate | ChatOpenAI | StrOutputParser`. If your instructor strictly requires the literal legacy `LLMChain` class, discuss this version difference before submission.

## Privacy and safety
The app does not connect to banks, execute transactions, promise outcomes or provide personalized investment recommendations. Submitted figures are transmitted to OpenAI when AI analysis is requested. Avoid sensitive details. The project does not implement user authentication, encrypted account storage or production compliance controls.

## Alternative entry point
Run `streamlit run finwise.py` if your instructor expects a file named finwise.py. Keep the entire project folder including `src/`; the file is a launcher, not a standalone application.

## Security and deployment limits
Financial inputs sent to OpenAI for AI analysis. No bank connectivity or payments. SQLite cache may store model prompts including financial amounts on local disk; avoid shared hosting or disable persistent cache. The theme selector is informational; change actual appearance in Streamlit's Settings menu.
