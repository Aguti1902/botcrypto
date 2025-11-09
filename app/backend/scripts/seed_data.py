"""Script to download historical data."""
import asyncio
from datetime import datetime, timedelta
from loguru import logger

from config.settings import settings, load_trading_config
from exchanges.binance_ccxt import BinanceExchange
from utils.secrets import SecretManager


async def main():
    """Download historical OHLCV data."""
    logger.info("Starting data seed...")
    
    # Load config
    config = load_trading_config()
    symbols = config.symbols
    timeframe = config.timeframe
    
    # Initialize exchange
    api_key, secret = SecretManager.get_binance_credentials()
    exchange = BinanceExchange(api_key, secret, testnet=settings.binance_testnet)
    await exchange.initialize()
    
    # Download data for each symbol
    since = datetime.utcnow() - timedelta(days=365)
    
    for symbol in symbols:
        logger.info(f"Downloading {symbol} {timeframe} data...")
        
        try:
            ohlcv = await exchange.get_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                since=since,
                limit=1000,
            )
            
            logger.info(f"Downloaded {len(ohlcv)} candles for {symbol}")
            
            # TODO: Save to database or CSV
            
        except Exception as e:
            logger.error(f"Failed to download {symbol}: {e}")
    
    await exchange.close()
    logger.info("Data seed completed")


if __name__ == "__main__":
    asyncio.run(main())

