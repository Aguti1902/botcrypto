"""PnL calculation."""
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class PnLSnapshot:
    """PnL snapshot."""
    total_pnl: float
    realized_pnl: float
    unrealized_pnl: float
    by_symbol: Dict[str, float]


class PnLCalculator:
    """Calculate portfolio PnL."""
    
    def __init__(self):
        """Initialize PnL calculator."""
        self.realized_pnl = 0.0
        self.symbol_realized_pnl: Dict[str, float] = {}
    
    def calculate_unrealized_pnl(
        self,
        positions: List[Dict],
        current_prices: Dict[str, float],
    ) -> Dict[str, float]:
        """Calculate unrealized PnL for open positions.
        
        Args:
            positions: List of position dictionaries
            current_prices: Current prices per symbol
            
        Returns:
            Dictionary of symbol -> unrealized PnL
        """
        unrealized = {}
        
        for pos in positions:
            symbol = pos['symbol']
            entry_price = pos['entry_price']
            quantity = pos['quantity']
            side = pos['side']
            
            current_price = current_prices.get(symbol, entry_price)
            
            if side == "buy":
                pnl = (current_price - entry_price) * quantity
            else:
                pnl = (entry_price - current_price) * quantity
            
            unrealized[symbol] = pnl
        
        return unrealized
    
    def record_realized_pnl(self, symbol: str, pnl: float):
        """Record realized PnL from closed position.
        
        Args:
            symbol: Trading symbol
            pnl: Realized PnL
        """
        self.realized_pnl += pnl
        self.symbol_realized_pnl[symbol] = self.symbol_realized_pnl.get(symbol, 0.0) + pnl
    
    def get_snapshot(
        self,
        positions: List[Dict],
        current_prices: Dict[str, float],
    ) -> PnLSnapshot:
        """Get PnL snapshot.
        
        Args:
            positions: Open positions
            current_prices: Current prices
            
        Returns:
            PnLSnapshot
        """
        unrealized_by_symbol = self.calculate_unrealized_pnl(positions, current_prices)
        total_unrealized = sum(unrealized_by_symbol.values())
        
        return PnLSnapshot(
            total_pnl=self.realized_pnl + total_unrealized,
            realized_pnl=self.realized_pnl,
            unrealized_pnl=total_unrealized,
            by_symbol={
                symbol: self.symbol_realized_pnl.get(symbol, 0.0) + unrealized_by_symbol.get(symbol, 0.0)
                for symbol in set(list(self.symbol_realized_pnl.keys()) + list(unrealized_by_symbol.keys()))
            },
        )

