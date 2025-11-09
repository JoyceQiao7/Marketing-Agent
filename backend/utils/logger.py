"""
Centralized logging configuration using loguru.
"""
import sys
from pathlib import Path
from loguru import logger
from backend.config.settings import settings


def setup_logger():
    """Configure logger with appropriate settings."""
    # Remove default handler
    logger.remove()
    
    # Add custom handler with formatting
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    # Add file handler for persistent logs
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    logger.add(
        str(log_dir / "mulan_agent_{time:YYYY-MM-DD}.log"),
        rotation="500 MB",
        retention="10 days",
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    return logger


# Initialize logger
log = setup_logger()

