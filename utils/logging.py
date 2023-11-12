from loguru import logger

logger.add(
    "logs/debug.log",
    level="DEBUG",
    format="{time} | {level} | {module}:{function}:{line} | {message}",
    rotation="30 KB",
    compression="zip",
)
