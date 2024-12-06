from loguru import logger
import sys

# Remove any existing handlers
logger.remove()

# Add a handler to stdout with a custom format
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True,
)

# Add a file handler for persistent logging
logger.add(
    "logs/botify.log",
    rotation="10 MB",  # Rotate file when it reaches 10MB
    retention="1 week",  # Keep logs for 1 week
    compression="zip",  # Compress rotated logs
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
)

# Set minimum logging level
logger.level("INFO")

# Export logger instance
__all__ = ["logger"]
