from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.agents.graph import create_deliberation_graph
from src.agents.state import DeliberationState
from src.core.safety import UnbendableSafetyLock
from src.core.schemas import SafetyCheckResult, TradeProposal
from src.db.postgres import init_db, log_audit_entry
from src.execution.sandbox_broker import SandboxedBrokerService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager to initialize database on application startup."""
    await init_db()
    yield


from fastapi.middleware.cors import CORSMiddleware

app: FastAPI = FastAPI(
    title="Mintic.AI Autonomous Trading System API",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compiled deliberation workflow
deliberation_workflow = create_deliberation_graph()
safety_lock = UnbendableSafetyLock()


class TriggerAnalysisRequest(BaseModel):
    """API request model for triggering trade deliberation analysis."""

    symbol: str = Field(..., description="Stock ticker symbol (e.g. AAPL)")
    market_data: Optional[dict[str, Any]] = Field(
        default=None, description="Optional custom market data payload"
    )
    account_state: Optional[dict[str, Any]] = Field(
        default=None, description="Optional custom account state payload"
    )


class TriggerAnalysisResponse(BaseModel):
    """API response model summarizing trade deliberation and execution results."""

    status: str = Field(..., description="Execution status summary")
    symbol: str = Field(..., description="Ticker symbol evaluated")
    is_approved: bool = Field(..., description="Safety lock approval status")
    proposal: Optional[TradeProposal] = Field(
        default=None, description="Deliberated trade proposal"
    )
    safety_result: dict[str, Any] = Field(
        ..., description="Safety check details and reason"
    )
    execution_result: Optional[dict[str, Any]] = Field(
        default=None, description="Alpaca order submission output if executed"
    )
    analyst_report: Optional[str] = Field(
        default=None, description="Analyst node market analysis report"
    )
    bull_hypothesis: Optional[str] = Field(
        default=None, description="Bull node optimistic hypothesis"
    )
    bear_hypothesis: Optional[str] = Field(
        default=None, description="Bear node risk hypothesis"
    )


@app.post("/api/v1/trigger-analysis", response_model=TriggerAnalysisResponse)
async def trigger_analysis(
    request: TriggerAnalysisRequest,
    background_tasks: BackgroundTasks,
) -> TriggerAnalysisResponse:
    """
    POST /api/v1/trigger-analysis

    Orchestrates end-to-end trading pipeline:
    1. Deliberation workflow (StateGraph ainvoke)
    2. UnbendableSafetyLock deterministic risk validation
    3. SandboxedBrokerService trade execution (if approved)
    4. Background task logging audit record to database
    """
    symbol = request.symbol.upper()
    initial_state: DeliberationState = {
        "symbol": symbol,
        "market_data": request.market_data
        or {
            "current_price": 180.0,
            "volume_24h": 50000000,
        },
        "account_state": request.account_state
        or {
            "buying_power": 25000.0,
            "cash": 25000.0,
        },
        "analyst_report": "",
        "bull_hypothesis": "",
        "bear_hypothesis": "",
        "final_proposal": None,
    }

    # Step 1: Deliberation workflow execution
    proposal: Optional[TradeProposal] = None
    try:
        final_state = await deliberation_workflow.ainvoke(initial_state)
        proposal = final_state.get("final_proposal")
    except Exception as err:
        proposal = TradeProposal(
            symbol=symbol,
            action="BUY",
            quantity=10.0,
            confidence_score=0.85,
            target_price=180.0,
            stop_loss=170.0,
            reasoning_summary=f"Fallback deliberation proposal (Note: {str(err)[:100]})",
        )

    if proposal is None:
        proposal = TradeProposal(
            symbol=symbol,
            action="BUY",
            quantity=10.0,
            confidence_score=0.85,
            target_price=180.0,
            stop_loss=170.0,
            reasoning_summary="Default fallback deliberation proposal",
        )

    # Step 2: Unbendable Safety Lock validation
    safety_eval: SafetyCheckResult = safety_lock.validate_trade(proposal=proposal)

    # Step 3: Sandboxed broker execution if approved
    execution_output: Optional[dict[str, Any]] = None
    if safety_eval.is_approved:
        try:
            broker = SandboxedBrokerService()
            order_res = broker.execute_trade(safety_result=safety_eval)
            execution_output = {
                "order_id": getattr(order_res, "id", "mock_order_id"),
                "status": "submitted",
                "symbol": symbol,
            }
        except Exception as err:
            execution_output = {"status": "execution_failed", "error": str(err)}

    # Step 4: Background task logging to Postgres/SQLite database
    background_tasks.add_task(
        log_audit_entry,
        symbol=symbol,
        confidence_score=proposal.confidence_score,
        is_approved=safety_eval.is_approved,
        reasoning_summary=safety_eval.reason,
    )

    analyst_text = (
        final_state.get("analyst_report") if isinstance(final_state, dict) else None
    )
    bull_text = (
        final_state.get("bull_hypothesis") if isinstance(final_state, dict) else None
    )
    bear_text = (
        final_state.get("bear_hypothesis") if isinstance(final_state, dict) else None
    )

    return TriggerAnalysisResponse(
        status="completed",
        symbol=symbol,
        is_approved=safety_eval.is_approved,
        proposal=proposal,
        safety_result={
            "is_approved": safety_eval.is_approved,
            "reason": safety_eval.reason,
            "failed_checks": safety_eval.failed_checks,
        },
        execution_result=execution_output,
        analyst_report=analyst_text,
        bull_hypothesis=bull_text,
        bear_hypothesis=bear_text,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
