"""Order routing and execution."""
from typing import Optional
from loguru import logger

from exchanges.base import BaseExchange, OrderResult
from utils.retry import retry_with_backoff


class OrderRouter:
    """Route and execute orders on exchange."""
    
    def __init__(self, exchange: BaseExchange):
        """Initialize order router.
        
        Args:
            exchange: Exchange instance
        """
        self.exchange = exchange
    
    @retry_with_backoff(max_attempts=3)
    async def execute_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        client_order_id: Optional[str] = None,
    ) -> OrderResult:
        """Execute market order.
        
        Args:
            symbol: Trading symbol
            side: "buy" or "sell"
            quantity: Order quantity
            client_order_id: Optional client order ID
            
        Returns:
            OrderResult
        """
        logger.info(f"Executing market order: {symbol} {side} {quantity}")
        
        result = await self.exchange.create_market_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            client_order_id=client_order_id,
        )
        
        logger.info(f"Order executed: {result.order_id} - {result.status}")
        return result
    
    @retry_with_backoff(max_attempts=3)
    async def execute_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        post_only: bool = False,
        client_order_id: Optional[str] = None,
    ) -> OrderResult:
        """Execute limit order.
        
        Args:
            symbol: Trading symbol
            side: "buy" or "sell"
            quantity: Order quantity
            price: Limit price
            post_only: Maker-only flag
            client_order_id: Optional client order ID
            
        Returns:
            OrderResult
        """
        logger.info(f"Executing limit order: {symbol} {side} {quantity} @ {price}")
        
        result = await self.exchange.create_limit_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            post_only=post_only,
            client_order_id=client_order_id,
        )
        
        logger.info(f"Order placed: {result.order_id} - {result.status}")
        return result
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order.
        
        Args:
            order_id: Order ID
            symbol: Trading symbol
            
        Returns:
            True if cancelled successfully
        """
        logger.info(f"Cancelling order: {order_id}")
        
        success = await self.exchange.cancel_order(order_id, symbol)
        
        if success:
            logger.info(f"Order cancelled: {order_id}")
        else:
            logger.warning(f"Failed to cancel order: {order_id}")
        
        return success

