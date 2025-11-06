"""
Logging utilities for JusticeGraph.

Provides structured JSON logging for all ETL operations, with support
for different log levels, file rotation, and contextual information.
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import sys

# Project root and logs directory
PROJECT_ROOT = Path(__file__).parent.parent
LOGS_DIR = PROJECT_ROOT / 'logs'


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    Formats log records as JSON objects with timestamp, level, message,
    and additional contextual information.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception information if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add any extra fields passed to the logger
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)  # type: ignore[attr-defined]
        
        return json.dumps(log_data, default=str)


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    json_format: bool = True,
    console_output: bool = True
) -> logging.Logger:
    """
    Set up a logger with file and/or console handlers.
    
    Args:
        name: Name of the logger
        log_file: Path to the log file (relative to logs directory)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Whether to use JSON formatting
        console_output: Whether to output to console
    
    Returns:
        Configured logger instance
    
    Example:
        >>> logger = setup_logger('ingest', 'ingest.log', level=logging.DEBUG)
        >>> logger.info('Starting data ingestion', extra={'source': 'ecourts'})
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # File handler
    if log_file:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        file_path = LOGS_DIR / log_file
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Use simpler format for console
        if json_format:
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
        else:
            console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
    
    return logger


class ContextLogger:
    """
    Logger wrapper that adds contextual information to all log messages.
    
    Useful for adding consistent context (like scraper name, data source)
    to all logs from a specific operation.
    """
    
    def __init__(self, logger: logging.Logger, context: Dict[str, Any]):
        """
        Initialize the context logger.
        
        Args:
            logger: Base logger instance
            context: Dictionary of context information to add to all logs
        """
        self.logger = logger
        self.context = context
    
    def _log(self, level: int, msg: str, **kwargs):
        """Internal method to log with context."""
        extra = kwargs.get('extra', {})
        extra.update({'extra_fields': self.context})
        kwargs['extra'] = extra
        self.logger.log(level, msg, **kwargs)
    
    def debug(self, msg: str, **kwargs):
        """Log debug message with context."""
        self._log(logging.DEBUG, msg, **kwargs)
    
    def info(self, msg: str, **kwargs):
        """Log info message with context."""
        self._log(logging.INFO, msg, **kwargs)
    
    def warning(self, msg: str, **kwargs):
        """Log warning message with context."""
        self._log(logging.WARNING, msg, **kwargs)
    
    def error(self, msg: str, **kwargs):
        """Log error message with context."""
        self._log(logging.ERROR, msg, **kwargs)
    
    def critical(self, msg: str, **kwargs):
        """Log critical message with context."""
        self._log(logging.CRITICAL, msg, **kwargs)
    
    def exception(self, msg: str, **kwargs):
        """Log exception with context."""
        kwargs['exc_info'] = True
        self._log(logging.ERROR, msg, **kwargs)


def log_scraper_activity(
    logger: logging.Logger,
    scraper_name: str,
    url: str,
    status: str,
    record_count: int = 0,
    errors: Optional[list] = None,
    **kwargs
):
    """
    Log scraper activity with standardized format.
    
    Args:
        logger: Logger instance
        scraper_name: Name of the scraper
        url: URL being scraped
        status: Status of the scraping (success, failed, partial)
        record_count: Number of records extracted
        errors: List of errors encountered
        **kwargs: Additional fields to log
    
    Example:
        >>> logger = setup_logger('scraper')
        >>> log_scraper_activity(
        ...     logger,
        ...     'cause_list_ingest',
        ...     'https://ecourts.gov.in/causelists',
        ...     'success',
        ...     record_count=150
        ... )
    """
    log_data = {
        'scraper_name': scraper_name,
        'url': url,
        'status': status,
        'record_count': record_count,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if errors:
        log_data['errors'] = errors
    
    log_data.update(kwargs)
    
    if status == 'success':
        logger.info(f"Scraper {scraper_name} completed successfully", extra={'extra_fields': log_data})
    elif status == 'failed':
        logger.error(f"Scraper {scraper_name} failed", extra={'extra_fields': log_data})
    else:
        logger.warning(f"Scraper {scraper_name} completed with status: {status}", extra={'extra_fields': log_data})


def log_pipeline_stage(
    logger: logging.Logger,
    stage_name: str,
    status: str,
    input_count: int = 0,
    output_count: int = 0,
    duration_seconds: float = 0.0,
    **kwargs
):
    """
    Log pipeline stage execution with metrics.
    
    Args:
        logger: Logger instance
        stage_name: Name of the pipeline stage
        status: Status of the stage (started, completed, failed)
        input_count: Number of input records
        output_count: Number of output records
        duration_seconds: Execution duration in seconds
        **kwargs: Additional fields to log
    
    Example:
        >>> logger = setup_logger('pipeline')
        >>> log_pipeline_stage(
        ...     logger,
        ...     'parse_cause_list',
        ...     'completed',
        ...     input_count=1,
        ...     output_count=150,
        ...     duration_seconds=2.5
        ... )
    """
    log_data = {
        'stage_name': stage_name,
        'status': status,
        'input_count': input_count,
        'output_count': output_count,
        'duration_seconds': round(duration_seconds, 2),
        'timestamp': datetime.utcnow().isoformat()
    }
    
    log_data.update(kwargs)
    
    if status == 'completed':
        logger.info(f"Pipeline stage {stage_name} completed", extra={'extra_fields': log_data})
    elif status == 'failed':
        logger.error(f"Pipeline stage {stage_name} failed", extra={'extra_fields': log_data})
    elif status == 'started':
        logger.info(f"Pipeline stage {stage_name} started", extra={'extra_fields': log_data})


def log_validation_results(
    logger: logging.Logger,
    validation_name: str,
    passed: bool,
    total_records: int,
    failed_records: int = 0,
    errors: Optional[list] = None,
    **kwargs
):
    """
    Log data validation results.
    
    Args:
        logger: Logger instance
        validation_name: Name of the validation check
        passed: Whether the validation passed
        total_records: Total number of records validated
        failed_records: Number of records that failed validation
        errors: List of validation errors
        **kwargs: Additional fields to log
    
    Example:
        >>> logger = setup_logger('validation')
        >>> log_validation_results(
        ...     logger,
        ...     'null_check',
        ...     passed=False,
        ...     total_records=150,
        ...     failed_records=5,
        ...     errors=['case_123: missing case_number']
        ... )
    """
    log_data = {
        'validation_name': validation_name,
        'passed': passed,
        'total_records': total_records,
        'failed_records': failed_records,
        'pass_rate': round((total_records - failed_records) / total_records * 100, 2) if total_records > 0 else 0,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if errors:
        log_data['errors'] = errors[:10]  # Log first 10 errors
        log_data['total_errors'] = len(errors)
    
    log_data.update(kwargs)
    
    if passed:
        logger.info(f"Validation {validation_name} passed", extra={'extra_fields': log_data})
    else:
        logger.warning(f"Validation {validation_name} failed", extra={'extra_fields': log_data})


# Create default loggers for different modules
def get_logger(module_name: str) -> logging.Logger:
    """
    Get or create a logger for a specific module.
    
    Args:
        module_name: Name of the module (e.g., 'ingest', 'parse', 'normalize')
    
    Returns:
        Logger instance for the module
    
    Example:
        >>> logger = get_logger('ingest')
        >>> logger.info('Starting ingestion process')
    """
    log_file = f"{module_name}.log"
    return setup_logger(module_name, log_file, level=logging.INFO)
