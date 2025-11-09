"""API routers module."""
from .status import router as status_router
from .orders import router as orders_router
from .strategies import router as strategies_router
from .portfolio import router as portfolio_router
from .config import router as config_router

__all__ = [
    "status_router",
    "orders_router",
    "strategies_router",
    "portfolio_router",
    "config_router",
]

