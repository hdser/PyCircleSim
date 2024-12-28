# src/framework/logging/logger.py

import logging
import colorama
from typing import Optional

# Initialize colorama for Windows compatibility
colorama.init(autoreset=True)

# Color codes for different log levels
COLORS = {
    'DEBUG': '\033[36m',      # Cyan
    'INFO': '\033[32m',       # Green
    'WARNING': '\033[33m',    # Yellow
    'ERROR': '\033[31m',      # Red
    'CRITICAL': '\033[31;1m'  # Bold Red
}

class ColorFormatter(logging.Formatter):
    """Add colors to log level names and simplify logger names"""
    def format(self, record):
        # Simplify the logger name
        if record.name.startswith('src.framework.'):
            record.name = record.name.split('.')[-1]
        
        # Add color to the level name
        levelname = record.levelname
        if levelname in COLORS:
            record.levelname = f"{COLORS[levelname]}{levelname}\033[0m"
        
        return super().format(record)

def setup_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """Set up a logger with consistent formatting"""
    # Remove existing handlers from the root logger
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers[:]:
            root.removeHandler(handler)
            
    logger = logging.getLogger(name)
    
    # Remove any existing handlers
    if logger.handlers:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
    
    logger.setLevel(logging.INFO)
    
    # Create formatters
    formatter = ColorFormatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if log file specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent log propagation to avoid duplicate logs
    logger.propagate = False

    return logger

# Create a function to get a logger instance
def get_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """Get a logger with consistent formatting"""
    return setup_logger(name, log_file)