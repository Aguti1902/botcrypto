"""Risk limits enforcement."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List
from loguru import logger

from utils.time import now_utc


@dataclass
class TradeRecord:
    """Record of a trade for rate limiting."""
    timestamp: datetime
    symbol: str
    side: str


class RiskLimits:
    """Enforce risk limits on trading activity.
    
    Limits:
    - Max trades per minute
    - Max trades per day
    - Max position exposure per symbol
    - Max total exposure
    """
    
    def __init__(
        self,
        max_trades_per_minute: int = 6,
        max_trades_per_day: int = 1200,
        max_position_exposure_pct: float = 0.25,
        max_total_exposure_pct: float = 0.80,
    ):
        """Initialize risk limits.
        
        Args:
            max_trades_per_minute: Max trades per minute
            max_trades_per_day: Max trades per day
            max_position_exposure_pct: Max exposure per position (0.25 = 25%)
            max_total_exposure_pct: Max total exposure (0.80 = 80%)
        """
        self.max_trades_per_minute = max_trades_per_minute
        self.max_trades_per_day = max_trades_per_day
        self.max_position_exposure_pct = max_position_exposure_pct
        self.max_total_exposure_pct = max_total_exposure_pct
        
        self.trade_history: List[TradeRecord] = []
        self.position_exposures: Dict[str, float] = {}  # symbol -> exposure value
    
    def can_place_order(
        self,
        symbol: str,
        side: str,
        position_value: float,
        equity: float,
    ) -> tuple[bool, str]:
        """Check if order can be placed within risk limits.
        
        Args:
            symbol: Trading symbol
            side: Order side (buy/sell)
            position_value: Value of proposed position
            equity: Current account equity
            
        Returns:
            Tuple of (can_place, reason_if_not)
        """
        now = now_utc()
        
        # Check rate limits
        can_trade, reason = self._check_rate_limits(now)
        if not can_trade:
            return False, reason
        
        # Check position exposure
        current_exposure = self.position_exposures.get(symbol, 0.0)
        new_exposure = current_exposure + position_value
        exposure_pct = new_exposure / equity
        
        if exposure_pct > self.max_position_exposure_pct:
            return False, (
                f"Position exposure limit exceeded for {symbol}: "
                f"{exposure_pct:.2%} > {self.max_position_exposure_pct:.2%}"
            )
        
        # Check total exposure
        total_exposure = sum(self.position_exposures.values()) + position_value
        total_exposure_pct = total_exposure / equity
        
        if total_exposure_pct > self.max_total_exposure_pct:
            return False, (
                f"Total exposure limit exceeded: "
                f"{total_exposure_pct:.2%} > {self.max_total_exposure_pct:.2%}"
            )
        
        return True, ""
    
    def record_trade(self, symbol: str, side: str):
        """Record a trade for rate limiting.
        
        Args:
            symbol: Trading symbol
            side: Order side
        """
        now = now_utc()
        self.trade_history.append(TradeRecord(
            timestamp=now,
            symbol=symbol,
            side=side,
        ))
        
        logger.debug(f"Trade recorded: {symbol} {side}")
    
    def update_position_exposure(self, symbol: str, exposure: float):
        """Update position exposure for a symbol.
        
        Args:
            symbol: Trading symbol
            exposure: Current exposure value (0 if no position)
        """
        if exposure <= 0:
            self.position_exposures.pop(symbol, None)
        else:
            self.position_exposures[symbol] = exposure
    
    def _check_rate_limits(self, now: datetime) -> tuple[bool, str]:
        """Check trade rate limits.
        
        Args:
            now: Current time
            
        Returns:
            Tuple of (can_trade, reason_if_not)
        """
        # Clean old trades
        one_minute_ago = now - timedelta(minutes=1)
        one_day_ago = now - timedelta(days=1)
        
        self.trade_history = [
            t for t in self.trade_history if t.timestamp > one_day_ago
        ]
        
        # Check per-minute limit
        trades_last_minute = [
            t for t in self.trade_history if t.timestamp > one_minute_ago
        ]
        
        if len(trades_last_minute) >= self.max_trades_per_minute:
            return False, (
                f"Trade rate limit exceeded: {len(trades_last_minute)} trades in last minute"
            )
        
        # Check per-day limit
        if len(self.trade_history) >= self.max_trades_per_day:
            return False, (
                f"Daily trade limit exceeded: {len(self.trade_history)} trades today"
            )
        
        return True, ""
    
    def get_status(self) -> Dict:
        """Get risk limits status.
        
        Returns:
            Status dictionary
        """
        now = now_utc()
        one_minute_ago = now - timedelta(minutes=1)
        
        trades_last_minute = [
            t for t in self.trade_history if t.timestamp > one_minute_ago
        ]
        
        total_exposure = sum(self.position_exposures.values())
        
        return {
            "trades_last_minute": len(trades_last_minute),
            "trades_today": len(self.trade_history),
            "max_trades_per_minute": self.max_trades_per_minute,
            "max_trades_per_day": self.max_trades_per_day,
            "position_exposures": self.position_exposures,
            "total_exposure": total_exposure,
            "max_position_exposure_pct": self.max_position_exposure_pct,
            "max_total_exposure_pct": self.max_total_exposure_pct,
        }

