"""EVM DEX integration (Uniswap v3) using web3.py."""
from typing import List, Optional
from datetime import datetime
from web3 import Web3
from loguru import logger

from .base import BaseExchange, Balance, Ticker, OrderBook, OHLCV, OrderResult
from utils.time import now_utc


# Uniswap V3 Router address (Ethereum mainnet)
UNISWAP_V3_ROUTER = "0xE592427A0AEce92De3Edee1F18E0157C05861564"

# Uniswap V3 Router ABI (simplified for swaps)
ROUTER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "tokenIn", "type": "address"},
                    {"internalType": "address", "name": "tokenOut", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "address", "name": "recipient", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountOutMinimum", "type": "uint256"},
                    {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"},
                ],
                "internalType": "struct ISwapRouter.ExactInputSingleParams",
                "name": "params",
                "type": "tuple",
            }
        ],
        "name": "exactInputSingle",
        "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function",
    }
]

# ERC20 ABI (simplified)
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
]


class UniswapExchange(BaseExchange):
    """Uniswap V3 DEX integration for EVM chains.
    
    Note: This is a simplified implementation. Production use would require:
    - Price oracle integration (Chainlink, Uniswap TWAP)
    - Gas estimation and management
    - MEV protection
    - Proper slippage handling
    - Event monitoring for fills
    """
    
    def __init__(
        self,
        private_key: str,
        rpc_url: str,
        chain_id: int = 1,
        router_address: str = UNISWAP_V3_ROUTER,
    ):
        super().__init__()
        self.private_key = private_key
        self.rpc_url = rpc_url
        self.chain_id = chain_id
        self.router_address = router_address
        self.w3: Optional[Web3] = None
        self.account = None
    
    async def initialize(self) -> None:
        """Initialize Web3 connection."""
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to RPC: {self.rpc_url}")
        
        # Setup account
        self.account = self.w3.eth.account.from_key(self.private_key)
        
        logger.info(
            f"Uniswap initialized: chain_id={self.chain_id}, "
            f"address={self.account.address}"
        )
    
    async def get_balance(self, currency: Optional[str] = None) -> List[Balance]:
        """Get token balances.
        
        Note: For production, would query multiple tokens and handle ERC20s properly.
        """
        if not self.w3 or not self.account:
            raise RuntimeError("Exchange not initialized")
        
        balances = []
        
        # Get ETH balance
        eth_balance_wei = self.w3.eth.get_balance(self.account.address)
        eth_balance = self.w3.from_wei(eth_balance_wei, 'ether')
        
        balances.append(Balance(
            currency="ETH",
            free=float(eth_balance),
            used=0.0,
            total=float(eth_balance),
        ))
        
        # TODO: Query ERC20 token balances
        
        if currency:
            balances = [b for b in balances if b.currency == currency]
        
        return balances
    
    async def get_ticker(self, symbol: str) -> Ticker:
        """Get ticker - requires price oracle integration."""
        raise NotImplementedError(
            "get_ticker requires price oracle integration (Chainlink, Uniswap TWAP)"
        )
    
    async def get_order_book(self, symbol: str, depth: int = 20) -> OrderBook:
        """DEX doesn't have traditional order book - uses AMM."""
        raise NotImplementedError("DEX uses AMM, no traditional order book")
    
    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1m",
        since: Optional[datetime] = None,
        limit: int = 500,
    ) -> List[OHLCV]:
        """Get OHLCV - requires indexer or subgraph."""
        raise NotImplementedError(
            "get_ohlcv requires The Graph subgraph or similar indexer"
        )
    
    async def create_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        client_order_id: Optional[str] = None,
    ) -> OrderResult:
        """Create market swap on Uniswap.
        
        Args:
            symbol: Format "TOKEN0/TOKEN1" (e.g., "WETH/USDC")
            side: "buy" or "sell"
            quantity: Amount in base currency
            client_order_id: Not used in DEX
            
        Returns:
            OrderResult with transaction details
        """
        if not self.w3 or not self.account:
            raise RuntimeError("Exchange not initialized")
        
        # Parse symbol
        token_in, token_out = self._parse_symbol(symbol, side)
        
        # Build swap parameters
        deadline = int((now_utc().timestamp() + 300))  # 5 min deadline
        amount_in = self.w3.to_wei(quantity, 'ether')  # Simplified
        amount_out_min = 0  # TODO: Calculate from slippage tolerance
        
        router_contract = self.w3.eth.contract(
            address=self.router_address,
            abi=ROUTER_ABI,
        )
        
        swap_params = {
            'tokenIn': token_in,
            'tokenOut': token_out,
            'fee': 3000,  # 0.3% pool
            'recipient': self.account.address,
            'deadline': deadline,
            'amountIn': amount_in,
            'amountOutMinimum': amount_out_min,
            'sqrtPriceLimitX96': 0,
        }
        
        # Build transaction
        txn = router_contract.functions.exactInputSingle(swap_params).build_transaction({
            'from': self.account.address,
            'gas': 300000,  # Estimate
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'chainId': self.chain_id,
        })
        
        # Sign and send
        signed_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        logger.info(f"Swap submitted: tx_hash={tx_hash.hex()}")
        
        # Wait for receipt (simplified - production should handle pending state)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        success = receipt['status'] == 1
        
        return OrderResult(
            order_id=tx_hash.hex(),
            client_order_id=None,
            symbol=symbol,
            side=side,
            order_type="market",
            status="filled" if success else "rejected",
            quantity=quantity,
            filled_quantity=quantity if success else 0.0,
            price=None,
            average_fill_price=None,  # TODO: Parse from logs
            timestamp=now_utc(),
            metadata={
                'tx_hash': tx_hash.hex(),
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
            },
        )
    
    async def create_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        post_only: bool = False,
        client_order_id: Optional[str] = None,
    ) -> OrderResult:
        """DEX doesn't support traditional limit orders without external keeper."""
        raise NotImplementedError(
            "Limit orders on DEX require external keeper system (e.g., Gelato)"
        )
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cannot cancel on-chain transactions once submitted."""
        return False
    
    async def get_order(self, order_id: str, symbol: str) -> OrderResult:
        """Get transaction status."""
        if not self.w3:
            raise RuntimeError("Exchange not initialized")
        
        try:
            receipt = self.w3.eth.get_transaction_receipt(order_id)
            success = receipt['status'] == 1
            
            return OrderResult(
                order_id=order_id,
                client_order_id=None,
                symbol=symbol,
                side="unknown",
                order_type="market",
                status="filled" if success else "rejected",
                quantity=0.0,
                filled_quantity=0.0,
                price=None,
                average_fill_price=None,
                timestamp=now_utc(),
                metadata=dict(receipt),
            )
        except Exception as e:
            logger.error(f"Failed to get transaction: {e}")
            raise
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[OrderResult]:
        """No pending orders in DEX (transactions are atomic)."""
        return []
    
    async def close(self) -> None:
        """Close connection."""
        logger.info("Uniswap connection closed")
    
    def _parse_symbol(self, symbol: str, side: str) -> tuple[str, str]:
        """Parse symbol and side to token addresses.
        
        Note: This is simplified. Production needs proper token registry.
        """
        # Example: "WETH/USDC"
        tokens = symbol.split("/")
        if len(tokens) != 2:
            raise ValueError(f"Invalid symbol format: {symbol}")
        
        # TODO: Map token symbols to addresses
        # This is a placeholder
        token_map = {
            "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        }
        
        base, quote = tokens
        
        if side == "buy":
            # Buy base with quote
            return token_map.get(quote, quote), token_map.get(base, base)
        else:
            # Sell base for quote
            return token_map.get(base, base), token_map.get(quote, quote)

