"""Trend following strategy with ATR-based stops."""
import pandas as pd
import pandas_ta as ta
from typing import List
from .base import BaseStrategy, Signal


class TrendATRStrategy(BaseStrategy):
    """Trend following using SMA crossover + ATR for stops."""
    
    def __init__(self, config: dict):
        super().__init__("trend_atr", config)
        self.sma_fast = config.get("sma_fast", 50)
        self.sma_slow = config.get("sma_slow", 200)
        self.atr_period = config.get("atr_period", 14)
        self.atr_mult_sl = config.get("atr_mult_sl", 2.0)
        self.atr_mult_tp = config.get("atr_mult_tp", 2.0)
    
    def generate_signals(self, symbol: str, data: pd.DataFrame) -> List[Signal]:
        """Generate trend signals."""
        if len(data) < max(self.sma_slow, self.atr_period):
            return []
        
        df = data.copy()
        
        # Calculate indicators
        df['sma_fast'] = df['close'].rolling(self.sma_fast).mean()
        df['sma_slow'] = df['close'].rolling(self.sma_slow).mean()
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=self.atr_period)
        
        # Latest values
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        signals = []
        
        # Bullish crossover
        if prev['sma_fast'] <= prev['sma_slow'] and last['sma_fast'] > last['sma_slow']:
            stop_loss = last['close'] - (self.atr_mult_sl * last['atr'])
            take_profit = last['close'] + (self.atr_mult_tp * self.atr_mult_sl * last['atr'])
            
            signals.append(Signal(
                symbol=symbol,
                side="buy",
                entry_price=last['close'],
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=1.0,
                reason=f"SMA crossover bullish: {self.sma_fast}/{self.sma_slow}",
            ))
        
        # Bearish crossover
        elif prev['sma_fast'] >= prev['sma_slow'] and last['sma_fast'] < last['sma_slow']:
            stop_loss = last['close'] + (self.atr_mult_sl * last['atr'])
            take_profit = last['close'] - (self.atr_mult_tp * self.atr_mult_sl * last['atr'])
            
            signals.append(Signal(
                symbol=symbol,
                side="sell",
                entry_price=last['close'],
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=1.0,
                reason=f"SMA crossover bearish: {self.sma_fast}/{self.sma_slow}",
            ))
        
        return signals

