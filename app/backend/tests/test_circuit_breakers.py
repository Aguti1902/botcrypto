"""Tests for circuit breakers."""
import pytest
from risk.circuit_breakers import CircuitBreakerManager


def test_circuit_breaker_drawdown():
    """Test circuit breaker triggers on max drawdown."""
    cb = CircuitBreakerManager(max_daily_drawdown=0.04)
    
    # Start with $10,000
    starting_equity = 10000
    
    # Drop to $9,500 (5% drawdown)
    triggered = cb.check_drawdown(current_equity=9500, starting_equity=starting_equity)
    
    assert triggered is True
    assert cb.state.triggered is True
    assert cb.can_trade() is False


def test_circuit_breaker_failed_orders():
    """Test circuit breaker triggers on too many failed orders."""
    cb = CircuitBreakerManager(max_failed_orders_per_hour=3)
    
    # Record 3 failed orders
    for _ in range(3):
        triggered = cb.record_failed_order()
    
    assert triggered is True
    assert cb.can_trade() is False


def test_circuit_breaker_reset():
    """Test circuit breaker can be reset."""
    cb = CircuitBreakerManager()
    
    cb.manual_kill_switch("Test")
    assert cb.can_trade() is False
    
    cb.reset(force=True)
    assert cb.can_trade() is True

