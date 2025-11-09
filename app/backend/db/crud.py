"""CRUD operations for database models."""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload

from .models import (
    Order,
    Trade,
    Position,
    EquityCurve,
    Metric,
    Experiment,
    MLFeature,
    CircuitBreaker,
    OrderStatus,
)


# Orders
async def create_order(db: AsyncSession, order_data: dict) -> Order:
    """Create a new order."""
    order = Order(**order_data)
    db.add(order)
    await db.flush()
    await db.refresh(order)
    return order


async def get_order(db: AsyncSession, order_id: str) -> Optional[Order]:
    """Get order by ID."""
    result = await db.execute(
        select(Order).where(Order.order_id == order_id)
    )
    return result.scalar_one_or_none()


async def get_orders(
    db: AsyncSession,
    symbol: Optional[str] = None,
    status: Optional[OrderStatus] = None,
    strategy: Optional[str] = None,
    limit: int = 100,
) -> List[Order]:
    """Get orders with filters."""
    query = select(Order).order_by(desc(Order.created_at)).limit(limit)
    
    if symbol:
        query = query.where(Order.symbol == symbol)
    if status:
        query = query.where(Order.status == status)
    if strategy:
        query = query.where(Order.strategy == strategy)
    
    result = await db.execute(query)
    return result.scalars().all()


async def update_order_status(
    db: AsyncSession,
    order_id: str,
    status: OrderStatus,
    filled_quantity: Optional[float] = None,
    average_fill_price: Optional[float] = None,
) -> Optional[Order]:
    """Update order status."""
    order = await get_order(db, order_id)
    if not order:
        return None
    
    order.status = status
    order.updated_at = datetime.utcnow()
    
    if filled_quantity is not None:
        order.filled_quantity = filled_quantity
    if average_fill_price is not None:
        order.average_fill_price = average_fill_price
    
    if status == OrderStatus.FILLED:
        order.filled_at = datetime.utcnow()
    elif status == OrderStatus.CANCELLED:
        order.cancelled_at = datetime.utcnow()
    
    await db.flush()
    await db.refresh(order)
    return order


# Trades
async def create_trade(db: AsyncSession, trade_data: dict) -> Trade:
    """Create a new trade."""
    trade = Trade(**trade_data)
    db.add(trade)
    await db.flush()
    await db.refresh(trade)
    return trade


async def get_trades(
    db: AsyncSession,
    symbol: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
) -> List[Trade]:
    """Get trades with filters."""
    query = select(Trade).order_by(desc(Trade.executed_at)).limit(limit)
    
    if symbol:
        query = query.where(Trade.symbol == symbol)
    if start_date:
        query = query.where(Trade.executed_at >= start_date)
    if end_date:
        query = query.where(Trade.executed_at <= end_date)
    
    result = await db.execute(query)
    return result.scalars().all()


# Positions
async def create_position(db: AsyncSession, position_data: dict) -> Position:
    """Create a new position."""
    position = Position(**position_data)
    db.add(position)
    await db.flush()
    await db.refresh(position)
    return position


async def get_open_positions(db: AsyncSession, symbol: Optional[str] = None) -> List[Position]:
    """Get all open positions."""
    query = select(Position).where(Position.is_open == True)
    
    if symbol:
        query = query.where(Position.symbol == symbol)
    
    result = await db.execute(query)
    return result.scalars().all()


async def close_position(db: AsyncSession, position_id: int, close_price: float) -> Optional[Position]:
    """Close a position."""
    result = await db.execute(
        select(Position).where(Position.id == position_id)
    )
    position = result.scalar_one_or_none()
    
    if not position:
        return None
    
    position.is_open = False
    position.current_price = close_price
    position.closed_at = datetime.utcnow()
    position.updated_at = datetime.utcnow()
    
    # Calculate final realized PnL
    if position.side.value == "buy":
        pnl = (close_price - position.entry_price) * position.quantity
    else:
        pnl = (position.entry_price - close_price) * position.quantity
    
    position.realized_pnl = pnl
    
    await db.flush()
    await db.refresh(position)
    return position


# Equity Curve
async def add_equity_point(db: AsyncSession, equity_data: dict) -> EquityCurve:
    """Add equity curve point."""
    equity = EquityCurve(**equity_data)
    db.add(equity)
    await db.flush()
    await db.refresh(equity)
    return equity


async def get_equity_curve(
    db: AsyncSession,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[EquityCurve]:
    """Get equity curve."""
    query = select(EquityCurve).order_by(EquityCurve.timestamp)
    
    if start_date:
        query = query.where(EquityCurve.timestamp >= start_date)
    if end_date:
        query = query.where(EquityCurve.timestamp <= end_date)
    
    result = await db.execute(query)
    return result.scalars().all()


# Metrics
async def save_metric(db: AsyncSession, metric_data: dict) -> Metric:
    """Save a metric."""
    metric = Metric(**metric_data)
    db.add(metric)
    await db.flush()
    await db.refresh(metric)
    return metric


async def get_metrics(
    db: AsyncSession,
    metric_type: Optional[str] = None,
    metric_name: Optional[str] = None,
    scope: Optional[str] = None,
) -> List[Metric]:
    """Get metrics with filters."""
    query = select(Metric).order_by(desc(Metric.calculated_at))
    
    if metric_type:
        query = query.where(Metric.metric_type == metric_type)
    if metric_name:
        query = query.where(Metric.metric_name == metric_name)
    if scope:
        query = query.where(Metric.scope == scope)
    
    result = await db.execute(query)
    return result.scalars().all()


# Experiments
async def create_experiment(db: AsyncSession, experiment_data: dict) -> Experiment:
    """Create ML/RL experiment."""
    experiment = Experiment(**experiment_data)
    db.add(experiment)
    await db.flush()
    await db.refresh(experiment)
    return experiment


async def get_experiment(db: AsyncSession, experiment_id: str) -> Optional[Experiment]:
    """Get experiment by ID."""
    result = await db.execute(
        select(Experiment).where(Experiment.experiment_id == experiment_id)
    )
    return result.scalar_one_or_none()


async def update_experiment(
    db: AsyncSession,
    experiment_id: str,
    update_data: dict,
) -> Optional[Experiment]:
    """Update experiment."""
    experiment = await get_experiment(db, experiment_id)
    if not experiment:
        return None
    
    for key, value in update_data.items():
        setattr(experiment, key, value)
    
    await db.flush()
    await db.refresh(experiment)
    return experiment


# Circuit Breakers
async def trigger_circuit_breaker(db: AsyncSession, breaker_data: dict) -> CircuitBreaker:
    """Trigger circuit breaker."""
    breaker = CircuitBreaker(**breaker_data)
    db.add(breaker)
    await db.flush()
    await db.refresh(breaker)
    return breaker


async def resolve_circuit_breaker(db: AsyncSession, breaker_id: int) -> Optional[CircuitBreaker]:
    """Resolve circuit breaker."""
    result = await db.execute(
        select(CircuitBreaker).where(CircuitBreaker.id == breaker_id)
    )
    breaker = result.scalar_one_or_none()
    
    if not breaker:
        return None
    
    breaker.status = "resolved"
    breaker.resolved_at = datetime.utcnow()
    
    await db.flush()
    await db.refresh(breaker)
    return breaker


async def get_active_circuit_breakers(db: AsyncSession) -> List[CircuitBreaker]:
    """Get active circuit breakers."""
    result = await db.execute(
        select(CircuitBreaker)
        .where(CircuitBreaker.status == "triggered")
        .order_by(desc(CircuitBreaker.triggered_at))
    )
    return result.scalars().all()

