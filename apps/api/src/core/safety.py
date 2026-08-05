from typing import Optional
from src.config import Settings, settings as default_settings
from src.core.schemas import SafetyCheckResult, TradeProposal


class UnbendableSafetyLock:
    """
    Deterministic Safety Lock for trade validation.

    CRITICAL RULE (GEMINI.md): Safety Lock logic in src/core/safety.py MUST NOT
    contain any LLM or AI dependencies.
    """

    def __init__(self, config: Optional[Settings] = None) -> None:
        """Initialize the UnbendableSafetyLock with specified risk parameters or defaults."""
        self.config: Settings = config or default_settings

    def validate_trade(
        self,
        proposal: TradeProposal,
        current_daily_drawdown_percent: float = 0.0,
    ) -> SafetyCheckResult:
        """
        Validates a trade proposal against hard risk boundaries.

        Args:
            proposal: The trade proposal to validate.
            current_daily_drawdown_percent: The current daily portfolio drawdown percentage.

        Returns:
            SafetyCheckResult indicating approval or list of risk rule violations.
        """
        failed_checks: list[str] = []

        # 1. Whitelist Check
        if proposal.symbol not in self.config.ALLOWED_SYMBOLS:
            failed_checks.append(
                f"Symbol '{proposal.symbol}' is not in allowed whitelist: "
                f"{sorted(list(self.config.ALLOWED_SYMBOLS))}"
            )

        # 2. Maximum Position Size GBP Check (quantity * target_price)
        position_size_gbp: float = proposal.quantity * proposal.target_price
        if position_size_gbp > self.config.MAX_POSITION_SIZE_GBP:
            failed_checks.append(
                f"Position size £{position_size_gbp:,.2f} exceeds maximum threshold of "
                f"£{self.config.MAX_POSITION_SIZE_GBP:,.2f}"
            )

        # 3. Minimum Confidence Score Check
        if proposal.confidence_score < self.config.MIN_CONFIDENCE_THRESHOLD:
            failed_checks.append(
                f"Confidence score {proposal.confidence_score:.2f} is below minimum threshold of "
                f"{self.config.MIN_CONFIDENCE_THRESHOLD:.2f}"
            )

        # 4. Maximum Daily Drawdown Check
        if current_daily_drawdown_percent > self.config.MAX_DAILY_DRAWDOWN_PERCENT:
            failed_checks.append(
                f"Current daily drawdown {current_daily_drawdown_percent:.2f}% exceeds maximum limit of "
                f"{self.config.MAX_DAILY_DRAWDOWN_PERCENT:.2f}%"
            )

        is_approved: bool = len(failed_checks) == 0
        reason: str = (
            "All safety checks passed."
            if is_approved
            else f"Safety lock rejected trade with {len(failed_checks)} violation(s)."
        )

        return SafetyCheckResult(
            is_approved=is_approved,
            reason=reason,
            proposal=proposal,
            failed_checks=failed_checks,
        )
