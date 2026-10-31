"""Convenient entry point: streamlit run finwise.py."""
from pathlib import Path
exec(compile((Path(__file__).parent / "app.py").read_text(encoding="utf-8"), str(Path(__file__).parent / "app.py"), "exec"))
