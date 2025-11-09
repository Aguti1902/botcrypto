"""Script to run backtests."""
import asyncio
from loguru import logger

from config.settings import load_trading_config
from backtest.engine import BacktestEngine
from strategies.trend_atr import TrendATRStrategy
from strategies.meanrev_rsi import MeanRevRSIStrategy


async def main():
    """Run backtests for all strategies."""
    logger.info("Starting backtests...")
    
    # Load config
    config = load_trading_config()
    backtest_config = config.get_backtest_config()
    
    # Initialize engine
    engine = BacktestEngine(
        initial_cash=backtest_config.get('initial_cash', 10000),
        fees_bps=config.fees_bps,
        slippage_bps=config.slippage_bps,
    )
    
    # Load strategies
    strategies = []
    
    if config.is_strategy_enabled('trend_atr'):
        strategies.append(TrendATRStrategy(config.get_strategy_config('trend_atr')))
    
    if config.is_strategy_enabled('meanrev_rsi'):
        strategies.append(MeanRevRSIStrategy(config.get_strategy_config('meanrev_rsi')))
    
    # TODO: Load historical data
    data = {}
    
    # Run backtests
    for strategy in strategies:
        results = engine.run_backtest(
            strategy=strategy,
            data=data,
            start_date=backtest_config.get('start_date', '2023-01-01'),
            end_date=backtest_config.get('end_date', '2024-12-31'),
        )
        
        logger.info(f"Strategy: {strategy.name}")
        logger.info(f"Results: {results}")
    
    logger.info("Backtests completed")


if __name__ == "__main__":
    asyncio.run(main())

