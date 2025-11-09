"""Base exchange interface."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass


@dataclass
class OrderBook:
    """Order book data."""
    bids: List[Tuple[float, float]]  # [(price, size), ...]
    asks: List[Tuple[float, float]]
    timestamp: datetime


@dataclass
class Ticker:
    """Ticker data."""
    symbol: str
    bid: float
    ask: float
    last: float
    volume: float
    timestamp: datetime


@dataclass
class OHLCV:
    """OHLCV candle."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class Balance:
    """Account balance."""
    currency: str
    free: float
    used: float
    total: float


@dataclass
class OrderResult:
    """Order execution result."""
    order_id: str
    client_order_id: Optional[str]
    symbol: str
    side: str  # buy, sell
    order_type: str  # market, limit, etc.
    status: str
    quantity: float
    filled_quantity: float
    price: Optional[float]
    average_fill_price: Optional[float]
    timestamp: datetime
    metadata: Dict


class BaseExchange(ABC):
    """Base class for exchange integrations."""
    
    def __init__(self, api_key: str = "", secret: str = "", testnet: bool = True):
        """Initialize exchange.
        
        Args:
            api_key: API key
            secret: API secret
            testnet: Whether to use testnet
        """
        self.api_key = api_key
        self.secret = secret
        self.testnet = testnet
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize exchange connection."""
        pass
    
    @abstractmethod
    async def get_balance(self, currency: Optional[str] = None) -> List[Balance]:
        """Get account balance.
        
        Args:
            currency: Optional currency filter
            
        Returns:
            List of balances
        """
        pass
    
    @abstractmethod
    async def get_ticker(self, symbol: str) -> Ticker:
        """Get ticker for symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Ticker data
        """
        pass
    
    @abstractmethod
    async def get_order_book(self, symbol: str, depth: int = 20) -> OrderBook:
        """Get order book.
        
        Args:
            symbol: Trading symbol
            depth: Depth of order book
            
        Returns:
            Order book data
        """
        pass
    
    @abstractmethod
    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1m",
        since: Optional[datetime] = None,
        limit: int = 500,
    ) -> List[OHLCV]:
        """Get OHLCV candles.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe (1m, 5m, 1h, etc.)
            since: Start time
            limit: Number of candles
            
        Returns:
            List of OHLCV candles
        """
        pass
    
    @abstractmethod
    async def create_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        client_order_id: Optional[str] = None,
    ) -> OrderResult:
        """Create market order.
        
        Args:
            symbol: Trading symbol
            side: buy or sell
            quantity: Order quantity
            client_order_id: Optional client order ID
            
        Returns:
            Order result
        """
        pass
    
    @abstractmethod
    async def create_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        post_only: bool = False,
        client_order_id: Optional[str] = None,
    ) -> OrderResult:
        """Create limit order.
        
        Args:
            symbol: Trading symbol
            side: buy or sell
            quantity: Order quantity
            price: Limit price
            post_only: Post-only flag (maker-only)
            client_order_id: Optional client order ID
            
        Returns:
            Order result
        """
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel order.
        
        Args:
            order_id: Order ID
            symbol: Trading symbol
            
        Returns:
            True if cancelled successfully
        """
        pass
    
    @abstractmethod
    async def get_order(self, order_id: str, symbol: str) -> OrderResult:
        """Get order status.
        
        Args:
            order_id: Order ID
            symbol: Trading symbol
            
        Returns:
            Order result
        """
        pass
    
    @abstractmethod
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[OrderResult]:
        """Get open orders.
        
        Args:
            symbol: Optional symbol filter
            
        Returns:
            List of open orders
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close exchange connection."""
        pass

