from typing import Any, Optional

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from mcp.server.fastmcp import FastMCP

from src.config import settings

mcp: FastMCP = FastMCP("MarketMCP")


def _get_data_client() -> StockHistoricalDataClient:
    """Helper function to instantiate Alpaca StockHistoricalDataClient."""
    return StockHistoricalDataClient(
        api_key=settings.ALPACA_API_KEY,
        secret_key=settings.ALPACA_SECRET_KEY,
    )


def fetch_ticker_price_impl(
    symbol: str, data_client: Optional[Any] = None
) -> dict[str, Any]:
    """
    Implementation function to fetch latest ticker price quote for a stock symbol.

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, GOOGL).
        data_client: Optional historical data client instance for testing / injection.
    """
    client = data_client or _get_data_client()
    upper_symbol = symbol.upper()
    request_params = StockLatestQuoteRequest(symbol_or_symbols=upper_symbol)
    quotes = client.get_stock_latest_quote(request_params)

    if upper_symbol in quotes:
        quote = quotes[upper_symbol]
        ask_price = float(getattr(quote, "ask_price", 0.0) or 0.0)
        bid_price = float(getattr(quote, "bid_price", 0.0) or 0.0)
        current_price = ask_price if ask_price > 0 else bid_price
    else:
        current_price = 0.0
        ask_price = 0.0
        bid_price = 0.0

    return {
        "symbol": upper_symbol,
        "current_price": current_price,
        "ask_price": ask_price,
        "bid_price": bid_price,
    }


@mcp.tool()
def fetch_ticker_price(symbol: str) -> dict[str, Any]:
    """FastMCP tool to fetch the latest market price quote for a ticker symbol."""
    return fetch_ticker_price_impl(symbol=symbol)


if __name__ == "__main__":
    mcp.run()
