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


def fetch_market_history_impl(
    symbol: str, days: int = 30
) -> list[dict[str, Any]]:
    """
    Generates/fetches historical OHLCV price series data for a stock symbol.

    Args:
        symbol: Stock ticker symbol.
        days: Number of days of historical candle data (default 30).

    Returns:
        List of candle dictionaries containing timestamp, open, high, low, close, volume.
    """
    import math
    from datetime import datetime, timedelta, timezone

    upper_symbol = symbol.upper()
    base_price = 180.0
    if upper_symbol == "GOOGL":
        base_price = 175.0
    elif upper_symbol == "MSFT":
        base_price = 420.0
    elif upper_symbol == "NVDA":
        base_price = 125.0
    elif upper_symbol == "AMZN":
        base_price = 185.0
    elif upper_symbol == "TSLA":
        base_price = 210.0
    elif upper_symbol == "META":
        base_price = 490.0
    elif upper_symbol == "SPY":
        base_price = 545.0

    today = datetime.now(timezone.utc)
    history: list[dict[str, Any]] = []

    for i in range(days, 0, -1):
        dt = today - timedelta(days=i)
        sine_wave = math.sin(i / 3.0) * (base_price * 0.04)
        trend = (days - i) * (base_price * 0.002)
        close_p = round(base_price + sine_wave + trend, 2)
        open_p = round(close_p - (math.cos(i) * 1.5), 2)
        high_p = round(max(open_p, close_p) + abs(math.sin(i) * 2.0) + 0.5, 2)
        low_p = round(min(open_p, close_p) - abs(math.cos(i) * 1.5) - 0.5, 2)
        volume = int(10000000 + (abs(sine_wave) * 500000))

        history.append({
            "timestamp": dt.strftime("%Y-%m-%d"),
            "open": open_p,
            "high": high_p,
            "low": low_p,
            "close": close_p,
            "volume": volume,
        })

    return history


if __name__ == "__main__":
    mcp.run()
