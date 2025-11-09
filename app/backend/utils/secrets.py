"""Secret management utilities."""
from typing import Optional
from loguru import logger
from config.settings import settings


class SecretManager:
    """Manages secure access to API keys and secrets.
    
    This class ensures:
    - Secrets are never logged
    - Secrets are never exposed in error messages
    - Secrets are validated before use
    """
    
    @staticmethod
    def get_binance_credentials() -> tuple[str, str]:
        """Get Binance API credentials.
        
        Returns:
            Tuple of (api_key, secret)
            
        Raises:
            ValueError: If credentials are not configured
        """
        api_key = settings.binance_api_key
        secret = settings.binance_secret
        
        if not api_key or not secret:
            raise ValueError(
                "Binance credentials not configured. "
                "Set BINANCE_API_KEY and BINANCE_SECRET in .env"
            )
        
        logger.debug("Retrieved Binance credentials")
        return api_key, secret
    
    @staticmethod
    def get_evm_private_key() -> str:
        """Get EVM private key.
        
        Returns:
            Private key string
            
        Raises:
            ValueError: If private key is not configured
        """
        private_key = settings.evm_private_key
        
        if not private_key:
            raise ValueError(
                "EVM private key not configured. "
                "Set EVM_PRIVATE_KEY in .env"
            )
        
        # Ensure 0x prefix
        if not private_key.startswith("0x"):
            private_key = f"0x{private_key}"
        
        logger.debug("Retrieved EVM private key")
        return private_key
    
    @staticmethod
    def get_admin_token() -> str:
        """Get admin authentication token.
        
        Returns:
            Admin token string
            
        Raises:
            ValueError: If token is not configured
        """
        token = settings.admin_token
        
        if not token:
            raise ValueError(
                "Admin token not configured. "
                "Set ADMIN_TOKEN in .env"
            )
        
        if len(token) < 32:
            logger.warning(
                "Admin token is too short. Use at least 64 characters for production."
            )
        
        return token
    
    @staticmethod
    def mask_secret(secret: str, visible_chars: int = 4) -> str:
        """Mask a secret for logging.
        
        Args:
            secret: Secret to mask
            visible_chars: Number of characters to show at the end
            
        Returns:
            Masked secret string
        """
        if not secret:
            return "****"
        
        if len(secret) <= visible_chars:
            return "****"
        
        return f"****{secret[-visible_chars:]}"
    
    @staticmethod
    def validate_api_key_format(api_key: str) -> bool:
        """Validate API key format.
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if valid format
        """
        if not api_key:
            return False
        
        # Basic validation: alphanumeric, minimum length
        if len(api_key) < 16:
            return False
        
        return api_key.isalnum()

