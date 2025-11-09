"""Paper trading broker - simulates order execution."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

from exchanges.base import OrderResult, Balance
from execution.slippage import SlippageSimulator
from execution.fees import FeesCalculator
from utils.time import now_utc


class PaperBroker:
    """Paper trading broker for simulation."""
    
    def __init__(
        self,
        initial_cash: float = 10000.0,
        slippage_bps: float = 2.0,
        fees_bps: float = 10.0,
    ):
        """Initialize paper broker.
        
        Args:
            initial_cash: Initial cash balance
            slippage_bps: Slippage in basis points
            fees_bps: Fees in basis points
        """
        self.cash = initial_cash
        self.initial_cash = initial_cash
        self.positions: Dict[str, Dict] = {}  # symbol -> position
        self.orders: Dict[str, OrderResult] = {}  # order_id -> order
        
        self.slippage_sim = SlippageSimulator(slippage_bps=slippage_bps)
        self.fees_calc = FeesCalculator(taker_fee_bps=fees_bps)
        
        logger.info(f"Paper broker initialized: cash={initial_cash}")
    
    async def create_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        current_price: float,
        client_order_id: Optional[str] = None,
    ) -> OrderResult:
        """Simulate market order execution.
        
        Args:
            symbol: Trading symbol
            side: "buy" or "sell"
            quantity: Order quantity
            current_price: Current market price
            client_order_id: Optional client order ID
            
        Returns:
            OrderResult
        """
        order_id = str(uuid.uuid4())
        
        # Apply slippage
        exec_price = self.slippage_sim.apply_slippage(current_price, side)
        
        # Calculate notional and fee
        notional = exec_price * quantity
        fee = self.fees_calc.calculate_fee(notional, is_maker=False)
        
        # Check if we have enough cash
        if side == "buy":
            required_cash = notional + fee
            if required_cash > self.cash:
                logger.warning(f"Insufficient cash for buy: {required_cash} > {self.cash}")
                return OrderResult(
                    order_id=order_id,
                    client_order_id=client_order_id,
                    symbol=symbol,
                    side=side,
                    order_type="market",
                    status="rejected",
                    quantity=quantity,
                    filled_quantity=0.0,
                    price=None,
                    average_fill_price=None,
                    timestamp=now_utc(),
                    metadata={"reject_reason": "insufficient_cash"},
                )
            
            # Execute buy
            self.cash -= required_cash
            self._update_position(symbol, quantity, exec_price, side)
        else:
            # Check position
            if symbol not in self.positions or self.positions[symbol]['quantity'] < quantity:
                logger.warning(f"Insufficient position for sell: {symbol}")
                return OrderResult(
                    order_id=order_id,
                    client_order_id=client_order_id,
                    symbol=symbol,
                    side=side,
                    order_type="market",
                    status="rejected",
                    quantity=quantity,
                    filled_quantity=0.0,
                    price=None,
                    average_fill_price=None,
                    timestamp=now_utc(),
                    metadata={"reject_reason": "insufficient_position"},
                )
            
            # Execute sell
            self.cash += (notional - fee)
            self._update_position(symbol, -quantity, exec_price, side)
        
        result = OrderResult(
            order_id=order_id,
            client_order_id=client_order_id,
            symbol=symbol,
            side=side,
            order_type="market",
            status="filled",
            quantity=quantity,
            filled_quantity=quantity,
            price=None,
            average_fill_price=exec_price,
            timestamp=now_utc(),
            metadata={"fee": fee, "slippage_price": exec_price},
        )
        
        self.orders[order_id] = result
        
        logger.info(
            f"Paper order filled: {symbol} {side} {quantity} @ {exec_price:.2f}, "
            f"fee={fee:.2f}, cash={self.cash:.2f}"
        )
        
        return result
    
    def _update_position(self, symbol: str, quantity: float, price: float, side: str):
        """Update position."""
        if symbol not in self.positions:
            self.positions[symbol] = {
                'quantity': 0.0,
                'avg_price': 0.0,
            }
        
        pos = self.positions[symbol]
        
        if side == "buy":
            # Add to position
            total_cost = (pos['quantity'] * pos['avg_price']) + (quantity * price)
            pos['quantity'] += quantity
            pos['avg_price'] = total_cost / pos['quantity'] if pos['quantity'] > 0 else 0.0
        else:
            # Reduce position
            pos['quantity'] -= quantity
            if pos['quantity'] <= 0:
                del self.positions[symbol]
    
    def get_balance(self) -> List[Balance]:
        """Get account balance."""
        balances = [
            Balance(
                currency="USD",
                free=self.cash,
                used=0.0,
                total=self.cash,
            )
        ]
        
        for symbol, pos in self.positions.items():
            base_currency = symbol.split("/")[0]
            balances.append(Balance(
                currency=base_currency,
                free=pos['quantity'],
                used=0.0,
                total=pos['quantity'],
            ))
        
        return balances
    
    def get_positions(self) -> List[Dict]:
        """Get open positions."""
        return [
            {
                'symbol': symbol,
                'quantity': pos['quantity'],
                'avg_price': pos['avg_price'],
            }
            for symbol, pos in self.positions.items()
        ]
    
    def get_equity(self, current_prices: Dict[str, float]) -> float:
        """Calculate total equity.
        
        Args:
            current_prices: Current prices per symbol
            
        Returns:
            Total equity
        """
        equity = self.cash
        
        for symbol, pos in self.positions.items():
            price = current_prices.get(symbol, pos['avg_price'])
            equity += pos['quantity'] * price
        
        return equity

