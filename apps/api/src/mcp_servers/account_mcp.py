from typing import Any, Optional

from alpaca.trading.client import TradingClient
from mcp.server.fastmcp import FastMCP

from src.config import settings

mcp: FastMCP = FastMCP("AccountMCP")


def _get_trading_client() -> TradingClient:
    """Helper function to create Alpaca paper TradingClient."""
    return TradingClient(
        api_key=settings.ALPACA_API_KEY,
        secret_key=settings.ALPACA_SECRET_KEY,
        paper=settings.ALPACA_PAPER,
    )


def get_buying_power_impl(client: Optional[TradingClient] = None) -> dict[str, Any]:
    """
    Implementation function for retrieving current buying power from Alpaca paper trading account.

    Args:
        client: Optional TradingClient instance for testing / dependency injection.
    """
    tc = client or _get_trading_client()
    account = tc.get_account()
    return {
        "buying_power": float(account.buying_power),
        "currency": getattr(account, "currency", "GBP"),
        "cash": float(getattr(account, "cash", 0.0)),
        "portfolio_value": float(getattr(account, "portfolio_value", 0.0)),
    }


def get_current_positions_impl(
    client: Optional[TradingClient] = None,
) -> list[dict[str, Any]]:
    """
    Implementation function for retrieving current open positions from Alpaca paper trading account.

    Args:
        client: Optional TradingClient instance for testing / dependency injection.
    """
    tc = client or _get_trading_client()
    positions = tc.get_all_positions()
    return [
        {
            "symbol": pos.symbol,
            "qty": float(pos.qty),
            "market_value": float(getattr(pos, "market_value", 0.0)),
            "current_price": float(getattr(pos, "current_price", 0.0)),
            "unrealized_pl": float(getattr(pos, "unrealized_pl", 0.0)),
        }
        for pos in positions
    ]


@mcp.tool()
def get_buying_power() -> dict[str, Any]:
    """FastMCP tool to retrieve current account buying power."""
    return get_buying_power_impl()


@mcp.tool()
def get_current_positions() -> list[dict[str, Any]]:
    """FastMCP tool to retrieve current open portfolio positions."""
    return get_current_positions_impl()


if __name__ == "__main__":
    mcp.run()
