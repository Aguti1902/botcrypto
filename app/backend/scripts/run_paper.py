"""Script to run paper trading."""
import asyncio
from loguru import logger

from config.settings import load_trading_config
from utils.logging import setup_logging


async def main():
    """Run paper trading."""
    setup_logging(log_level="INFO")
    logger.info("Starting paper trading...")
    
    config = load_trading_config()
    
    if config.mode != "paper":
        logger.error(f"Config mode is '{config.mode}', expected 'paper'")
        return
    
    # TODO: Initialize trading engine in paper mode
    logger.info("Paper trading engine initialized")
    
    logger.info("Paper trading started. Press Ctrl+C to stop.")
    
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        logger.info("Stopping paper trading...")


if __name__ == "__main__":
    asyncio.run(main())

