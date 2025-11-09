"""Portfolio rebalancing logic."""
from typing import Dict
from loguru import logger


class Rebalancer:
    """Rebalance portfolio to target allocation."""
    
    def __init__(
        self,
        rebalance_threshold_pct: float = 0.02,
        cost_aware: bool = True,
        fee_bps: float = 10.0,
    ):
        """Initialize rebalancer.
        
        Args:
            rebalance_threshold_pct: Min deviation to trigger rebalance (0.02 = 2%)
            cost_aware: Whether to consider transaction costs
            fee_bps: Trading fees in basis points
        """
        self.rebalance_threshold_pct = rebalance_threshold_pct
        self.cost_aware = cost_aware
        self.fee_bps = fee_bps
    
    def calculate_rebalance_trades(
        self,
        current_allocation: Dict[str, float],
        target_allocation: Dict[str, float],
        prices: Dict[str, float],
    ) -> Dict[str, Dict[str, float]]:
        """Calculate trades needed to rebalance.
        
        Args:
            current_allocation: Current value per symbol
            target_allocation: Target value per symbol
            prices: Current prices per symbol
            
        Returns:
            Dictionary of symbol -> {
                'current_value': float,
                'target_value': float,
                'delta_value': float,
                'delta_quantity': float,
                'side': 'buy' or 'sell',
            }
        """
        trades = {}
        total_value = sum(current_allocation.values())
        
        for symbol in set(list(current_allocation.keys()) + list(target_allocation.keys())):
            current_value = current_allocation.get(symbol, 0.0)
            target_value = target_allocation.get(symbol, 0.0)
            delta_value = target_value - current_value
            
            # Check if deviation exceeds threshold
            if total_value > 0:
                deviation_pct = abs(delta_value) / total_value
            else:
                deviation_pct = 0.0
            
            if deviation_pct < self.rebalance_threshold_pct:
                continue
            
            # Cost-aware: only rebalance if benefit > cost
            if self.cost_aware:
                estimated_cost = abs(delta_value) * (self.fee_bps / 10000)
                if abs(delta_value) < estimated_cost * 2:  # Need at least 2x benefit
                    logger.debug(
                        f"Skipping rebalance of {symbol}: cost ({estimated_cost:.2f}) "
                        f"too high vs delta ({abs(delta_value):.2f})"
                    )
                    continue
            
            price = prices.get(symbol, 0.0)
            if price == 0:
                logger.warning(f"No price for {symbol}, skipping")
                continue
            
            delta_quantity = delta_value / price
            side = "buy" if delta_quantity > 0 else "sell"
            
            trades[symbol] = {
                'current_value': current_value,
                'target_value': target_value,
                'delta_value': delta_value,
                'delta_quantity': abs(delta_quantity),
                'side': side,
                'price': price,
            }
        
        logger.info(f"Rebalance trades calculated: {len(trades)} symbols")
        return trades
    
    def should_rebalance(
        self,
        current_allocation: Dict[str, float],
        target_allocation: Dict[str, float],
    ) -> bool:
        """Check if rebalancing is needed.
        
        Args:
            current_allocation: Current value per symbol
            target_allocation: Target value per symbol
            
        Returns:
            True if rebalancing is needed
        """
        total_value = sum(current_allocation.values())
        
        if total_value == 0:
            return False
        
        for symbol in set(list(current_allocation.keys()) + list(target_allocation.keys())):
            current_value = current_allocation.get(symbol, 0.0)
            target_value = target_allocation.get(symbol, 0.0)
            delta_value = abs(target_value - current_value)
            deviation_pct = delta_value / total_value
            
            if deviation_pct >= self.rebalance_threshold_pct:
                return True
        
        return False

