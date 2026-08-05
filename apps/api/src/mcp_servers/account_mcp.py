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


class PaperAccountLedger:
    """Dynamic in-memory paper trading account ledger."""

    def __init__(self) -> None:
        self.cash: float = 25000.0
        self.positions: dict[str, dict[str, Any]] = {}

    def get_summary(self) -> dict[str, Any]:
        from src.mcp_servers.market_mcp import fetch_ticker_price_impl

        total_market_val = 0.0
        pos_list: list[dict[str, Any]] = []

        for sym, pos in list(self.positions.items()):
            qty = pos["qty"]
            cost_basis = pos["cost_basis"]
            live_price = cost_basis
            try:
                q = fetch_ticker_price_impl(sym)
                if q.get("current_price", 0) > 0:
                    live_price = float(q["current_price"])
            except Exception:
                pass

            mkt_val = round(qty * live_price, 2)
            unrealized_pl = round(mkt_val - (qty * cost_basis), 2)
            total_market_val += mkt_val

            pos_list.append({
                "symbol": sym,
                "qty": round(qty, 4),
                "market_value": mkt_val,
                "current_price": round(live_price, 2 if live_price >= 1.0 else 4),
                "unrealized_pl": unrealized_pl,
            })

        portfolio_val = round(self.cash + total_market_val, 2)
        return {
            "buying_power": round(self.cash, 2),
            "cash": round(self.cash, 2),
            "portfolio_value": portfolio_val,
            "currency": "GBP",
            "positions": pos_list,
        }

    def record_trade(self, symbol: str, action: str, qty: float, price: float) -> None:
        cost = qty * price
        clean_sym = symbol.upper()
        if action.upper() == "BUY":
            if cost <= self.cash:
                self.cash -= cost
                if clean_sym in self.positions:
                    old_qty = self.positions[clean_sym]["qty"]
                    old_cost = old_qty * self.positions[clean_sym]["cost_basis"]
                    new_qty = old_qty + qty
                    self.positions[clean_sym] = {
                        "qty": new_qty,
                        "cost_basis": (old_cost + cost) / new_qty,
                    }
                else:
                    self.positions[clean_sym] = {"qty": qty, "cost_basis": price}
        elif action.upper() == "SELL":
            if clean_sym in self.positions:
                cur_qty = self.positions[clean_sym]["qty"]
                sell_qty = min(qty, cur_qty)
                self.cash += (sell_qty * price)
                remaining = cur_qty - sell_qty
                if remaining <= 0.0001:
                    del self.positions[clean_sym]
                else:
                    self.positions[clean_sym]["qty"] = remaining


paper_ledger = PaperAccountLedger()


def get_buying_power_impl(client: Optional[TradingClient] = None) -> dict[str, Any]:
    """
    Implementation function for retrieving current buying power from Alpaca paper trading account.
    """
    if client is not None:
        try:
            account = client.get_account()
            return {
                "buying_power": float(account.buying_power),
                "currency": getattr(account, "currency", "GBP"),
                "cash": float(getattr(account, "cash", 0.0)),
                "portfolio_value": float(getattr(account, "portfolio_value", 0.0)),
            }
        except Exception:
            pass

    try:
        tc = _get_trading_client()
        account = tc.get_account()
        return {
            "buying_power": float(account.buying_power),
            "currency": getattr(account, "currency", "GBP"),
            "cash": float(getattr(account, "cash", 0.0)),
            "portfolio_value": float(getattr(account, "portfolio_value", 0.0)),
        }
    except Exception:
        return paper_ledger.get_summary()


def get_current_positions_impl(
    client: Optional[TradingClient] = None,
) -> list[dict[str, Any]]:
    """
    Implementation function for retrieving current open positions from Alpaca paper trading account.
    """
    if client is not None:
        try:
            positions = client.get_all_positions()
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
        except Exception:
            pass

    try:
        tc = _get_trading_client()
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
    except Exception:
        return paper_ledger.get_summary()["positions"]


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
