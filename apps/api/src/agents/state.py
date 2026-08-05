from typing import Any, Optional, TypedDict

from src.core.schemas import TradeProposal


class DeliberationState(TypedDict):
    """
    TypedDict defining the shared state across nodes in the multi-agent deliberation graph.
    """

    symbol: str
    market_data: dict[str, Any]
    account_state: dict[str, Any]
    analyst_report: str
    bull_hypothesis: str
    bear_hypothesis: str
    final_proposal: Optional[TradeProposal]
