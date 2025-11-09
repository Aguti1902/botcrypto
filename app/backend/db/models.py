"""SQLAlchemy models for database tables."""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
    JSON,
    Enum,
    Index,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class OrderStatus(enum.Enum):
    """Order status enumeration."""
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class OrderType(enum.Enum):
    """Order type enumeration."""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    STOP_LOSS_LIMIT = "stop_loss_limit"
    TAKE_PROFIT = "take_profit"
    TAKE_PROFIT_LIMIT = "take_profit_limit"
    TRAILING_STOP = "trailing_stop"


class OrderSide(enum.Enum):
    """Order side enumeration."""
    BUY = "buy"
    SELL = "sell"


class Order(Base):
    """Order model - tracks all orders (paper and live)."""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True, nullable=False)
    correlation_id = Column(String, index=True)  # For tracing
    
    # Order details
    exchange = Column(String, nullable=False)
    symbol = Column(String, nullable=False, index=True)
    side = Column(Enum(OrderSide), nullable=False)
    order_type = Column(Enum(OrderType), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, index=True)
    
    # Quantities and prices
    quantity = Column(Float, nullable=False)
    filled_quantity = Column(Float, default=0.0)
    price = Column(Float)  # Limit price
    average_fill_price = Column(Float)
    stop_price = Column(Float)  # For stop orders
    
    # Strategy and risk
    strategy = Column(String, index=True)
    position_id = Column(Integer, ForeignKey("positions.id"))
    
    # Metadata
    client_order_id = Column(String)
    exchange_order_id = Column(String, index=True)
    error_message = Column(Text)
    metadata = Column(JSON)  # Extra data
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    filled_at = Column(DateTime)
    cancelled_at = Column(DateTime)
    
    # Relationships
    trades = relationship("Trade", back_populates="order")
    
    __table_args__ = (
        Index("idx_orders_symbol_status", "symbol", "status"),
        Index("idx_orders_strategy_created", "strategy", "created_at"),
    )


class Trade(Base):
    """Trade model - individual fills of orders."""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String, unique=True, index=True, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    # Trade details
    exchange = Column(String, nullable=False)
    symbol = Column(String, nullable=False, index=True)
    side = Column(Enum(OrderSide), nullable=False)
    
    # Execution
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    fee = Column(Float, default=0.0)
    fee_currency = Column(String)
    
    # PnL (calculated later)
    realized_pnl = Column(Float)
    
    # Metadata
    exchange_trade_id = Column(String)
    metadata = Column(JSON)
    
    # Timestamps
    executed_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    order = relationship("Order", back_populates="trades")
    
    __table_args__ = (
        Index("idx_trades_symbol_executed", "symbol", "executed_at"),
    )


class Position(Base):
    """Position model - current and historical positions."""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Position details
    exchange = Column(String, nullable=False)
    symbol = Column(String, nullable=False, index=True)
    side = Column(Enum(OrderSide), nullable=False)
    
    # Quantities
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float)
    
    # Risk management
    stop_loss = Column(Float)
    take_profit = Column(Float)
    trailing_stop_distance = Column(Float)
    
    # PnL
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    
    # Strategy
    strategy = Column(String, index=True)
    
    # Status
    is_open = Column(Boolean, default=True, index=True)
    
    # Timestamps
    opened_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    closed_at = Column(DateTime)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metadata
    metadata = Column(JSON)
    
    __table_args__ = (
        Index("idx_positions_symbol_open", "symbol", "is_open"),
        Index("idx_positions_strategy_opened", "strategy", "opened_at"),
    )


class EquityCurve(Base):
    """Equity curve - portfolio value over time."""
    __tablename__ = "equity_curve"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Values
    timestamp = Column(DateTime, nullable=False, index=True)
    total_equity = Column(Float, nullable=False)
    cash = Column(Float, nullable=False)
    positions_value = Column(Float, nullable=False)
    
    # Performance metrics
    daily_return = Column(Float)
    cumulative_return = Column(Float)
    drawdown = Column(Float)
    
    # Breakdown by strategy
    strategy_breakdown = Column(JSON)
    
    # Metadata
    metadata = Column(JSON)


class Metric(Base):
    """Metrics - performance and risk metrics."""
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Scope
    metric_type = Column(String, nullable=False, index=True)  # strategy, portfolio, system
    metric_name = Column(String, nullable=False, index=True)
    scope = Column(String)  # Strategy name, symbol, or "global"
    
    # Value
    value = Column(Float, nullable=False)
    
    # Time range
    period_start = Column(DateTime, index=True)
    period_end = Column(DateTime, index=True)
    
    # Timestamps
    calculated_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Metadata
    metadata = Column(JSON)
    
    __table_args__ = (
        Index("idx_metrics_type_name", "metric_type", "metric_name"),
        Index("idx_metrics_calculated", "calculated_at"),
    )


class Experiment(Base):
    """Experiment - ML/RL training experiments."""
    __tablename__ = "experiments"
    
    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(String, unique=True, index=True, nullable=False)
    
    # Experiment details
    experiment_type = Column(String, nullable=False)  # ml_ensemble, rl_ppo, etc.
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # Configuration
    config = Column(JSON, nullable=False)
    
    # Results
    metrics = Column(JSON)  # Training metrics
    validation_metrics = Column(JSON)
    test_metrics = Column(JSON)
    
    # Model
    model_path = Column(String)  # Path to saved model
    feature_importance = Column(JSON)
    
    # Status
    status = Column(String, default="running", index=True)  # running, completed, failed
    
    # Deployment
    deployed = Column(Boolean, default=False, index=True)
    deployed_at = Column(DateTime)
    
    # Timestamps
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Metadata
    metadata = Column(JSON)
    
    __table_args__ = (
        Index("idx_experiments_type_status", "experiment_type", "status"),
    )


class MLFeature(Base):
    """ML Features - computed features for ML models."""
    __tablename__ = "ml_features"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identification
    symbol = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Features (stored as JSON for flexibility)
    features = Column(JSON, nullable=False)
    
    # Label (if known)
    label = Column(Float)
    label_type = Column(String)  # directional, regression, etc.
    
    # Metadata
    feature_version = Column(String, default="v1")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_ml_features_symbol_timestamp", "symbol", "timestamp"),
    )


class CircuitBreaker(Base):
    """Circuit breaker events."""
    __tablename__ = "circuit_breakers"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Event details
    trigger_type = Column(String, nullable=False, index=True)  # max_drawdown, error_rate, etc.
    trigger_value = Column(Float)
    threshold_value = Column(Float)
    
    # Status
    status = Column(String, nullable=False)  # triggered, resolved
    
    # Timestamps
    triggered_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime)
    
    # Metadata
    metadata = Column(JSON)

