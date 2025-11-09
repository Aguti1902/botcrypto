"""Tests for risk limits."""
import pytest
from risk.limits import RiskLimits


def test_position_exposure_limit():
    """Test position exposure limit."""
    limits = RiskLimits(max_position_exposure_pct=0.25)
    
    equity = 10000
    position_value = 3000  # 30% of equity
    
    can_place, reason = limits.can_place_order(
        symbol="BTC/USDT",
        side="buy",
        position_value=position_value,
        equity=equity,
    )
    
    assert can_place is False
    assert "Position exposure limit exceeded" in reason


def test_total_exposure_limit():
    """Test total exposure limit."""
    limits = RiskLimits(max_total_exposure_pct=0.80)
    
    # Set existing exposures to 70%
    limits.update_position_exposure("BTC/USDT", 4000)
    limits.update_position_exposure("ETH/USDT", 3000)
    
    equity = 10000
    position_value = 2000  # Would bring total to 90%
    
    can_place, reason = limits.can_place_order(
        symbol="SOL/USDT",
        side="buy",
        position_value=position_value,
        equity=equity,
    )
    
    assert can_place is False
    assert "Total exposure limit exceeded" in reason


def test_rate_limits():
    """Test trade rate limits."""
    limits = RiskLimits(max_trades_per_minute=2)
    
    # Record 2 trades
    limits.record_trade("BTC/USDT", "buy")
    limits.record_trade("ETH/USDT", "buy")
    
    # Try to place 3rd trade
    can_place, reason = limits.can_place_order(
        symbol="SOL/USDT",
        side="buy",
        position_value=100,
        equity=10000,
    )
    
    assert can_place is False
    assert "rate limit exceeded" in reason.lower()

