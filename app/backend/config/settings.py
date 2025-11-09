"""Application settings and configuration."""
import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
import yaml
from loguru import logger


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # API Keys
    binance_api_key: str = Field(default="", alias="BINANCE_API_KEY")
    binance_secret: str = Field(default="", alias="BINANCE_SECRET")
    binance_testnet: bool = Field(default=True, alias="BINANCE_TESTNET")
    
    # EVM/DEX
    evm_private_key: str = Field(default="", alias="EVM_PRIVATE_KEY")
    rpc_url: str = Field(default="", alias="RPC_URL")
    chain_id: int = Field(default=1, alias="CHAIN_ID")
    
    # Database
    postgres_user: str = Field(default="nexi", alias="POSTGRES_USER")
    postgres_password: str = Field(default="nexi", alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="nexitrade", alias="POSTGRES_DB")
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    
    # Security
    admin_token: str = Field(default="", alias="ADMIN_TOKEN")
    jwt_secret: str = Field(default="", alias="JWT_SECRET")
    
    # Backend
    backend_host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    
    # Environment
    environment: str = Field(default="development", alias="ENVIRONMENT")
    
    @property
    def database_url(self) -> str:
        """Build database URL."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    @property
    def async_database_url(self) -> str:
        """Build async database URL."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class TradingConfig:
    """Trading configuration from YAML."""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = Path(__file__).parent / "system.yaml"
        
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        logger.info(f"Loaded trading config from {config_path}")
    
    @property
    def mode(self) -> str:
        """Trading mode: backtest, paper, or live."""
        return self.config.get("mode", "paper")
    
    @property
    def symbols(self) -> list[str]:
        """List of trading symbols."""
        return self.config.get("symbols", [])
    
    @property
    def timeframe(self) -> str:
        """Timeframe for OHLCV data."""
        return self.config.get("timeframe", "1m")
    
    @property
    def capital(self) -> float:
        """Initial capital."""
        return float(self.config.get("capital", 10000))
    
    @property
    def fees_bps(self) -> float:
        """Fees in basis points."""
        return float(self.config.get("fees_bps", 10))
    
    @property
    def slippage_bps(self) -> float:
        """Slippage in basis points."""
        return float(self.config.get("slippage_bps", 2))
    
    def get_risk_config(self) -> dict:
        """Get risk management configuration."""
        return self.config.get("risk", {})
    
    def get_portfolio_config(self) -> dict:
        """Get portfolio configuration."""
        return self.config.get("portfolio", {})
    
    def get_strategy_config(self, strategy_name: str) -> Optional[dict]:
        """Get configuration for a specific strategy."""
        strategies = self.config.get("strategies", {})
        return strategies.get(strategy_name)
    
    def get_ml_config(self) -> dict:
        """Get ML configuration."""
        return self.config.get("ml", {})
    
    def get_rl_config(self) -> dict:
        """Get RL configuration."""
        return self.config.get("rl", {})
    
    def get_backtest_config(self) -> dict:
        """Get backtest configuration."""
        return self.config.get("backtest", {})
    
    def get_exchange_config(self, exchange_name: str) -> Optional[dict]:
        """Get configuration for a specific exchange."""
        exchanges = self.config.get("exchanges", {})
        return exchanges.get(exchange_name)
    
    def is_strategy_enabled(self, strategy_name: str) -> bool:
        """Check if a strategy is enabled."""
        strategy_config = self.get_strategy_config(strategy_name)
        if strategy_config is None:
            return False
        return strategy_config.get("enabled", False)


def load_trading_config(config_path: Optional[str] = None) -> TradingConfig:
    """Load trading configuration."""
    return TradingConfig(config_path)


# Global settings instance
settings = Settings()

