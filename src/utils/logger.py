"""
Logging utilities for the Email Scanner system.
Provides centralized logging configuration and utilities.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

from ..config.config_manager import get_config


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for console logging."""
    
    # Color codes for different log levels
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to the log level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logger(
    name: str = "email_scanner",
    log_file: Optional[str] = None,
    level: str = "INFO",
    max_size: str = "10MB",
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up a logger with both console and file handlers.
    
    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level
        max_size: Maximum size for log rotation
        backup_count: Number of backup files to keep
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create formatters
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert max_size to bytes
        size_map = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
        size_str = max_size.upper().replace(' ', '')
        for unit, multiplier in size_map.items():
            if size_str.endswith(unit):
                max_bytes = int(size_str[:-len(unit)]) * multiplier
                break
        else:
            max_bytes = 10 * 1024**2  # Default to 10MB
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "email_scanner") -> logging.Logger:
    """
    Get a logger instance with configuration from config file.
    
    Args:
        name: Logger name
    
    Returns:
        Configured logger instance
    """
    try:
        config = get_config()
        return setup_logger(
            name=name,
            log_file=config.logging.file,
            level=config.logging.level,
            max_size=config.logging.max_size,
            backup_count=config.logging.backup_count
        )
    except Exception as e:
        # Fallback to basic logger if config fails
        print(f"Warning: Could not load logging config: {e}")
        return setup_logger(name=name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        return self._logger


def log_function_call(func):
    """Decorator to log function calls with parameters and return values."""
    def wrapper(*args, **kwargs):
        logger = get_logger("function_calls")
        
        # Log function call
        func_name = func.__name__
        logger.debug(f"Calling {func_name} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func_name} returned: {result}")
            return result
        except Exception as e:
            logger.error(f"{func_name} raised exception: {e}")
            raise
    
    return wrapper


def log_execution_time(func):
    """Decorator to log function execution time."""
    def wrapper(*args, **kwargs):
        logger = get_logger("performance")
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"{func.__name__} failed after {execution_time:.2f} seconds: {e}")
            raise
    
    return wrapper


# Global logger instance
logger = get_logger()


def log_email_scan_start(email_count: int):
    """Log the start of an email scanning session."""
    logger.info(f"Starting email scan for {email_count} emails")


def log_email_scan_complete(processed_count: int, categorized_count: int, topics_generated: int):
    """Log the completion of an email scanning session."""
    logger.info(
        f"Email scan completed: {processed_count} processed, "
        f"{categorized_count} categorized, {topics_generated} topics generated"
    )


def log_email_categorization(email_id: str, category: str, confidence: float):
    """Log email categorization results."""
    logger.debug(f"Email {email_id} categorized as {category} (confidence: {confidence:.2f})")


def log_topic_generation(content_length: int, topics_generated: int):
    """Log topic generation results."""
    logger.info(f"Generated {topics_generated} topics from {content_length} characters of content")


def log_error(error: Exception, context: str = ""):
    """Log an error with context."""
    logger.error(f"Error in {context}: {error}", exc_info=True)


def log_warning(message: str, context: str = ""):
    """Log a warning with context."""
    logger.warning(f"Warning in {context}: {message}")


def log_info(message: str, context: str = ""):
    """Log an info message with context."""
    logger.info(f"Info in {context}: {message}")


def log_debug(message: str, context: str = ""):
    """Log a debug message with context."""
    logger.debug(f"Debug in {context}: {message}") 