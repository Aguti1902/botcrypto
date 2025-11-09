"""Fees calculation."""


class FeesCalculator:
    """Calculate trading fees."""
    
    def __init__(self, maker_fee_bps: float = 10.0, taker_fee_bps: float = 10.0):
        """Initialize fees calculator.
        
        Args:
            maker_fee_bps: Maker fee in basis points
            taker_fee_bps: Taker fee in basis points
        """
        self.maker_fee_bps = maker_fee_bps
        self.taker_fee_bps = taker_fee_bps
    
    def calculate_fee(self, notional: float, is_maker: bool = False) -> float:
        """Calculate fee for a trade.
        
        Args:
            notional: Notional value of trade
            is_maker: Whether trade is maker
            
        Returns:
            Fee amount
        """
        fee_bps = self.maker_fee_bps if is_maker else self.taker_fee_bps
        return notional * (fee_bps / 10000)

