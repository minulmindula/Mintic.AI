from typing import Any, Optional

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

import os

from src.agents.state import DeliberationState
from src.config import settings
from src.core.schemas import TradeProposal


def get_default_llm() -> ChatGoogleGenerativeAI:
    """Helper function to instantiate ChatGoogleGenerativeAI with gemini-1.5-flash."""
    api_key = (
        settings.GEMINI_API_KEY
        or settings.GOOGLE_API_KEY
        or os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or ""
    )
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
        os.environ["GOOGLE_API_KEY"] = api_key

    kwargs: dict[str, Any] = {
        "model": "gemini-1.5-flash",
        "temperature": 0.2,
    }
    if api_key:
        kwargs["google_api_key"] = api_key
        kwargs["api_key"] = api_key

    return ChatGoogleGenerativeAI(**kwargs)


def analyst_node(
    state: DeliberationState, llm: Optional[Any] = None
) -> dict[str, Any]:
    """
    Analyst agent node: Evaluates market data and account state to synthesize a baseline market report.

    Args:
        state: Current DeliberationState.
        llm: Optional ChatGoogleGenerativeAI instance for dependency injection/testing.

    Returns:
        Dictionary updating analyst_report state key.
    """
    model = llm or get_default_llm()
    messages = [
        SystemMessage(
            content=(
                "You are an expert financial analyst. Analyze the provided market data "
                "and account state to synthesize a concise, objective market analysis report."
            )
        ),
        HumanMessage(
            content=(
                f"Symbol: {state.get('symbol')}\n"
                f"Market Data: {state.get('market_data')}\n"
                f"Account State: {state.get('account_state')}"
            )
        ),
    ]
    response = model.invoke(messages)
    content_str = str(getattr(response, "content", response))
    return {"analyst_report": content_str}


def bull_node(
    state: DeliberationState, llm: Optional[Any] = None
) -> dict[str, Any]:
    """
    Bull agent node: Analyzes the analyst report to construct a compelling bullish thesis.

    Args:
        state: Current DeliberationState.
        llm: Optional ChatGoogleGenerativeAI instance for dependency injection/testing.

    Returns:
        Dictionary updating bull_hypothesis state key.
    """
    model = llm or get_default_llm()
    messages = [
        SystemMessage(
            content=(
                "You are a bullish market researcher. Formulate a strong bullish argument "
                "highlighting upside potential and catalyst triggers based on the analyst report."
            )
        ),
        HumanMessage(
            content=(
                f"Symbol: {state.get('symbol')}\n"
                f"Analyst Report: {state.get('analyst_report')}"
            )
        ),
    ]
    response = model.invoke(messages)
    content_str = str(getattr(response, "content", response))
    return {"bull_hypothesis": content_str}


def bear_node(
    state: DeliberationState, llm: Optional[Any] = None
) -> dict[str, Any]:
    """
    Bear agent node: Analyzes the analyst report to construct a critical bearish thesis and risk assessment.

    Args:
        state: Current DeliberationState.
        llm: Optional ChatGoogleGenerativeAI instance for dependency injection/testing.

    Returns:
        Dictionary updating bear_hypothesis state key.
    """
    model = llm or get_default_llm()
    messages = [
        SystemMessage(
            content=(
                "You are a cautious bearish risk analyst. Formulate a detailed bearish argument "
                "highlighting downside risks, resistance levels, and potential failure points."
            )
        ),
        HumanMessage(
            content=(
                f"Symbol: {state.get('symbol')}\n"
                f"Analyst Report: {state.get('analyst_report')}"
            )
        ),
    ]
    response = model.invoke(messages)
    content_str = str(getattr(response, "content", response))
    return {"bear_hypothesis": content_str}


def risk_manager_node(
    state: DeliberationState, llm: Optional[Any] = None
) -> dict[str, Any]:
    """
    Risk Manager agent node: Weighs bull and bear hypotheses to issue a final structured TradeProposal.

    Args:
        state: Current DeliberationState.
        llm: Optional ChatGoogleGenerativeAI instance for dependency injection/testing.

    Returns:
        Dictionary updating final_proposal state key with a TradeProposal instance.
    """
    model = llm or get_default_llm()
    structured_llm = model.with_structured_output(TradeProposal)

    messages = [
        SystemMessage(
            content=(
                "You are the Chief Risk Officer. Review the analyst report, bullish thesis, "
                "and bearish thesis to issue a final, highly disciplined TradeProposal in structured JSON format."
            )
        ),
        HumanMessage(
            content=(
                f"Symbol: {state.get('symbol')}\n"
                f"Analyst Report: {state.get('analyst_report')}\n"
                f"Bull Hypothesis: {state.get('bull_hypothesis')}\n"
                f"Bear Hypothesis: {state.get('bear_hypothesis')}\n"
                f"Market Data: {state.get('market_data')}\n"
                f"Account State: {state.get('account_state')}"
            )
        ),
    ]
    proposal: TradeProposal = structured_llm.invoke(messages)
    return {"final_proposal": proposal}
