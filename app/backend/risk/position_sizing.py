"""Position sizing logic."""
from typing import Optional
from loguru import logger


class PositionSizer:
    """Calculate position sizes based on risk parameters."""
    
    def __init__(
        self,
        risk_per_trade: float = 0.01,
        max_position_pct: float = 0.25,
    ):
        """Initialize position sizer.
        
        Args:
            risk_per_trade: Max risk per trade as fraction of equity
            max_position_pct: Max position size as fraction of equity
        """
        self.risk_per_trade = risk_per_trade
        self.max_position_pct = max_position_pct
    
    def calculate_size(
        self,
        equity: float,
        entry_price: float,
        stop_loss: float,
        side: str = "buy",
        confidence: float = 1.0,
    ) -> float:
        """Calculate position size based on risk.
        
        Args:
            equity: Current account equity
            entry_price: Entry price
            stop_loss: Stop loss price
            side: "buy" or "sell"
            confidence: Confidence level (0-1) to scale size
            
        Returns:
            Position size in base currency
        """
        if stop_loss <= 0 or entry_price <= 0:
            logger.warning("Invalid prices for position sizing")
            return 0.0
        
        # Calculate risk per unit
        if side == "buy":
            risk_per_unit = abs(entry_price - stop_loss)
        else:
            risk_per_unit = abs(stop_loss - entry_price)
        
        if risk_per_unit == 0:
            logger.warning("Stop loss equals entry price")
            return 0.0
        
        # Risk amount in quote currency
        risk_amount = equity * self.risk_per_trade * confidence
        
        # Position size
        position_size = risk_amount / risk_per_unit
        
        # Apply max position limit
        max_position_value = equity * self.max_position_pct
        max_position_size = max_position_value / entry_price
        
        position_size = min(position_size, max_position_size)
        
        logger.debug(
            f"Position sizing: equity={equity:.2f}, risk={risk_amount:.2f}, "
            f"size={position_size:.6f}, confidence={confidence:.2f}"
        )
        
        return position_size
    
    def calculate_size_fixed_pct(
        self,
        equity: float,
        entry_price: float,
        size_pct: float = 0.01,
    ) -> float:
        """Calculate position size as fixed percentage of equity.
        
        Args:
            equity: Current account equity
            entry_price: Entry price
            size_pct: Size as fraction of equity
            
        Returns:
            Position size in base currency
        """
        position_value = equity * size_pct
        position_size = position_value / entry_price
        
        return position_size

