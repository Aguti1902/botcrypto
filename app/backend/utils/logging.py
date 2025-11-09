"""Structured logging configuration with JSON output."""
import sys
import json
from pathlib import Path
from typing import Any
from loguru import logger
from config.settings import settings


def serialize_json(record: dict[str, Any]) -> str:
    """Serialize log record to JSON."""
    subset = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "logger": record["name"],
        "function": record["function"],
        "line": record["line"],
        "message": record["message"],
    }
    
    # Add extra fields
    if record.get("extra"):
        subset["extra"] = record["extra"]
    
    # Add exception if present
    if record["exception"]:
        subset["exception"] = {
            "type": record["exception"].type.__name__,
            "value": str(record["exception"].value"),
            "traceback": record["exception"].traceback,
        }
    
    return json.dumps(subset)


def setup_logging(log_level: str = "INFO", json_logs: bool = True) -> None:
    """Configure structured logging with Loguru.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Whether to output logs in JSON format
    """
    # Remove default handler
    logger.remove()
    
    # Console handler
    if json_logs and settings.environment == "production":
        logger.add(
            sys.stderr,
            level=log_level,
            serialize=True,
            format=serialize_json,
        )
    else:
        # Human-readable for development
        logger.add(
            sys.stderr,
            level=log_level,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
        )
    
    # File handler with rotation
    log_dir = Path("/logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "nexitrade_{time}.log",
        level=log_level,
        rotation="100 MB",
        retention="30 days",
        compression="gz",
        serialize=json_logs,
        format=serialize_json if json_logs else None,
    )
    
    logger.info(
        f"Logging initialized: level={log_level}, json={json_logs}, env={settings.environment}"
    )


def get_logger(name: str):
    """Get a logger with a specific name."""
    return logger.bind(logger=name)

