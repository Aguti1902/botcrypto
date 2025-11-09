"""Configuration API endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict

router = APIRouter()


class ConfigResponse(BaseModel):
    """Configuration response model."""
    mode: str
    symbols: list[str]
    risk_config: Dict
    strategies_config: Dict


@router.get("/config", response_model=ConfigResponse)
async def get_config():
    """Get current configuration."""
    # TODO: Load from config
    return ConfigResponse(
        mode="paper",
        symbols=["BTC/USDT", "ETH/USDT"],
        risk_config={
            "risk_per_trade": 0.003,
            "max_daily_drawdown": 0.04,
        },
        strategies_config={},
    )


@router.post("/config/update")
async def update_config(config: Dict):
    """Update configuration."""
    # TODO: Validate and update config
    return {"status": "updated"}

