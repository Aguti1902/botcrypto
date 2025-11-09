"""Stop loss and take profit management."""
from dataclasses import dataclass
from typing import Optional
from loguru import logger


@dataclass
class StopLevels:
    """Stop loss and take profit levels."""
    stop_loss: Optional[float]
    take_profit: Optional[float]
    trailing_stop_distance: Optional[float]
    highest_price: Optional[float]  # For trailing stop
    lowest_price: Optional[float]  # For trailing stop (shorts)


class StopLossManager:
    """Manages stop loss, take profit, and trailing stops."""
    
    def __init__(self):
        """Initialize stop loss manager."""
        self.stops: dict[str, StopLevels] = {}  # position_id -> stops
    
    def set_stops(
        self,
        position_id: str,
        entry_price: float,
        side: str,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        trailing_stop_distance: Optional[float] = None,
    ):
        """Set stop levels for a position.
        
        Args:
            position_id: Position identifier
            entry_price: Entry price
            side: "buy" or "sell"
            stop_loss: Stop loss price
            take_profit: Take profit price
            trailing_stop_distance: Trailing stop distance
        """
        self.stops[position_id] = StopLevels(
            stop_loss=stop_loss,
            take_profit=take_profit,
            trailing_stop_distance=trailing_stop_distance,
            highest_price=entry_price if side == "buy" else None,
            lowest_price=entry_price if side == "sell" else None,
        )
        
        logger.info(
            f"Stops set for {position_id}: SL={stop_loss}, TP={take_profit}, "
            f"trailing={trailing_stop_distance}"
        )
    
    def update_trailing_stop(
        self,
        position_id: str,
        current_price: float,
        side: str,
    ) -> Optional[float]:
        """Update trailing stop and return new stop loss if changed.
        
        Args:
            position_id: Position identifier
            current_price: Current market price
            side: "buy" or "sell"
            
        Returns:
            New stop loss price if updated, None otherwise
        """
        if position_id not in self.stops:
            return None
        
        stops = self.stops[position_id]
        
        if stops.trailing_stop_distance is None:
            return None
        
        if side == "buy":
            # Long position
            if stops.highest_price is None or current_price > stops.highest_price:
                stops.highest_price = current_price
                new_stop = current_price - stops.trailing_stop_distance
                
                # Only move stop up, never down
                if stops.stop_loss is None or new_stop > stops.stop_loss:
                    old_stop = stops.stop_loss
                    stops.stop_loss = new_stop
                    logger.info(
                        f"Trailing stop updated for {position_id}: "
                        f"{old_stop} -> {new_stop}"
                    )
                    return new_stop
        else:
            # Short position
            if stops.lowest_price is None or current_price < stops.lowest_price:
                stops.lowest_price = current_price
                new_stop = current_price + stops.trailing_stop_distance
                
                # Only move stop down, never up
                if stops.stop_loss is None or new_stop < stops.stop_loss:
                    old_stop = stops.stop_loss
                    stops.stop_loss = new_stop
                    logger.info(
                        f"Trailing stop updated for {position_id}: "
                        f"{old_stop} -> {new_stop}"
                    )
                    return new_stop
        
        return None
    
    def check_stops(
        self,
        position_id: str,
        current_price: float,
        side: str,
    ) -> tuple[bool, Optional[str]]:
        """Check if any stops are hit.
        
        Args:
            position_id: Position identifier
            current_price: Current market price
            side: "buy" or "sell"
            
        Returns:
            Tuple of (should_close, reason)
        """
        if position_id not in self.stops:
            return False, None
        
        stops = self.stops[position_id]
        
        if side == "buy":
            # Long position
            if stops.stop_loss and current_price <= stops.stop_loss:
                return True, f"Stop loss hit: {current_price} <= {stops.stop_loss}"
            
            if stops.take_profit and current_price >= stops.take_profit:
                return True, f"Take profit hit: {current_price} >= {stops.take_profit}"
        else:
            # Short position
            if stops.stop_loss and current_price >= stops.stop_loss:
                return True, f"Stop loss hit: {current_price} >= {stops.stop_loss}"
            
            if stops.take_profit and current_price <= stops.take_profit:
                return True, f"Take profit hit: {current_price} <= {stops.take_profit}"
        
        return False, None
    
    def remove_stops(self, position_id: str):
        """Remove stops for a closed position.
        
        Args:
            position_id: Position identifier
        """
        if position_id in self.stops:
            del self.stops[position_id]
            logger.debug(f"Stops removed for {position_id}")
    
    def get_stops(self, position_id: str) -> Optional[StopLevels]:
        """Get stop levels for a position.
        
        Args:
            position_id: Position identifier
            
        Returns:
            StopLevels if exists, None otherwise
        """
        return self.stops.get(position_id)

