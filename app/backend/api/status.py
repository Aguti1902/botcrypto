"""Status API endpoints."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict

router = APIRouter()


class StatusResponse(BaseModel):
    """Status response model."""
    status: str
    mode: str
    can_trade: bool
    circuit_breaker_triggered: bool
    uptime_seconds: float
    symbols: list[str]


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get system status."""
    # TODO: Integrate with actual trading engine
    return StatusResponse(
        status="running",
        mode="paper",
        can_trade=True,
        circuit_breaker_triggered=False,
        uptime_seconds=0.0,
        symbols=["BTC/USDT", "ETH/USDT"],
    )


@router.get("/metrics")
async def get_metrics():
    """Get performance metrics."""
    # TODO: Get from metrics calculator
    return {
        "sharpe_ratio": 0.0,
        "max_drawdown": 0.0,
        "total_return": 0.0,
        "win_rate": 0.0,
        "num_trades": 0,
    }


@router.post("/kill")
async def kill_switch():
    """Emergency kill switch - stop all trading."""
    # TODO: Trigger circuit breaker
    return {"status": "trading_stopped", "message": "Kill switch activated"}

