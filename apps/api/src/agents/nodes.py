import os
from typing import Any, Optional, cast

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.agents.state import DeliberationState
from src.config import settings
from src.core.schemas import TradeProposal

# Prioritized list of active Gemini models
GEMINI_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-3-flash-preview",
    "gemini-3.8-flash",
]


def _get_api_key() -> str:
    """Retrieves and normalizes Gemini API key from environment."""
    from dotenv import load_dotenv

    load_dotenv(override=True)
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or settings.GEMINI_API_KEY
        or settings.GOOGLE_API_KEY
        or ""
    ).strip()

    if not api_key:
        for env_path in ["/app/.env", ".env", "apps/api/.env"]:
            if os.path.exists(env_path):
                from dotenv import dotenv_values

                vals = dotenv_values(env_path)
                api_key = (
                    vals.get("GEMINI_API_KEY") or vals.get("GOOGLE_API_KEY") or ""
                ).strip()
                if api_key:
                    break

    if not api_key:
        raise ValueError(
            "API key required for Gemini Developer API. Please set GEMINI_API_KEY in environment."
        )

    os.environ["GEMINI_API_KEY"] = api_key
    os.environ["GOOGLE_API_KEY"] = api_key
    return api_key


def get_default_llm(model_name: Optional[str] = None) -> ChatGoogleGenerativeAI:
    """Helper function to instantiate ChatGoogleGenerativeAI with active Gemini model."""
    api_key = _get_api_key()
    chosen_model = model_name or os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    return ChatGoogleGenerativeAI(
        model=chosen_model,
        temperature=0.2,
        google_api_key=api_key,
        api_key=api_key,
        max_retries=2,
    )


def _extract_text(content: Any) -> str:
    """Extracts clean text string from LangChain / Gemini response content."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            elif hasattr(item, "text"):
                parts.append(str(item.text))
        if parts:
            return "\n\n".join(parts)
    if hasattr(content, "content"):
        return _extract_text(content.content)
    return str(content)


def _invoke_with_fallback(
    messages: list[Any], default_llm: Optional[Any] = None
) -> str:
    """Invokes LLM with automatic fallback across available Gemini model candidates."""
    if default_llm is not None:
        resp = default_llm.invoke(messages)
        return _extract_text(getattr(resp, "content", resp))

    last_error: Optional[Exception] = None
    for model_name in GEMINI_MODELS:
        try:
            llm = get_default_llm(model_name=model_name)
            resp = llm.invoke(messages)
            return _extract_text(getattr(resp, "content", resp))
        except Exception as err:
            last_error = err
            continue

    if last_error:
        raise last_error
    raise RuntimeError("Failed to invoke Gemini models across all fallbacks.")


def analyst_node(
    state: DeliberationState, llm: Optional[Any] = None
) -> dict[str, Any]:
    """
    Analyst agent node: Evaluates market data, Google News, and technicals.
    Generates a concise, short, to-the-point report with 24h High/Low, multi-day prediction (Rise/Fall timing),
    and an actionable investment suggestion.
    """
    symbol = state.get("symbol", "UNKNOWN")
    market_data = state.get("market_data", {})
    account_state = state.get("account_state", {})

    messages = [
        SystemMessage(
            content=(
                "You are an elite quantitative financial analyst for Mintic.AI. "
                "Synthesize a CONCISE, DIRECT, and HIGH-IMPACT Market Report (strictly under 130 words). "
                "Do NOT write long essays or wordy filler paragraphs. Use clear bullet points:\n"
                "• **Price & Range:** State current price, 24h Low, and 24h High.\n"
                "• **News & Sentiment:** 1-sentence synthesis of breaking news from Google News.\n"
                "• **Multi-Day Prediction (Rise / Fall):** Explicit prediction on whether the asset tends to RISE or FALL over the next 2-5 days, with key target and support levels.\n"
                "• **Investment Suggestion:** Clear verdict: 'INVEST / BUY (Accumulate)' vs 'HOLD / WAIT' vs 'AVOID / DOWNWARD CORRECTION'."
            )
        ),
        HumanMessage(
            content=(
                f"Asset: {symbol}\n"
                f"Live Market Data: {market_data}\n"
                f"Account: {account_state}"
            )
        ),
    ]

    report = _invoke_with_fallback(messages, default_llm=llm)
    return {"analyst_report": report}


def bull_node(
    state: DeliberationState, llm: Optional[Any] = None
) -> dict[str, Any]:
    """
    Bull agent node: Constructs a short, punchy bullish thesis (under 80 words).
    """
    symbol = state.get("symbol", "UNKNOWN")
    analyst_report = state.get("analyst_report", "")
    market_data = state.get("market_data", {})

    messages = [
        SystemMessage(
            content=(
                "You are a strategic bullish market researcher. "
                "Formulate a SHORT, PUNCHY Bullish Hypothesis (under 80 words, 3 bullets max):\n"
                "• **Upside Catalyst:** Key news/technical driver triggering buying pressure.\n"
                "• **Rise Target & Timing:** Specific upside target and timeframe (e.g. Rise toward $X over next 3-5 days).\n"
                "• **Buy Trigger:** Breakout confirmation level."
            )
        ),
        HumanMessage(
            content=(
                f"Asset: {symbol}\n"
                f"Metrics: {market_data}\n"
                f"Analyst Report: {analyst_report}"
            )
        ),
    ]

    bull_text = _invoke_with_fallback(messages, default_llm=llm)
    return {"bull_hypothesis": bull_text}


def bear_node(
    state: DeliberationState, llm: Optional[Any] = None
) -> dict[str, Any]:
    """
    Bear agent node: Constructs a short, punchy bearish risk assessment (under 80 words).
    """
    symbol = state.get("symbol", "UNKNOWN")
    analyst_report = state.get("analyst_report", "")
    market_data = state.get("market_data", {})

    messages = [
        SystemMessage(
            content=(
                "You are a disciplined bearish risk analyst. "
                "Formulate a SHORT, PUNCHY Bearish Risk Assessment (under 80 words, 3 bullets max):\n"
                "• **Downside Vulnerability:** Key overhead resistance or negative news friction.\n"
                "• **Fall Target & Breakdown:** Specific pullback level if support fails over the coming days.\n"
                "• **Stop-Loss / Invalidation:** Exact capital preservation stop-loss price."
            )
        ),
        HumanMessage(
            content=(
                f"Asset: {symbol}\n"
                f"Metrics: {market_data}\n"
                f"Analyst Report: {analyst_report}"
            )
        ),
    ]

    bear_text = _invoke_with_fallback(messages, default_llm=llm)
    return {"bear_hypothesis": bear_text}


def risk_manager_node(
    state: DeliberationState, llm: Optional[Any] = None
) -> dict[str, Any]:
    """
    Risk Manager agent node: Weighs bull and bear hypotheses to issue a final structured TradeProposal.
    Enforces strict Safety Lock position sizing (maximum position size <= £5,000) and confidence >= 0.72.
    """
    symbol = state.get("symbol", "UNKNOWN")
    analyst_report = state.get("analyst_report", "")
    bull_hypothesis = state.get("bull_hypothesis", "")
    bear_hypothesis = state.get("bear_hypothesis", "")
    market_data = state.get("market_data", {})
    account_state = state.get("account_state", {})

    messages = [
        SystemMessage(
            content=(
                "You are the Chief Risk Officer for Mintic.AI. Issue a final disciplined TradeProposal in structured JSON format.\n"
                "- Action: 'BUY' if upside potential and catalysts dominate, 'SELL' if downside risks dominate.\n"
                "- CRITICAL SAFETY RULE (MANDATORY): Position value (quantity * target_price) must NOT exceed £5,000. Calculate quantity = round(min(5000.0 / target_price, 100.0), 4).\n"
                "- Confidence Score: Strictly between 0.72 and 0.95.\n"
                "- Target Price & Stop Loss: Realistic numbers aligned with the support/resistance discussed.\n"
                "- Reasoning Summary: A concise 2-sentence executive summary stating the investment suggestion, predicted rise/fall trajectory, and risk boundary."
            )
        ),
        HumanMessage(
            content=(
                f"Asset: {symbol}\n"
                f"Analyst Report: {analyst_report}\n"
                f"Bull: {bull_hypothesis}\n"
                f"Bear: {bear_hypothesis}\n"
                f"Market Data: {market_data}\n"
                f"Account State: {account_state}"
            )
        ),
    ]

    if llm is not None:
        structured_llm = llm.with_structured_output(TradeProposal)
        proposal = cast(TradeProposal, structured_llm.invoke(messages))
        return {"final_proposal": proposal}

    last_error: Optional[Exception] = None
    for model_name in GEMINI_MODELS:
        try:
            active_llm = get_default_llm(model_name=model_name)
            structured_llm = active_llm.with_structured_output(TradeProposal)
            proposal = cast(TradeProposal, structured_llm.invoke(messages))
            return {"final_proposal": proposal}
        except Exception as err:
            last_error = err
            continue

    if last_error:
        raise last_error
    raise RuntimeError("Failed to generate structured TradeProposal across all fallbacks.")
