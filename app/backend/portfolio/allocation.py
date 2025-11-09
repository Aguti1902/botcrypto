"""Portfolio allocation strategies."""
import numpy as np
import pandas as pd
from typing import Dict, List
from loguru import logger


class PortfolioAllocator:
    """Allocate capital across assets.
    
    Strategies:
    - Equal weight
    - Risk parity (inverse volatility)
    - Momentum-based
    """
    
    def __init__(
        self,
        strategy: str = "risk_parity",
        target_vol_annual: float = 0.25,
    ):
        """Initialize allocator.
        
        Args:
            strategy: Allocation strategy (equal_weight, risk_parity, momentum)
            target_vol_annual: Target annual volatility for risk parity
        """
        self.strategy = strategy
        self.target_vol_annual = target_vol_annual
    
    def allocate(
        self,
        symbols: List[str],
        prices: Dict[str, pd.DataFrame],
        total_equity: float,
    ) -> Dict[str, float]:
        """Calculate target allocation.
        
        Args:
            symbols: List of symbols
            prices: Dictionary of symbol -> price DataFrame
            total_equity: Total portfolio equity
            
        Returns:
            Dictionary of symbol -> target value
        """
        if self.strategy == "equal_weight":
            return self._equal_weight(symbols, total_equity)
        elif self.strategy == "risk_parity":
            return self._risk_parity(symbols, prices, total_equity)
        elif self.strategy == "momentum":
            return self._momentum(symbols, prices, total_equity)
        else:
            logger.warning(f"Unknown strategy: {self.strategy}, using equal weight")
            return self._equal_weight(symbols, total_equity)
    
    def _equal_weight(self, symbols: List[str], total_equity: float) -> Dict[str, float]:
        """Equal weight allocation."""
        allocation_per_symbol = total_equity / len(symbols)
        return {symbol: allocation_per_symbol for symbol in symbols}
    
    def _risk_parity(
        self,
        symbols: List[str],
        prices: Dict[str, pd.DataFrame],
        total_equity: float,
    ) -> Dict[str, float]:
        """Risk parity allocation (inverse volatility weighting)."""
        # Calculate volatilities
        vols = {}
        for symbol in symbols:
            if symbol not in prices or prices[symbol].empty:
                vols[symbol] = 0.01  # Default if no data
                continue
            
            returns = prices[symbol]['close'].pct_change().dropna()
            
            if len(returns) < 20:
                vols[symbol] = 0.01
                continue
            
            # Annualized volatility (assuming daily returns)
            daily_vol = returns.std()
            annual_vol = daily_vol * np.sqrt(365)
            vols[symbol] = annual_vol if annual_vol > 0 else 0.01
        
        # Inverse volatility weights
        inv_vols = {symbol: 1.0 / vol for symbol, vol in vols.items()}
        total_inv_vol = sum(inv_vols.values())
        
        weights = {symbol: inv_vol / total_inv_vol for symbol, inv_vol in inv_vols.items()}
        
        # Scale to target volatility
        portfolio_vol = sum(weights[s] * vols[s] for s in symbols)
        if portfolio_vol > 0:
            scale = self.target_vol_annual / portfolio_vol
            scale = min(scale, 1.0)  # Don't leverage
        else:
            scale = 1.0
        
        allocation = {symbol: total_equity * weights[symbol] * scale for symbol in symbols}
        
        logger.debug(f"Risk parity allocation: {allocation}")
        return allocation
    
    def _momentum(
        self,
        symbols: List[str],
        prices: Dict[str, pd.DataFrame],
        total_equity: float,
    ) -> Dict[str, float]:
        """Momentum-based allocation."""
        # Calculate momentum scores (e.g., 20-day returns)
        scores = {}
        
        for symbol in symbols:
            if symbol not in prices or prices[symbol].empty or len(prices[symbol]) < 20:
                scores[symbol] = 0.0
                continue
            
            close = prices[symbol]['close']
            momentum = (close.iloc[-1] / close.iloc[-20] - 1) if len(close) >= 20 else 0.0
            scores[symbol] = max(momentum, 0.0)  # Only positive momentum
        
        total_score = sum(scores.values())
        
        if total_score == 0:
            # Fall back to equal weight
            return self._equal_weight(symbols, total_equity)
        
        allocation = {symbol: total_equity * (score / total_score) for symbol, score in scores.items()}
        
        logger.debug(f"Momentum allocation: {allocation}")
        return allocation

