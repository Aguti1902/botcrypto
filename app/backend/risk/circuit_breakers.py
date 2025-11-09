"""Circuit breaker system for emergency stops."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional
from loguru import logger

from utils.time import now_utc


@dataclass
class CircuitBreakerState:
    """Circuit breaker state."""
    triggered: bool
    trigger_time: Optional[datetime]
    trigger_reason: str
    can_resume_at: Optional[datetime]


class CircuitBreakerManager:
    """Manages circuit breakers for risk control.
    
    Triggers:
    - Max daily drawdown exceeded
    - Too many failed orders
    - Exchange connectivity issues
    - Manual kill switch
    """
    
    def __init__(
        self,
        max_daily_drawdown: float = 0.04,
        max_failed_orders_per_hour: int = 10,
        cooldown_minutes: int = 60,
    ):
        """Initialize circuit breaker manager.
        
        Args:
            max_daily_drawdown: Max daily drawdown (0.04 = 4%)
            max_failed_orders_per_hour: Max failed orders before trigger
            cooldown_minutes: Cooldown period after trigger
        """
        self.max_daily_drawdown = max_daily_drawdown
        self.max_failed_orders_per_hour = max_failed_orders_per_hour
        self.cooldown_minutes = cooldown_minutes
        
        self.state = CircuitBreakerState(
            triggered=False,
            trigger_time=None,
            trigger_reason="",
            can_resume_at=None,
        )
        
        self.failed_orders_history: list[datetime] = []
        self.daily_high_equity: Optional[float] = None
        self.last_reset_date: Optional[datetime] = None
    
    def check_drawdown(self, current_equity: float, starting_equity: float) -> bool:
        """Check if daily drawdown limit exceeded.
        
        Args:
            current_equity: Current equity
            starting_equity: Starting equity for the day
            
        Returns:
            True if breaker triggered
        """
        if self.state.triggered:
            return True
        
        # Update daily high
        now = now_utc()
        if self.last_reset_date is None or now.date() > self.last_reset_date.date():
            self.daily_high_equity = starting_equity
            self.last_reset_date = now
        
        if self.daily_high_equity is None:
            self.daily_high_equity = max(starting_equity, current_equity)
        else:
            self.daily_high_equity = max(self.daily_high_equity, current_equity)
        
        # Calculate drawdown from daily high
        drawdown = (self.daily_high_equity - current_equity) / self.daily_high_equity
        
        if drawdown >= self.max_daily_drawdown:
            self._trigger(
                f"Max daily drawdown exceeded: {drawdown:.2%} >= {self.max_daily_drawdown:.2%}"
            )
            return True
        
        return False
    
    def record_failed_order(self) -> bool:
        """Record a failed order and check if threshold exceeded.
        
        Returns:
            True if breaker triggered
        """
        if self.state.triggered:
            return True
        
        now = now_utc()
        self.failed_orders_history.append(now)
        
        # Clean old entries (> 1 hour)
        cutoff = now - timedelta(hours=1)
        self.failed_orders_history = [
            t for t in self.failed_orders_history if t > cutoff
        ]
        
        if len(self.failed_orders_history) >= self.max_failed_orders_per_hour:
            self._trigger(
                f"Too many failed orders: {len(self.failed_orders_history)} in last hour"
            )
            return True
        
        return False
    
    def manual_kill_switch(self, reason: str = "Manual kill switch activated"):
        """Manually trigger circuit breaker.
        
        Args:
            reason: Reason for manual trigger
        """
        self._trigger(reason)
    
    def _trigger(self, reason: str):
        """Trigger circuit breaker."""
        if self.state.triggered:
            return
        
        now = now_utc()
        self.state.triggered = True
        self.state.trigger_time = now
        self.state.trigger_reason = reason
        self.state.can_resume_at = now + timedelta(minutes=self.cooldown_minutes)
        
        logger.critical(
            f"🚨 CIRCUIT BREAKER TRIGGERED: {reason}",
            extra={
                "trigger_time": now.isoformat(),
                "can_resume_at": self.state.can_resume_at.isoformat(),
            },
        )
    
    def can_trade(self) -> bool:
        """Check if trading is allowed.
        
        Returns:
            True if trading is allowed
        """
        if not self.state.triggered:
            return True
        
        # Check if cooldown period has passed
        now = now_utc()
        if self.state.can_resume_at and now >= self.state.can_resume_at:
            logger.warning("Circuit breaker cooldown period passed, but manual reset required")
        
        return False
    
    def reset(self, force: bool = False):
        """Reset circuit breaker.
        
        Args:
            force: Force reset even if cooldown not complete
        """
        if not self.state.triggered:
            return
        
        now = now_utc()
        
        if not force and self.state.can_resume_at and now < self.state.can_resume_at:
            remaining = (self.state.can_resume_at - now).total_seconds() / 60
            logger.warning(
                f"Cannot reset circuit breaker: {remaining:.1f} minutes remaining in cooldown"
            )
            return
        
        logger.info(
            f"Circuit breaker reset: was triggered at {self.state.trigger_time} "
            f"for reason: {self.state.trigger_reason}"
        )
        
        self.state = CircuitBreakerState(
            triggered=False,
            trigger_time=None,
            trigger_reason="",
            can_resume_at=None,
        )
        
        self.failed_orders_history.clear()
    
    def get_status(self) -> Dict:
        """Get circuit breaker status.
        
        Returns:
            Status dictionary
        """
        return {
            "triggered": self.state.triggered,
            "can_trade": self.can_trade(),
            "trigger_time": self.state.trigger_time.isoformat() if self.state.trigger_time else None,
            "trigger_reason": self.state.trigger_reason,
            "can_resume_at": self.state.can_resume_at.isoformat() if self.state.can_resume_at else None,
            "failed_orders_last_hour": len(self.failed_orders_history),
        }

