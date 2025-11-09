"""Orders API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.crud import get_orders, get_order

router = APIRouter()


class OrderResponse(BaseModel):
    """Order response model."""
    order_id: str
    symbol: str
    side: str
    order_type: str
    status: str
    quantity: float
    filled_quantity: float
    price: Optional[float]
    average_fill_price: Optional[float]
    strategy: Optional[str]


@router.get("/orders", response_model=List[OrderResponse])
async def list_orders(
    symbol: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List orders."""
    orders = await get_orders(db, symbol=symbol, limit=limit)
    
    return [
        OrderResponse(
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side.value,
            order_type=order.order_type.value,
            status=order.status.value,
            quantity=order.quantity,
            filled_quantity=order.filled_quantity,
            price=order.price,
            average_fill_price=order.average_fill_price,
            strategy=order.strategy,
        )
        for order in orders
    ]


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order_detail(
    order_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get order details."""
    order = await get_order(db, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return OrderResponse(
        order_id=order.order_id,
        symbol=order.symbol,
        side=order.side.value,
        order_type=order.order_type.value,
        status=order.status.value,
        quantity=order.quantity,
        filled_quantity=order.filled_quantity,
        price=order.price,
        average_fill_price=order.average_fill_price,
        strategy=order.strategy,
    )


@router.get("/positions")
async def list_positions(db: AsyncSession = Depends(get_db)):
    """List open positions."""
    # TODO: Implement
    return []

