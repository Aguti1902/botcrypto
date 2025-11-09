"""Portfolio API endpoints."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db

router = APIRouter()


class PortfolioSnapshot(BaseModel):
    """Portfolio snapshot model."""
    total_equity: float
    cash: float
    positions_value: float
    unrealized_pnl: float
    realized_pnl: float
    daily_return: float


@router.get("/portfolio", response_model=PortfolioSnapshot)
async def get_portfolio(db: AsyncSession = Depends(get_db)):
    """Get portfolio snapshot."""
    # TODO: Calculate from database
    return PortfolioSnapshot(
        total_equity=20000.0,
        cash=20000.0,
        positions_value=0.0,
        unrealized_pnl=0.0,
        realized_pnl=0.0,
        daily_return=0.0,
    )


@router.get("/portfolio/equity_curve")
async def get_equity_curve(db: AsyncSession = Depends(get_db)):
    """Get equity curve."""
    # TODO: Get from database
    return {"timestamps": [], "values": []}


@router.get("/portfolio/allocation")
async def get_allocation():
    """Get current portfolio allocation."""
    # TODO: Calculate current allocation
    return {"allocations": {}}

