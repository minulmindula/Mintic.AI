from unittest.mock import MagicMock, patch
import pytest

from src.agents.graph import create_deliberation_graph
from src.agents.nodes import analyst_node, bear_node, bull_node, risk_manager_node
from src.agents.state import DeliberationState
from src.core.schemas import TradeProposal


@pytest.fixture
def sample_trade_proposal() -> TradeProposal:
    """Fixture returning a sample valid TradeProposal."""
    return TradeProposal(
        symbol="AAPL",
        action="BUY",
        quantity=10.0,
        confidence_score=0.85,
        target_price=180.0,
        stop_loss=170.0,
        reasoning_summary="Deliberated bullish setup with strong risk controls",
    )


@pytest.fixture
def sample_initial_state() -> DeliberationState:
    """Fixture returning initial DeliberationState with mock market data."""
    return {
        "symbol": "AAPL",
        "market_data": {
            "current_price": 178.50,
            "volume_24h": 55000000,
            "sma_50": 172.00,
            "sma_200": 165.00,
        },
        "account_state": {
            "buying_power": 25000.00,
            "cash": 25000.00,
            "portfolio_value": 30000.00,
        },
        "analyst_report": "",
        "bull_hypothesis": "",
        "bear_hypothesis": "",
        "final_proposal": None,
    }


def test_individual_agent_nodes(sample_trade_proposal: TradeProposal) -> None:
    """Test individual node execution with mocked LLM instances."""
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Mocked LLM analysis output"
    mock_llm.invoke.return_value = mock_response

    mock_structured_llm = MagicMock()
    mock_structured_llm.invoke.return_value = sample_trade_proposal
    mock_llm.with_structured_output.return_value = mock_structured_llm

    state: DeliberationState = {
        "symbol": "AAPL",
        "market_data": {"price": 178.50},
        "account_state": {"buying_power": 25000.00},
        "analyst_report": "Baseline report",
        "bull_hypothesis": "Bullish thesis",
        "bear_hypothesis": "Bearish thesis",
        "final_proposal": None,
    }

    analyst_res = analyst_node(state=state, llm=mock_llm)
    assert "analyst_report" in analyst_res

    bull_res = bull_node(state=state, llm=mock_llm)
    assert "bull_hypothesis" in bull_res

    bear_res = bear_node(state=state, llm=mock_llm)
    assert "bear_hypothesis" in bear_res

    risk_res = risk_manager_node(state=state, llm=mock_llm)
    assert isinstance(risk_res["final_proposal"], TradeProposal)
    assert risk_res["final_proposal"] == sample_trade_proposal


@patch("src.agents.nodes.get_default_llm")
def test_deliberation_graph_execution(
    mock_get_llm: MagicMock,
    sample_initial_state: DeliberationState,
    sample_trade_proposal: TradeProposal,
) -> None:
    """
    Test that executing the full deliberation graph with mock market data
    populates state and yields a valid TradeProposal instance.
    """
    mock_llm = MagicMock()
    mock_text_response = MagicMock()
    mock_text_response.content = "Generated analysis report"
    mock_llm.invoke.return_value = mock_text_response

    mock_structured_llm = MagicMock()
    mock_structured_llm.invoke.return_value = sample_trade_proposal
    mock_llm.with_structured_output.return_value = mock_structured_llm
    mock_get_llm.return_value = mock_llm

    graph = create_deliberation_graph()
    final_state = graph.invoke(sample_initial_state)

    assert "analyst_report" in final_state
    assert "bull_hypothesis" in final_state
    assert "bear_hypothesis" in final_state
    assert isinstance(final_state.get("final_proposal"), TradeProposal)

    proposal = final_state["final_proposal"]
    assert proposal.symbol == "AAPL"
    assert proposal.quantity == 10.0
    assert proposal.target_price == 180.0
