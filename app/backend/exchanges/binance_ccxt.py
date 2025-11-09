"""Binance exchange integration using CCXT."""
import ccxt.async_support as ccxt
from typing import List, Optional
from datetime import datetime
from loguru import logger

from .base import BaseExchange, Balance, Ticker, OrderBook, OHLCV, OrderResult
from utils.retry import retry_with_backoff
from utils.time import from_timestamp, now_utc


class BinanceExchange(BaseExchange):
    """Binance exchange integration with rate limiting and retry logic."""
    
    def __init__(self, api_key: str = "", secret: str = "", testnet: bool = True):
        super().__init__(api_key, secret, testnet)
        self.exchange: Optional[ccxt.binance] = None
    
    async def initialize(self) -> None:
        """Initialize Binance exchange connection."""
        options = {
            'adjustForTimeDifference': True,
            'recvWindow': 10000,
        }
        
        if self.testnet:
            options['test'] = True
            logger.info("Initializing Binance TESTNET")
        else:
            logger.warning("Initializing Binance PRODUCTION")
        
        self.exchange = ccxt.binance({
            'apiKey': self.api_key,
            'secret': self.secret,
            'enableRateLimit': True,
            'rateLimit': 100,  # 100ms between requests
            'options': options,
        })
        
        # Load markets
        await self.exchange.load_markets()
        logger.info(f"Binance initialized: {len(self.exchange.markets)} markets")
    
    @retry_with_backoff(max_attempts=3, exceptions=(ccxt.NetworkError, ccxt.ExchangeNotAvailable))
    async def get_balance(self, currency: Optional[str] = None) -> List[Balance]:
        """Get account balance."""
        if not self.exchange:
            raise RuntimeError("Exchange not initialized")
        
        balance_data = await self.exchange.fetch_balance()
        balances = []
        
        for curr, amounts in balance_data['total'].items():
            if amounts > 0 or currency == curr:
                balances.append(Balance(
                    currency=curr,
                    free=balance_data['free'].get(curr, 0.0),
                    used=balance_data['used'].get(curr, 0.0),
                    total=amounts,
                ))
        
        if currency:
            balances = [b for b in balances if b.currency == currency]
        
        return balances
    
    @retry_with_backoff(max_attempts=3)
    async def get_ticker(self, symbol: str) -> Ticker:
        """Get ticker for symbol."""
        if not self.exchange:
            raise RuntimeError("Exchange not initialized")
        
        ticker_data = await self.exchange.fetch_ticker(symbol)
        
        return Ticker(
            symbol=symbol,
            bid=ticker_data['bid'],
            ask=ticker_data['ask'],
            last=ticker_data['last'],
            volume=ticker_data['baseVolume'],
            timestamp=from_timestamp(ticker_data['timestamp']) if ticker_data['timestamp'] else now_utc(),
        )
    
    @retry_with_backoff(max_attempts=3)
    async def get_order_book(self, symbol: str, depth: int = 20) -> OrderBook:
        """Get order book."""
        if not self.exchange:
            raise RuntimeError("Exchange not initialized")
        
        ob = await self.exchange.fetch_order_book(symbol, limit=depth)
        
        return OrderBook(
            bids=[(price, size) for price, size in ob['bids']],
            asks=[(price, size) for price, size in ob['asks']],
            timestamp=from_timestamp(ob['timestamp']) if ob['timestamp'] else now_utc(),
        )
    
    @retry_with_backoff(max_attempts=3)
    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1m",
        since: Optional[datetime] = None,
        limit: int = 500,
    ) -> List[OHLCV]:
        """Get OHLCV candles."""
        if not self.exchange:
            raise RuntimeError("Exchange not initialized")
        
        since_ms = int(since.timestamp() * 1000) if since else None
        
        candles = await self.exchange.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            since=since_ms,
            limit=limit,
        )
        
        return [
            OHLCV(
                timestamp=from_timestamp(c[0]),
                open=c[1],
                high=c[2],
                low=c[3],
                close=c[4],
                volume=c[5],
            )
            for c in candles
        ]
    
    @retry_with_backoff(max_attempts=3)
    async def create_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        client_order_id: Optional[str] = None,
    ) -> OrderResult:
        """Create market order."""
        if not self.exchange:
            raise RuntimeError("Exchange not initialized")
        
        params = {}
        if client_order_id:
            params['newClientOrderId'] = client_order_id
        
        order = await self.exchange.create_order(
            symbol=symbol,
            type='market',
            side=side,
            amount=quantity,
            params=params,
        )
        
        return self._parse_order(order)
    
    @retry_with_backoff(max_attempts=3)
    async def create_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        post_only: bool = False,
        client_order_id: Optional[str] = None,
    ) -> OrderResult:
        """Create limit order."""
        if not self.exchange:
            raise RuntimeError("Exchange not initialized")
        
        params = {}
        if client_order_id:
            params['newClientOrderId'] = client_order_id
        if post_only:
            params['timeInForce'] = 'GTX'  # Good-Til-Crossing (post-only)
        
        order = await self.exchange.create_order(
            symbol=symbol,
            type='limit',
            side=side,
            amount=quantity,
            price=price,
            params=params,
        )
        
        return self._parse_order(order)
    
    @retry_with_backoff(max_attempts=3)
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel order."""
        if not self.exchange:
            raise RuntimeError("Exchange not initialized")
        
        try:
            await self.exchange.cancel_order(order_id, symbol)
            return True
        except ccxt.OrderNotFound:
            logger.warning(f"Order {order_id} not found")
            return False
    
    @retry_with_backoff(max_attempts=3)
    async def get_order(self, order_id: str, symbol: str) -> OrderResult:
        """Get order status."""
        if not self.exchange:
            raise RuntimeError("Exchange not initialized")
        
        order = await self.exchange.fetch_order(order_id, symbol)
        return self._parse_order(order)
    
    @retry_with_backoff(max_attempts=3)
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[OrderResult]:
        """Get open orders."""
        if not self.exchange:
            raise RuntimeError("Exchange not initialized")
        
        orders = await self.exchange.fetch_open_orders(symbol)
        return [self._parse_order(order) for order in orders]
    
    async def close(self) -> None:
        """Close exchange connection."""
        if self.exchange:
            await self.exchange.close()
            logger.info("Binance connection closed")
    
    def _parse_order(self, order: dict) -> OrderResult:
        """Parse CCXT order to OrderResult."""
        return OrderResult(
            order_id=order['id'],
            client_order_id=order.get('clientOrderId'),
            symbol=order['symbol'],
            side=order['side'],
            order_type=order['type'],
            status=order['status'],
            quantity=order['amount'],
            filled_quantity=order.get('filled', 0.0),
            price=order.get('price'),
            average_fill_price=order.get('average'),
            timestamp=from_timestamp(order['timestamp']) if order['timestamp'] else now_utc(),
            metadata=order.get('info', {}),
        )

