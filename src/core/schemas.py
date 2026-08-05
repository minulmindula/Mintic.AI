from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class TradeProposal(BaseModel):
    """Pydantic model representing a trade proposal submitted for safety verification."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    symbol: str = Field(
        ...,
        min_length=1,
        description="Ticker symbol for the trade (e.g. AAPL, VOD.L)",
    )
    action: Literal["BUY", "SELL"] = Field(
        ...,
        description="Action to execute: BUY or SELL",
    )
    quantity: float = Field(
        ...,
        gt=0,
        description="Quantity of asset units to trade, strictly greater than zero",
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0",
    )
    target_price: float = Field(
        ...,
        gt=0,
        description="Target execution price per unit in GBP, strictly greater than zero",
    )
    stop_loss: float = Field(
        ...,
        gt=0,
        description="Stop loss price per unit in GBP, strictly greater than zero",
    )
    reasoning_summary: str = Field(
        ...,
        min_length=1,
        description="Brief summary explaining the rationale behind the trade proposal",
    )


class SafetyCheckResult(BaseModel):
    """Pydantic model representing the result of evaluating an UnbendableSafetyLock check."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    is_approved: bool = Field(
        ...,
        description="True if all safety checks pass, False if any safety check fails",
    )
    reason: str = Field(
        ...,
        description="Human-readable summary of the safety check evaluation",
    )
    proposal: TradeProposal = Field(
        ...,
        description="The trade proposal that was evaluated",
    )
    failed_checks: list[str] = Field(
        default_factory=list,
        description="List of specific safety rule violations, if any",
    )
