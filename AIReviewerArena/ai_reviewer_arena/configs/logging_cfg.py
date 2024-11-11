import logging
import logging.config
import os
from pathlib import Path

from ai_reviewer_arena.configs.app_cfg import ARENA_LOGGING_LEVEL


def setup_logging(
    log_file: str = "ai_reviewer_arena.log",
    log_level: int = ARENA_LOGGING_LEVEL,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    max_bytes: int = 100 * 1024 * 1024,
    backup_count: int = 5,
    log_dir: str = "logs",
):
    """
    Sets up logging configuration.

    Parameters:
    log_file (str): Name of the log file.
    log_level (int): Logging level (e.g., logging.DEBUG, logging.INFO).
    log_format (str): Format of the log messages.
    max_bytes (int): Maximum size of a log file before it is rotated.
    backup_count (int): Number of backup log files to keep.
    log_dir (str): Directory where log files will be stored.
    """
    # Check for environment variable for logging level
    env_log_level = os.getenv("APP_LOGGING_LEVEL")
    if env_log_level is not None:
        level = getattr(logging, env_log_level.upper(), None)
        if isinstance(level, int):
            log_level = level
        else:
            raise ValueError(f"Invalid log level: {env_log_level}")

    # Ensure log directory exists
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # Define the logging configuration
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": log_format,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
            "file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "standard",
                "filename": os.path.join(log_dir, log_file),
                "maxBytes": max_bytes,
                "backupCount": backup_count,
                "encoding": "utf8",
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["console", "file_handler"],
        },
    }

    # Apply the logging configuration
    logging.config.dictConfig(logging_config)
