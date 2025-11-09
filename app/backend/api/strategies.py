"""Strategies API endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict

router = APIRouter()


class StrategyInfo(BaseModel):
    """Strategy information model."""
    name: str
    enabled: bool
    type: str
    parameters: Dict


@router.get("/strategies", response_model=List[StrategyInfo])
async def list_strategies():
    """List all strategies and their status."""
    # TODO: Get from trading config
    return [
        StrategyInfo(
            name="trend_atr",
            enabled=True,
            type="trend",
            parameters={"sma_fast": 50, "sma_slow": 200},
        ),
        StrategyInfo(
            name="meanrev_rsi",
            enabled=True,
            type="mean_reversion",
            parameters={"rsi_th": 30},
        ),
    ]


@router.post("/strategies/{strategy_name}/enable")
async def enable_strategy(strategy_name: str):
    """Enable a strategy."""
    # TODO: Update config and trading engine
    return {"status": "enabled", "strategy": strategy_name}


@router.post("/strategies/{strategy_name}/disable")
async def disable_strategy(strategy_name: str):
    """Disable a strategy."""
    # TODO: Update config and trading engine
    return {"status": "disabled", "strategy": strategy_name}

