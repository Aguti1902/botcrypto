"""Portfolio performance metrics calculation."""
import numpy as np
import pandas as pd
from typing import Dict, Optional


class MetricsCalculator:
    """Calculate portfolio performance metrics."""
    
    @staticmethod
    def calculate_sharpe_ratio(
        returns: pd.Series,
        risk_free_rate: float = 0.0,
        periods_per_year: int = 365,
    ) -> float:
        """Calculate Sharpe ratio.
        
        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate
            periods_per_year: Periods per year for annualization
            
        Returns:
            Sharpe ratio
        """
        if len(returns) < 2 or returns.std() == 0:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / periods_per_year)
        sharpe = excess_returns.mean() / returns.std() * np.sqrt(periods_per_year)
        return sharpe
    
    @staticmethod
    def calculate_sortino_ratio(
        returns: pd.Series,
        risk_free_rate: float = 0.0,
        periods_per_year: int = 365,
    ) -> float:
        """Calculate Sortino ratio (uses downside deviation)."""
        if len(returns) < 2:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / periods_per_year)
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0
        
        sortino = excess_returns.mean() / downside_returns.std() * np.sqrt(periods_per_year)
        return sortino
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: pd.Series) -> float:
        """Calculate maximum drawdown.
        
        Args:
            equity_curve: Series of equity values
            
        Returns:
            Max drawdown as positive fraction
        """
        if len(equity_curve) < 2:
            return 0.0
        
        cummax = equity_curve.cummax()
        drawdown = (equity_curve - cummax) / cummax
        max_dd = abs(drawdown.min())
        return max_dd
    
    @staticmethod
    def calculate_calmar_ratio(
        returns: pd.Series,
        equity_curve: pd.Series,
        periods_per_year: int = 365,
    ) -> float:
        """Calculate Calmar ratio (CAGR / Max DD)."""
        if len(returns) < 2 or len(equity_curve) < 2:
            return 0.0
        
        # CAGR
        total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
        years = len(equity_curve) / periods_per_year
        cagr = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0.0
        
        # Max DD
        max_dd = MetricsCalculator.calculate_max_drawdown(equity_curve)
        
        if max_dd == 0:
            return 0.0
        
        calmar = cagr / max_dd
        return calmar
    
    @staticmethod
    def calculate_win_rate(trades: list) -> float:
        """Calculate win rate from trades.
        
        Args:
            trades: List of trade dictionaries with 'pnl' field
            
        Returns:
            Win rate (0.0 to 1.0)
        """
        if not trades:
            return 0.0
        
        winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
        return len(winning_trades) / len(trades)
    
    @staticmethod
    def calculate_profit_factor(trades: list) -> float:
        """Calculate profit factor (gross profit / gross loss).
        
        Args:
            trades: List of trade dictionaries with 'pnl' field
            
        Returns:
            Profit factor
        """
        if not trades:
            return 0.0
        
        gross_profit = sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0)
        gross_loss = abs(sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return gross_profit / gross_loss
    
    @staticmethod
    def calculate_metrics(
        returns: pd.Series,
        equity_curve: pd.Series,
        trades: Optional[list] = None,
        periods_per_year: int = 365,
    ) -> Dict:
        """Calculate comprehensive metrics.
        
        Args:
            returns: Series of returns
            equity_curve: Series of equity values
            trades: Optional list of trades
            periods_per_year: Periods per year
            
        Returns:
            Dictionary of metrics
        """
        metrics = {
            'sharpe_ratio': MetricsCalculator.calculate_sharpe_ratio(returns, periods_per_year=periods_per_year),
            'sortino_ratio': MetricsCalculator.calculate_sortino_ratio(returns, periods_per_year=periods_per_year),
            'max_drawdown': MetricsCalculator.calculate_max_drawdown(equity_curve),
            'calmar_ratio': MetricsCalculator.calculate_calmar_ratio(returns, equity_curve, periods_per_year),
        }
        
        if len(equity_curve) >= 2:
            total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
            years = len(equity_curve) / periods_per_year
            cagr = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0.0
            metrics['cagr'] = cagr
            metrics['total_return'] = total_return
        else:
            metrics['cagr'] = 0.0
            metrics['total_return'] = 0.0
        
        if trades:
            metrics['win_rate'] = MetricsCalculator.calculate_win_rate(trades)
            metrics['profit_factor'] = MetricsCalculator.calculate_profit_factor(trades)
            metrics['num_trades'] = len(trades)
        
        return metrics

