"""LangChain RunnableSequence is the supported replacement for deprecated LLMChain."""
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from .prompts import CHAT_PROMPT, NARRATIVE_CHAT_TEMPLATE
from .utils import parse_analysis

def make_llm(model='gpt-4o-mini', temperature=0.2):
    return ChatOpenAI(model=model, temperature=temperature, max_retries=2, timeout=60)

def build_llm_chain(llm):
    """Reusable LLMChain-equivalent: prompt | model | parser."""
    return CHAT_PROMPT | llm | StrOutputParser()

def run_analysis(llm, inputs, metrics):
    raw = build_llm_chain(llm).invoke(inputs)
    return parse_analysis(raw, metrics['preliminary_score'], metrics['risk_level'])

def stream_recommendations(llm, inputs):
    messages = NARRATIVE_CHAT_TEMPLATE.format_messages(**inputs)
    for chunk in llm.stream(messages):
        if chunk.content:
            yield chunk.content if isinstance(chunk.content,str) else str(chunk.content)

def message_demo():
    return [SystemMessage(content='Educational financial assistant.'),HumanMessage(content='How can I improve my budget?'),AIMessage(content='Track expenses and set a realistic savings goal.')]
