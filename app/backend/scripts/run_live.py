"""Script to run LIVE trading - requires explicit confirmation."""
import asyncio
import sys
from loguru import logger

from config.settings import load_trading_config
from utils.logging import setup_logging


async def main():
    """Run LIVE trading."""
    setup_logging(log_level="INFO")
    
    logger.critical("⚠️  LIVE TRADING MODE ⚠️")
    logger.critical("This will execute REAL orders with REAL money!")
    
    # Check command line flag
    if "--i-know-what-im-doing" not in sys.argv:
        logger.error("Missing safety flag. Use: --i-know-what-im-doing")
        logger.error("Read the documentation before using live mode.")
        return
    
    config = load_trading_config()
    
    if config.mode != "live":
        logger.error(f"Config mode is '{config.mode}', expected 'live'")
        return
    
    logger.warning("Initializing LIVE trading engine...")
    
    # TODO: Initialize trading engine in live mode
    
    logger.critical("LIVE trading started. Monitor carefully!")
    
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        logger.warning("Stopping LIVE trading...")


if __name__ == "__main__":
    asyncio.run(main())

