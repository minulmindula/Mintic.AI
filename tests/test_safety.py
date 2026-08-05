import pytest
from pydantic import ValidationError

from src.config import Settings
from src.core.safety import UnbendableSafetyLock
from src.core.schemas import SafetyCheckResult, TradeProposal


@pytest.fixture
def custom_settings() -> Settings:
    """Fixture returning custom risk settings for testing."""
    return Settings(
        ALLOWED_SYMBOLS={"AAPL", "GOOGL", "MSFT", "NVDA"},
        MAX_POSITION_SIZE_GBP=10000.0,
        MIN_CONFIDENCE_THRESHOLD=0.70,
        MAX_DAILY_DRAWDOWN_PERCENT=5.0,
    )


@pytest.fixture
def safety_lock(custom_settings: Settings) -> UnbendableSafetyLock:
    """Fixture returning an UnbendableSafetyLock instance with custom settings."""
    return UnbendableSafetyLock(config=custom_settings)


def test_valid_trade_approval(safety_lock: UnbendableSafetyLock) -> None:
    """Verify that a valid trade proposal passing all safety checks is approved."""
    proposal = TradeProposal(
        symbol="AAPL",
        action="BUY",
        quantity=20.0,
        confidence_score=0.85,
        target_price=180.0,  # 20 * 180 = £3,600 GBP position size
        stop_loss=170.0,
        reasoning_summary="Strong earnings momentum indicator",
    )
    result: SafetyCheckResult = safety_lock.validate_trade(
        proposal=proposal, current_daily_drawdown_percent=2.0
    )

    assert result.is_approved is True
    assert result.reason == "All safety checks passed."
    assert len(result.failed_checks) == 0
    assert result.proposal == proposal


def test_rejected_unwhitelisted_symbol(safety_lock: UnbendableSafetyLock) -> None:
    """Verify that a trade proposal for a non-whitelisted symbol is rejected."""
    proposal = TradeProposal(
        symbol="UNWANTED_TICKER",
        action="BUY",
        quantity=100.0,
        confidence_score=0.90,
        target_price=10.0,  # £1,000 position size
        stop_loss=8.0,
        reasoning_summary="Speculative unwhitelisted stock",
    )
    result: SafetyCheckResult = safety_lock.validate_trade(
        proposal=proposal, current_daily_drawdown_percent=0.0
    )

    assert result.is_approved is False
    assert len(result.failed_checks) == 1
    assert "UNWANTED_TICKER" in result.failed_checks[0]
    assert "not in allowed whitelist" in result.failed_checks[0]


def test_rejected_oversized_position(safety_lock: UnbendableSafetyLock) -> None:
    """Verify that a trade proposal exceeding MAX_POSITION_SIZE_GBP is rejected."""
    proposal = TradeProposal(
        symbol="AAPL",
        action="BUY",
        quantity=100.0,
        confidence_score=0.90,
        target_price=150.0,  # 100 * 150 = £15,000 GBP > £10,000 limit
        stop_loss=140.0,
        reasoning_summary="Oversized position attempt",
    )
    result: SafetyCheckResult = safety_lock.validate_trade(
        proposal=proposal, current_daily_drawdown_percent=1.0
    )

    assert result.is_approved is False
    assert len(result.failed_checks) == 1
    assert "exceeds maximum threshold" in result.failed_checks[0]


def test_rejected_low_confidence_score(safety_lock: UnbendableSafetyLock) -> None:
    """Verify that a trade proposal below MIN_CONFIDENCE_THRESHOLD is rejected."""
    proposal = TradeProposal(
        symbol="GOOGL",
        action="BUY",
        quantity=10.0,
        confidence_score=0.55,  # 0.55 < 0.70 threshold
        target_price=140.0,
        stop_loss=130.0,
        reasoning_summary="Low confidence setup",
    )
    result: SafetyCheckResult = safety_lock.validate_trade(
        proposal=proposal, current_daily_drawdown_percent=1.0
    )

    assert result.is_approved is False
    assert len(result.failed_checks) == 1
    assert "Confidence score 0.55 is below minimum threshold" in result.failed_checks[0]


def test_rejected_excessive_daily_drawdown(safety_lock: UnbendableSafetyLock) -> None:
    """Verify that a trade proposal is rejected when current drawdown exceeds MAX_DAILY_DRAWDOWN_PERCENT."""
    proposal = TradeProposal(
        symbol="MSFT",
        action="BUY",
        quantity=10.0,
        confidence_score=0.80,
        target_price=400.0,  # £4,000 position size
        stop_loss=380.0,
        reasoning_summary="Stock trade during high portfolio drawdown",
    )
    result: SafetyCheckResult = safety_lock.validate_trade(
        proposal=proposal, current_daily_drawdown_percent=6.5  # 6.5% > 5.0% limit
    )

    assert result.is_approved is False
    assert len(result.failed_checks) == 1
    assert "Current daily drawdown 6.50% exceeds maximum limit" in result.failed_checks[0]


def test_multiple_safety_violations(safety_lock: UnbendableSafetyLock) -> None:
    """Verify that multiple safety rule violations are all captured in failed_checks."""
    proposal = TradeProposal(
        symbol="PENNY_STOCK",  # Violation 1: Unwhitelisted
        action="BUY",
        quantity=100.0,
        confidence_score=0.40,  # Violation 2: Low confidence
        target_price=200.0,  # £20,000 GBP position size -> Violation 3: Oversized
        stop_loss=180.0,
        reasoning_summary="Highly risky multi-violation trade",
    )
    result: SafetyCheckResult = safety_lock.validate_trade(
        proposal=proposal, current_daily_drawdown_percent=8.0  # Violation 4: High drawdown
    )

    assert result.is_approved is False
    assert len(result.failed_checks) == 4


# Pydantic Schema Unit Validation Tests


def test_trade_proposal_invalid_quantity() -> None:
    """Verify Pydantic validation fails for zero or negative quantity."""
    with pytest.raises(ValidationError):
        TradeProposal(
            symbol="AAPL",
            action="BUY",
            quantity=0.0,
            confidence_score=0.80,
            target_price=180.0,
            stop_loss=170.0,
            reasoning_summary="Invalid zero quantity",
        )


def test_trade_proposal_invalid_confidence_score() -> None:
    """Verify Pydantic validation fails for out-of-bounds confidence scores (>1.0 or <0.0)."""
    with pytest.raises(ValidationError):
        TradeProposal(
            symbol="AAPL",
            action="BUY",
            quantity=10.0,
            confidence_score=1.5,
            target_price=180.0,
            stop_loss=170.0,
            reasoning_summary="Invalid confidence score above 1.0",
        )

    with pytest.raises(ValidationError):
        TradeProposal(
            symbol="AAPL",
            action="BUY",
            quantity=10.0,
            confidence_score=-0.1,
            target_price=180.0,
            stop_loss=170.0,
            reasoning_summary="Invalid negative confidence score",
        )


def test_trade_proposal_invalid_action() -> None:
    """Verify Pydantic validation fails for actions other than BUY or SELL."""
    with pytest.raises(ValidationError):
        TradeProposal(
            symbol="AAPL",
            action="HOLD",  # type: ignore[arg-type]
            quantity=10.0,
            confidence_score=0.80,
            target_price=180.0,
            stop_loss=170.0,
            reasoning_summary="Invalid action HOLD",
        )


def test_trade_proposal_invalid_prices() -> None:
    """Verify Pydantic validation fails for target_price or stop_loss <= 0."""
    with pytest.raises(ValidationError):
        TradeProposal(
            symbol="AAPL",
            action="BUY",
            quantity=10.0,
            confidence_score=0.80,
            target_price=-500.0,
            stop_loss=170.0,
            reasoning_summary="Invalid negative target price",
        )
