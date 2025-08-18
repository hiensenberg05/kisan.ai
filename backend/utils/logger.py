"""
Logging configuration for the application.
Uses standard logging with JSON formatting in production and colored output in development.
"""
import logging
import sys
import json
import os
from typing import Any, Dict, Optional, Union
from pathlib import Path
from datetime import datetime

# Default values
DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
DEFAULT_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DEFAULT_ENV = os.getenv("ENVIRONMENT", "development").lower()
DEFAULT_DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Initialize module-level variables
_log_initialized = False
_log_level = DEFAULT_LOG_LEVEL
_log_format = DEFAULT_LOG_FORMAT
_environment = DEFAULT_ENV
_debug = DEFAULT_DEBUG

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging in production."""
    
    def format(self, record: logging.LogRecord) -> str:
        try:
            log_record = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": record.levelname,
                "name": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
                "process": record.process,
                "thread": record.thread,
                "threadName": record.threadName,
            }
            
            # Add exception info if present
            if record.exc_info:
                log_record["exception"] = self.formatException(record.exc_info)
            
            # Add extra fields if present
            if hasattr(record, "extra") and isinstance(record.extra, dict):
                log_record.update(record.extra)
            
            return json.dumps(log_record, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": "ERROR",
                "name": "logger",
                "message": f"Failed to format log record: {str(e)}",
                "original_message": record.getMessage() if hasattr(record, 'getMessage') else str(record)
            })

def setup_logging(settings: Any = None) -> None:
    """
    Configure logging for the application.
    
    Args:
        settings: Optional settings object with logging configuration.
                 Expected attributes: LOG_LEVEL, LOG_FORMAT, ENVIRONMENT, DEBUG
    """
    global _log_initialized, _log_level, _log_format, _environment, _debug
    
    if _log_initialized:
        return
    
    try:
        # Update config from settings if provided
        if settings is not None:
            _log_level = getattr(settings, "LOG_LEVEL", _log_level)
            _log_format = getattr(settings, "LOG_FORMAT", _log_format)
            _environment = getattr(settings, "ENVIRONMENT", _environment)
            _debug = getattr(settings, "DEBUG", _debug)
        
        # Ensure log level is valid
        try:
            logging.getLevelName(_log_level)
        except ValueError:
            _log_level = "INFO"
        
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(_log_level)
        
        # Clear existing handlers
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)
        
        # Create formatter based on environment
        if _environment.lower() == "production":
            formatter = JSONFormatter()
            console_formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            )
        else:
            try:
                from colorlog import ColoredFormatter
                formatter = ColoredFormatter(
                    "%(log_color)s%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                    reset=True,
                    log_colors={
                        'DEBUG': 'cyan',
                        'INFO': 'green',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'red,bg_white',
                    },
                    secondary_log_colors={},
                    style='%'
                )
                console_formatter = formatter
            except ImportError:
                formatter = logging.Formatter(_log_format)
                console_formatter = formatter
        
        # File handler
        file_handler = logging.FileHandler(
            log_dir / f"{_environment}.log",
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        root_logger.addHandler(file_handler)
        
        # Add console handler in debug mode or if not in production
        if _debug or _environment.lower() != "production":
            root_logger.addHandler(console_handler)
        
        # Configure third-party loggers
        for lib in ["urllib3", "google", "openai", "httpx", "asyncio"]:
            logging.getLogger(lib).setLevel(logging.WARNING)
        
        _log_initialized = True
        
        # Log successful initialization
        logger = get_logger(__name__)
        logger.info("Logging configured successfully")
        logger.debug("Debug logging enabled")
        
    except Exception as e:
        # Fallback to basic config if anything goes wrong
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        logging.getLogger(__name__).error(
            f"Failed to configure logging: {str(e)}", 
            exc_info=True
        )

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    if not _log_initialized:
        setup_logging()
    return logging.getLogger(name)

# Create module logger
logger = get_logger(__name__)

# Initialize logging when module is imported
if not _log_initialized:
    setup_logging()