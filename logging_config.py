"""Centralized logging configuration for the Universal Data Migration project."""

import logging
import logging.handlers
from pathlib import Path


def setup_logging(name: str = __name__, log_dir: str = "logs", level=logging.INFO):
    """Setup logging with both file and console handlers.

    Args:
        name: Logger name (usually __name__)
        log_dir: Directory to store log files
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    # Ensure logs directory exists
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True, parents=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    simple_formatter = logging.Formatter(
        fmt='%(levelname)s - %(message)s'
    )

    # File handler (detailed)
    log_file = log_path / f"{name.split('.')[-1]}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)

    # Console handler (simple, INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str):
    """Get or create a logger for the given name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
