"""
Minimal logging utility.
Uses loguru if available, falls back to standard logging.
"""

from typing import Any

try:
    from loguru import logger as _loguru_logger  # type: ignore

    def get_logger(name: str) -> Any:
        return _loguru_logger.bind(module=name)

except Exception:  # pragma: no cover
    import logging

    _configured = False

    def _ensure_basic_config() -> None:
        global _configured
        if not _configured:
            logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
            _configured = True

    def get_logger(name: str) -> Any:
        _ensure_basic_config()
        return logging.getLogger(name)

"""
Logging configuration for the application.
"""
import logging
import sys
import json
from typing import Any, Dict, Optional
from pathlib import Path
from datetime import datetime

from utils.config import get_settings

settings = get_settings()

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_record.update(record.extra)
        
        return json.dumps(log_record)

def setup_logging():
    """Configure logging for the application."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # File handler for all logs
    file_handler = logging.FileHandler(
        log_dir / f"{settings.ENVIRONMENT}.log",
        encoding="utf-8"
    )
    file_handler.setFormatter(
        JSONFormatter() if settings.ENVIRONMENT == "production" 
        else logging.Formatter(settings.LOG_FORMAT)
    )
    
    # Console handler for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(settings.LOG_FORMAT))
    
    # Add handlers
    root_logger.addHandler(file_handler)
    
    if settings.DEBUG:
        root_logger.addHandler(console_handler)
    
    # Set log level for third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)
    
    return root_logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)

# Initialize logging when the module is imported
logger = get_logger(__name__)