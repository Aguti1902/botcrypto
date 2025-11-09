"""Base strategy class."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import pandas as pd


@dataclass
class Signal:
    """Trading signal."""
    symbol: str
    side: str  # "buy" or "sell"
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    confidence: float = 1.0
    reason: str = ""


class BaseStrategy(ABC):
    """Base class for trading strategies."""
    
    def __init__(self, name: str, config: dict):
        """Initialize strategy.
        
        Args:
            name: Strategy name
            config: Strategy configuration
        """
        self.name = name
        self.config = config
        self.enabled = config.get("enabled", False)
    
    @abstractmethod
    def generate_signals(self, symbol: str, data: pd.DataFrame) -> list[Signal]:
        """Generate trading signals.
        
        Args:
            symbol: Trading symbol
            data: OHLCV DataFrame
            
        Returns:
            List of signals
        """
        pass
    
    def is_enabled(self) -> bool:
        """Check if strategy is enabled."""
        return self.enabled

