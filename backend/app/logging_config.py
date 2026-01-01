"""
Structured logging configuration for the backend.
Provides consistent, parseable log output for production monitoring.
"""

import logging
import sys
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import os


class JSONFormatter(logging.Formatter):
    """
    Formats log records as JSON for easy parsing by log aggregators.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra"):
            log_data["extra"] = record.extra
        
        # Add request context if available
        for attr in ["request_id", "user_id", "client_ip", "path", "method"]:
            if hasattr(record, attr):
                log_data[attr] = getattr(record, attr)
        
        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """
    Colored console output for development.
    """
    
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    json_output: bool = False,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_output: Use JSON formatting (recommended for production)
        log_file: Optional file path for log output
    
    Returns:
        Configured root logger
    """
    # Determine settings from environment
    env = os.getenv("ENVIRONMENT", "development")
    if env == "production":
        json_output = True
        level = os.getenv("LOG_LEVEL", "INFO")
    
    # Create root logger
    logger = logging.getLogger("astronumeric")
    logger.setLevel(getattr(logging, level.upper()))
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    if json_output:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(ColoredFormatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
    
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    return logger


# Pre-configured logger instance
logger = setup_logging()


# Convenience functions
def log_request(request_id: str, method: str, path: str, client_ip: str):
    """Log an incoming request."""
    logger.info(
        f"Request: {method} {path}",
        extra={"request_id": request_id, "client_ip": client_ip, "path": path, "method": method}
    )


def log_response(request_id: str, status_code: int, duration_ms: float):
    """Log a completed response."""
    level = logging.INFO if status_code < 400 else logging.WARNING if status_code < 500 else logging.ERROR
    logger.log(
        level,
        f"Response: {status_code} ({duration_ms:.2f}ms)",
        extra={"request_id": request_id, "status_code": status_code, "duration_ms": duration_ms}
    )


def log_error(message: str, error: Exception = None, **context):
    """Log an error with context."""
    logger.error(message, exc_info=error, extra=context)


def log_chart_calculation(profile_name: str, chart_type: str, provider: str, duration_ms: float):
    """Log chart calculation metrics."""
    logger.info(
        f"Chart calculated: {chart_type} for {profile_name}",
        extra={"chart_type": chart_type, "provider": provider, "duration_ms": duration_ms}
    )
