"""Central logging configuration for eve-static-data.

The ``setup_logging`` function installs a ``dictConfig`` with rotating file
handlers for info/warning output and a console handler for critical messages.
"""

import logging
import logging.config
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def setup_logging(log_dir: Path) -> None:
    """Create log directories and configure application-wide logging.

    Args:
        log_dir: Directory where log files are written.

    Notes:
        The resulting configuration sets:
        - root logger level to ``DEBUG``
        - rotating file logs for INFO and WARNING+
        - console output at ``CRITICAL`` level
    """
    log_dir.mkdir(parents=True, exist_ok=True)

    log_config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "consoleFormatter": {
                "format": "%(asctime)s | %(name)s | %(levelname)s : %(message)s",
            },
            "fileFormatter": {
                "format": "%(asctime)s | %(name)s | %(levelname)-8s : %(message)s",
            },
            "brief": {
                "datefmt": "%H:%M:%S",
                "format": "%(levelname)-8s; %(name)s; %(message)s;",
            },
            "single-line": {
                "datefmt": "%H:%M:%S",
                "format": "%(levelname)-8s; %(asctime)s; %(name)s; %(module)s:%(funcName)s;%(lineno)d: %(message)s",
            },
            "multi-process": {
                "datefmt": "%H:%M:%S",
                "format": "%(levelname)-8s; [%(process)d]; %(name)s; %(module)s:%(funcName)s;%(lineno)d: %(message)s",
            },
            "multi-thread": {
                "datefmt": "%H:%M:%S",
                "format": "%(levelname)-8s; %(threadName)s; %(name)s; %(module)s:%(funcName)s;%(lineno)d: %(message)s",
            },
            "verbose": {
                "format": "%(levelname)-8s; [%(process)d]; %(threadName)s; %(name)s; %(module)s:%(funcName)s;%(lineno)d"
                ": %(message)s"
            },
            "multiline": {
                "format": "Level: %(levelname)s\nTime: %(asctime)s\nProcess: %(process)d\nThread: %(threadName)s\nLogger"
                ": %(name)s\nPath: %(module)s:%(lineno)d\nFunction :%(funcName)s\nMessage: %(message)s\n"
            },
            "mine": {
                "format": "%(asctime)s | %(levelname)-8s | %(funcName)s | %(message)s | [in %(pathname)s | %(lineno)d]"
            },
            "mine-multi": {
                "format": "%(asctime)s | %(levelname)-8s | %(funcName)s | [in %(pathname)s | %(lineno)d]\n\t %(message)s"
            },
        },
        "handlers": {
            "file": {
                "filename": log_dir / "debug.log",
                "level": "DEBUG",
                "class": "logging.FileHandler",
                "formatter": "mine",
            },
            "console": {
                "level": "CRITICAL",
                "class": "logging.StreamHandler",
                "formatter": "consoleFormatter",
            },
            "rot_file_info": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "mine-multi",
                "level": "INFO",
                "filename": log_dir / "rotating_info.log",
                "mode": "a",
                "encoding": "utf-8",
                "maxBytes": 10000000,
                "backupCount": 10,
            },
            "rot_file_warn": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "mine-multi",
                "level": "WARNING",
                "filename": log_dir / "rotating_warn.log",
                "mode": "a",
                "encoding": "utf-8",
                "maxBytes": 500000,
                "backupCount": 4,
            },
        },
        "loggers": {
            "": {
                "handlers": ["rot_file_info", "rot_file_warn", "console"],
                "level": "DEBUG",
            },
        },
    }
    logging.config.dictConfig(log_config)
