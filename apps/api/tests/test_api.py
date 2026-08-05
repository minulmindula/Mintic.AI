from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.core.schemas import TradeProposal
from src.db.postgres import init_db, log_audit_entry
from src.vector.qdrant_store import DocumentVectorStore


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Fixture providing FastAPI TestClient within lifespan context manager."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_proposal() -> TradeProposal:
    """Fixture returning a valid TradeProposal."""
    return TradeProposal(
        symbol="AAPL",
        action="BUY",
        quantity=10.0,
        confidence_score=0.85,
        target_price=180.0,
        stop_loss=170.0,
        reasoning_summary="Valid trade setup",
    )


@patch("src.api.main.deliberation_workflow.ainvoke")
@patch("src.execution.sandbox_broker.TradingClient")
def test_trigger_analysis_endpoint_returns_200(
    mock_alpaca_client: MagicMock,
    mock_ainvoke: AsyncMock,
    client: TestClient,
    sample_proposal: TradeProposal,
) -> None:
    """Verify POST /api/v1/trigger-analysis returns HTTP 200 and expected payload structure."""
    mock_ainvoke.return_value = {
        "symbol": "AAPL",
        "analyst_report": "Mock analyst report",
        "bull_hypothesis": "Mock bull hypothesis",
        "bear_hypothesis": "Mock bear hypothesis",
        "final_proposal": sample_proposal,
    }

    mock_order = MagicMock()
    mock_order.id = "order_123"
    mock_alpaca_client.return_value.submit_order.return_value = mock_order

    response = client.post(
        "/api/v1/trigger-analysis",
        json={
            "symbol": "AAPL",
            "market_data": {"current_price": 180.0},
            "account_state": {"buying_power": 25000.0},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["symbol"] == "AAPL"
    assert data["is_approved"] is True
    assert data["safety_result"]["is_approved"] is True
    assert "execution_result" in data


@pytest.mark.asyncio
async def test_database_audit_logging() -> None:
    """Verify async database audit log entry creation."""
    await init_db()
    entry = await log_audit_entry(
        symbol="AAPL",
        confidence_score=0.85,
        is_approved=True,
        reasoning_summary="Test audit log entry",
    )
    assert entry.id is not None
    assert entry.symbol == "AAPL"
    assert entry.is_approved is True
    assert entry.confidence_score == 0.85


def test_qdrant_document_vector_store() -> None:
    """Verify DocumentVectorStore initialization and financial_docs collection."""
    store = DocumentVectorStore(vector_size=1536)
    assert store.COLLECTION_NAME == "financial_docs"


def test_get_health_endpoint(client: TestClient) -> None:
    """Verify GET /api/v1/health returns 200 and healthy status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


def test_get_safety_rules_endpoint(client: TestClient) -> None:
    """Verify GET /api/v1/config/safety-rules returns active safety bounds."""
    response = client.get("/api/v1/config/safety-rules")
    assert response.status_code == 200
    data = response.json()
    assert "AAPL" in data["allowed_symbols"]
    assert data["max_position_size_gbp"] > 0
    assert data["min_confidence_threshold"] == 0.70


def test_get_audit_logs_endpoint(client: TestClient) -> None:
    """Verify GET /api/v1/audit-logs returns 200 and a list of audit records."""
    response = client.get("/api/v1/audit-logs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_account_summary_endpoint(client: TestClient) -> None:
    """Verify GET /api/v1/account returns 200 and account details."""
    response = client.get("/api/v1/account")
    assert response.status_code == 200
    data = response.json()
    assert "buying_power" in data
    assert data["currency"] == "GBP"


def test_get_market_quote_endpoint(client: TestClient) -> None:
    """Verify GET /api/v1/market/quote/{symbol} returns 200 and price data."""
    response = client.get("/api/v1/market/quote/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert "current_price" in data
