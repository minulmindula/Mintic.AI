from typing import Any, Optional

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest

from src.config import Settings, settings as default_settings
from src.core.schemas import SafetyCheckResult


class SandboxedBrokerService:
    """
    Sandboxed Broker Service executing paper trades via Alpaca.

    CRITICAL SAFETY REQUIREMENT: Must accept a SafetyCheckResult object and ONLY
    execute trades against Alpaca's paper trading client if is_approved is True.
    If is_approved is False, a PermissionError is raised.
    """

    def __init__(
        self,
        trading_client: Optional[TradingClient] = None,
        config: Optional[Settings] = None,
    ) -> None:
        """Initialize the SandboxedBrokerService with Alpaca paper trading client."""
        self.config: Settings = config or default_settings
        if trading_client is not None:
            self.trading_client: TradingClient = trading_client
        else:
            self.trading_client = TradingClient(
                api_key=self.config.ALPACA_API_KEY,
                secret_key=self.config.ALPACA_SECRET_KEY,
                paper=self.config.ALPACA_PAPER,
            )

    def execute_trade(self, safety_result: SafetyCheckResult) -> Any:
        """
        Executes a trade against Alpaca paper trading API if approved by UnbendableSafetyLock.

        Args:
            safety_result: SafetyCheckResult object containing evaluation status and trade details.

        Returns:
            The submitted order response from Alpaca TradingClient.

        Raises:
            PermissionError: If safety_result.is_approved is False.
        """
        if not safety_result.is_approved:
            raise PermissionError(
                f"Trade execution blocked by UnbendableSafetyLock: {safety_result.reason} "
                f"Violations: {safety_result.failed_checks}"
            )

        proposal = safety_result.proposal
        side: OrderSide = (
            OrderSide.BUY if proposal.action.upper() == "BUY" else OrderSide.SELL
        )

        order_data = MarketOrderRequest(
            symbol=proposal.symbol,
            qty=proposal.quantity,
            side=side,
            time_in_force=TimeInForce.GTC,
        )

        return self.trading_client.submit_order(order_data=order_data)
