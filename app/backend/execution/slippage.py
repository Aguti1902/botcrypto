"""Slippage simulation."""
import random


class SlippageSimulator:
    """Simulate slippage for paper trading."""
    
    def __init__(self, slippage_bps: float = 2.0, variance_bps: float = 1.0):
        """Initialize slippage simulator.
        
        Args:
            slippage_bps: Average slippage in basis points
            variance_bps: Variance in slippage
        """
        self.slippage_bps = slippage_bps
        self.variance_bps = variance_bps
    
    def apply_slippage(self, price: float, side: str) -> float:
        """Apply slippage to a price.
        
        Args:
            price: Original price
            side: "buy" or "sell"
            
        Returns:
            Price with slippage
        """
        # Random slippage within variance
        slippage = random.gauss(self.slippage_bps, self.variance_bps) / 10000
        
        if side == "buy":
            # Buying - slippage increases price
            return price * (1 + abs(slippage))
        else:
            # Selling - slippage decreases price
            return price * (1 - abs(slippage))

