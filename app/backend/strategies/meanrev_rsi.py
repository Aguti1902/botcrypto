"""Mean reversion strategy using RSI and Bollinger Bands."""
import pandas as pd
import pandas_ta as ta
from typing import List
from .base import BaseStrategy, Signal


class MeanRevRSIStrategy(BaseStrategy):
    """Mean reversion using RSI oversold/overbought + Bollinger Bands."""
    
    def __init__(self, config: dict):
        super().__init__("meanrev_rsi", config)
        self.rsi_period = config.get("rsi_period", 14)
        self.rsi_th = config.get("rsi_th", 30)
        self.bb_period = config.get("bb_period", 20)
        self.bb_std = config.get("bb_std", 2.0)
        self.min_rr = config.get("min_rr", 1.5)
    
    def generate_signals(self, symbol: str, data: pd.DataFrame) -> List[Signal]:
        """Generate mean reversion signals."""
        if len(data) < max(self.rsi_period, self.bb_period):
            return []
        
        df = data.copy()
        
        # Calculate indicators
        df['rsi'] = ta.rsi(df['close'], length=self.rsi_period)
        bbands = ta.bbands(df['close'], length=self.bb_period, std=self.bb_std)
        df['bb_upper'] = bbands[f'BBU_{self.bb_period}_{self.bb_std}']
        df['bb_middle'] = bbands[f'BBM_{self.bb_period}_{self.bb_std}']
        df['bb_lower'] = bbands[f'BBL_{self.bb_period}_{self.bb_std}']
        
        last = df.iloc[-1]
        
        signals = []
        
        # Oversold - potential long
        if last['rsi'] < self.rsi_th and last['close'] < last['bb_lower']:
            stop_loss = last['bb_lower'] * 0.98
            take_profit = last['bb_middle']
            
            # Check risk/reward
            risk = abs(last['close'] - stop_loss)
            reward = abs(take_profit - last['close'])
            
            if risk > 0 and (reward / risk) >= self.min_rr:
                signals.append(Signal(
                    symbol=symbol,
                    side="buy",
                    entry_price=last['close'],
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    confidence=0.8,
                    reason=f"RSI oversold: {last['rsi']:.1f}, below BB lower",
                ))
        
        # Overbought - potential short
        elif last['rsi'] > (100 - self.rsi_th) and last['close'] > last['bb_upper']:
            stop_loss = last['bb_upper'] * 1.02
            take_profit = last['bb_middle']
            
            risk = abs(stop_loss - last['close'])
            reward = abs(last['close'] - take_profit)
            
            if risk > 0 and (reward / risk) >= self.min_rr:
                signals.append(Signal(
                    symbol=symbol,
                    side="sell",
                    entry_price=last['close'],
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    confidence=0.8,
                    reason=f"RSI overbought: {last['rsi']:.1f}, above BB upper",
                ))
        
        return signals

