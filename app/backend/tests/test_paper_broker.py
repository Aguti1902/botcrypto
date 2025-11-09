"""Tests for paper broker."""
import pytest
from paper.broker_paper import PaperBroker


@pytest.mark.asyncio
async def test_paper_broker_buy():
    """Test paper broker buy order."""
    broker = PaperBroker(initial_cash=10000)
    
    result = await broker.create_market_order(
        symbol="BTC/USDT",
        side="buy",
        quantity=0.1,
        current_price=50000,
    )
    
    assert result.status == "filled"
    assert result.filled_quantity == 0.1
    assert broker.cash < 10000  # Cash should decrease


@pytest.mark.asyncio
async def test_paper_broker_insufficient_cash():
    """Test paper broker rejects order with insufficient cash."""
    broker = PaperBroker(initial_cash=1000)
    
    result = await broker.create_market_order(
        symbol="BTC/USDT",
        side="buy",
        quantity=1.0,  # Would cost ~$50,000
        current_price=50000,
    )
    
    assert result.status == "rejected"
    assert "insufficient_cash" in result.metadata.get("reject_reason", "")


@pytest.mark.asyncio
async def test_paper_broker_sell():
    """Test paper broker sell order."""
    broker = PaperBroker(initial_cash=10000)
    
    # First buy
    await broker.create_market_order(
        symbol="BTC/USDT",
        side="buy",
        quantity=0.1,
        current_price=50000,
    )
    
    # Then sell
    result = await broker.create_market_order(
        symbol="BTC/USDT",
        side="sell",
        quantity=0.1,
        current_price=51000,
    )
    
    assert result.status == "filled"
    assert broker.cash > 10000  # Made profit

