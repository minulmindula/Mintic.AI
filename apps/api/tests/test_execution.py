from unittest.mock import MagicMock
import pytest

from src.core.schemas import SafetyCheckResult, TradeProposal
from src.execution.sandbox_broker import SandboxedBrokerService
from src.mcp_servers.account_mcp import (
    get_buying_power,
    get_buying_power_impl,
    get_current_positions,
    get_current_positions_impl,
)
from src.mcp_servers.market_mcp import fetch_ticker_price, fetch_ticker_price_impl


@pytest.fixture
def mock_trading_client() -> MagicMock:
    """Fixture providing a mocked Alpaca TradingClient."""
    return MagicMock()


@pytest.fixture
def approved_safety_result() -> SafetyCheckResult:
    """Fixture returning an approved SafetyCheckResult."""
    proposal = TradeProposal(
        symbol="AAPL",
        action="BUY",
        quantity=10.0,
        confidence_score=0.85,
        target_price=180.0,
        stop_loss=170.0,
        reasoning_summary="Approved trade setup",
    )
    return SafetyCheckResult(
        is_approved=True,
        reason="All safety checks passed.",
        proposal=proposal,
        failed_checks=[],
    )


@pytest.fixture
def rejected_safety_result() -> SafetyCheckResult:
    """Fixture returning a rejected SafetyCheckResult."""
    proposal = TradeProposal(
        symbol="UNAPPROVED",
        action="BUY",
        quantity=10.0,
        confidence_score=0.50,
        target_price=180.0,
        stop_loss=170.0,
        reasoning_summary="Unapproved trade setup",
    )
    return SafetyCheckResult(
        is_approved=False,
        reason="Safety lock rejected trade.",
        proposal=proposal,
        failed_checks=["Symbol not allowed", "Confidence too low"],
    )


def test_sandbox_broker_raises_permission_error_on_unapproved_trade(
    mock_trading_client: MagicMock,
    rejected_safety_result: SafetyCheckResult,
) -> None:
    """Verify SandboxedBrokerService raises PermissionError if is_approved is False."""
    broker_service = SandboxedBrokerService(trading_client=mock_trading_client)

    with pytest.raises(PermissionError) as exc_info:
        broker_service.execute_trade(safety_result=rejected_safety_result)

    assert "Trade execution blocked by UnbendableSafetyLock" in str(exc_info.value)
    mock_trading_client.submit_order.assert_not_called()


def test_sandbox_broker_executes_trade_on_approved_result(
    mock_trading_client: MagicMock,
    approved_safety_result: SafetyCheckResult,
) -> None:
    """Verify SandboxedBrokerService submits market order to Alpaca when is_approved is True."""
    mock_order_response = MagicMock()
    mock_order_response.id = "mock_order_123"
    mock_trading_client.submit_order.return_value = mock_order_response

    broker_service = SandboxedBrokerService(trading_client=mock_trading_client)
    result = broker_service.execute_trade(safety_result=approved_safety_result)

    assert result == mock_order_response
    mock_trading_client.submit_order.assert_called_once()


def test_account_mcp_get_buying_power(mock_trading_client: MagicMock) -> None:
    """Test get_buying_power FastMCP tool implementation function."""
    mock_account = MagicMock()
    mock_account.buying_power = "25000.50"
    mock_account.currency = "GBP"
    mock_account.cash = "25000.50"
    mock_account.portfolio_value = "30000.00"
    mock_trading_client.get_account.return_value = mock_account

    result = get_buying_power_impl(client=mock_trading_client)

    assert result["buying_power"] == 25000.50
    assert result["currency"] == "GBP"


def test_account_mcp_get_current_positions(mock_trading_client: MagicMock) -> None:
    """Test get_current_positions FastMCP tool implementation function."""
    mock_pos = MagicMock()
    mock_pos.symbol = "AAPL"
    mock_pos.qty = "10"
    mock_pos.market_value = "1800.00"
    mock_pos.current_price = "180.00"
    mock_pos.unrealized_pl = "100.00"
    mock_trading_client.get_all_positions.return_value = [mock_pos]

    positions = get_current_positions_impl(client=mock_trading_client)

    assert len(positions) == 1
    assert positions[0]["symbol"] == "AAPL"
    assert positions[0]["qty"] == 10.0
    assert positions[0]["market_value"] == 1800.00


def test_market_mcp_fetch_ticker_price() -> None:
    """Test fetch_ticker_price FastMCP tool implementation function."""
    mock_data_client = MagicMock()
    mock_quote = MagicMock()
    mock_quote.ask_price = 182.50
    mock_quote.bid_price = 182.40
    mock_data_client.get_stock_latest_quote.return_value = {"AAPL": mock_quote}

    result = fetch_ticker_price_impl(symbol="aapl", data_client=mock_data_client)

    assert result["symbol"] == "AAPL"
    assert result["current_price"] == 182.50
    assert result["ask_price"] == 182.50
    assert result["bid_price"] == 182.40


def test_fastmcp_tool_functions_callable() -> None:
    """Verify FastMCP tool endpoints are properly registered and callable."""
    assert callable(get_buying_power)
    assert callable(get_current_positions)
    assert callable(fetch_ticker_price)
