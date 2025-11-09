"""OHLCV data feed."""
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger

from exchanges.base import BaseExchange, OHLCV
from utils.time import now_utc


class OHLCVFeed:
    """OHLCV data feed manager."""
    
    def __init__(
        self,
        exchange: BaseExchange,
        symbols: List[str],
        timeframe: str = "1m",
        lookback_bars: int = 500,
    ):
        """Initialize OHLCV feed.
        
        Args:
            exchange: Exchange instance
            symbols: List of symbols to track
            timeframe: Timeframe (1m, 5m, 1h, etc.)
            lookback_bars: Number of bars to keep in memory
        """
        self.exchange = exchange
        self.symbols = symbols
        self.timeframe = timeframe
        self.lookback_bars = lookback_bars
        
        # Storage: symbol -> DataFrame
        self.data: Dict[str, pd.DataFrame] = {}
    
    async def initialize(self):
        """Initialize data feed by downloading initial history."""
        logger.info(f"Initializing OHLCV feed for {len(self.symbols)} symbols")
        
        for symbol in self.symbols:
            await self.update_symbol(symbol, initial=True)
        
        logger.info("OHLCV feed initialized")
    
    async def update_symbol(self, symbol: str, initial: bool = False):
        """Update OHLCV data for a symbol.
        
        Args:
            symbol: Trading symbol
            initial: Whether this is initial download
        """
        try:
            # Determine since time
            if initial or symbol not in self.data or self.data[symbol].empty:
                # Initial download or no data yet
                since = now_utc() - timedelta(days=7)  # Last 7 days
                limit = self.lookback_bars
            else:
                # Update: get latest bar
                last_timestamp = self.data[symbol].index[-1]
                since = last_timestamp
                limit = 100
            
            # Fetch OHLCV
            ohlcv_list = await self.exchange.get_ohlcv(
                symbol=symbol,
                timeframe=self.timeframe,
                since=since,
                limit=limit,
            )
            
            if not ohlcv_list:
                return
            
            # Convert to DataFrame
            df = pd.DataFrame([
                {
                    'timestamp': bar.timestamp,
                    'open': bar.open,
                    'high': bar.high,
                    'low': bar.low,
                    'close': bar.close,
                    'volume': bar.volume,
                }
                for bar in ohlcv_list
            ])
            
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)
            
            # Merge with existing data
            if symbol in self.data and not self.data[symbol].empty:
                self.data[symbol] = pd.concat([self.data[symbol], df])
                self.data[symbol] = self.data[symbol][~self.data[symbol].index.duplicated(keep='last')]
                self.data[symbol].sort_index(inplace=True)
                
                # Trim to lookback
                if len(self.data[symbol]) > self.lookback_bars:
                    self.data[symbol] = self.data[symbol].iloc[-self.lookback_bars:]
            else:
                self.data[symbol] = df
            
            logger.debug(f"Updated {symbol}: {len(df)} new bars, {len(self.data[symbol])} total")
            
        except Exception as e:
            logger.error(f"Failed to update {symbol}: {e}")
    
    async def update_all(self):
        """Update all symbols."""
        for symbol in self.symbols:
            await self.update_symbol(symbol)
    
    def get_data(self, symbol: str, bars: Optional[int] = None) -> pd.DataFrame:
        """Get OHLCV data for a symbol.
        
        Args:
            symbol: Trading symbol
            bars: Number of latest bars to return (None = all)
            
        Returns:
            DataFrame with OHLCV data
        """
        if symbol not in self.data:
            return pd.DataFrame()
        
        df = self.data[symbol]
        
        if bars is not None and bars > 0:
            df = df.iloc[-bars:]
        
        return df.copy()
    
    def get_latest_bar(self, symbol: str) -> Optional[Dict]:
        """Get latest bar for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Latest bar as dictionary
        """
        if symbol not in self.data or self.data[symbol].empty:
            return None
        
        latest = self.data[symbol].iloc[-1]
        
        return {
            'timestamp': latest.name,
            'open': latest['open'],
            'high': latest['high'],
            'low': latest['low'],
            'close': latest['close'],
            'volume': latest['volume'],
        }
    
    def get_latest_close(self, symbol: str) -> Optional[float]:
        """Get latest close price.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Latest close price
        """
        bar = self.get_latest_bar(symbol)
        return bar['close'] if bar else None

