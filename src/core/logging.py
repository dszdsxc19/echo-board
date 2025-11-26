"""Logging configuration for Echo-Board application."""

import logging
import sys
from pathlib import Path
from typing import Optional

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)


class EchoBoardLogger:
    """Centralized logging configuration for Echo-Board."""

    _loggers = {}

    @classmethod
    def get_logger(
        cls,
        name: str,
        log_file: Optional[str] = None,
        level: int = logging.INFO,
    ) -> logging.Logger:
        """Get or create a logger instance.

        Args:
            name: Logger name
            log_file: Optional log file path
            level: Logging level

        Returns:
            Configured logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Avoid duplicate handlers
        if logger.handlers:
            cls._loggers[name] = logger
            return logger

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler (if specified)
        if log_file:
            log_path = LOGS_DIR / log_file
            file_handler = logging.FileHandler(log_path)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        cls._loggers[name] = logger
        return logger

    @classmethod
    def setup_default_loggers(cls):
        """Setup default loggers for different components."""
        # Agent workflow logger
        cls.get_logger(
            "agents",
            log_file="agents.log",
            level=logging.INFO,
        )

        # Database logger
        cls.get_logger(
            "database",
            log_file="database.log",
            level=logging.WARNING,
        )

        # Vector store logger
        cls.get_logger(
            "vector_store",
            log_file="vector_store.log",
            level=logging.INFO,
        )

        # Conversation logger
        cls.get_logger(
            "conversations",
            log_file="conversations.log",
            level=logging.INFO,
        )

        # UI logger
        cls.get_logger(
            "ui",
            log_file="ui.log",
            level=logging.WARNING,
        )


# Helper functions for structured logging
def log_agent_start(agent_type: str, user_query: str):
    """Log when an agent starts processing."""
    logger = EchoBoardLogger.get_logger("agents")
    logger.info(f"[{agent_type}] Starting processing for: {user_query[:100]}")


def log_agent_complete(agent_type: str, processing_time: float):
    """Log when an agent completes processing."""
    logger = EchoBoardLogger.get_logger("agents")
    logger.info(f"[{agent_type}] Completed in {processing_time:.2f}s")


def log_agent_error(agent_type: str, error: str):
    """Log when an agent encounters an error."""
    logger = EchoBoardLogger.get_logger("agents")
    logger.error(f"[{agent_type}] Error: {error}")


def log_session_start(session_id: str, user_query: str):
    """Log when a conversation session starts."""
    logger = EchoBoardLogger.get_logger("conversations")
    logger.info(f"[Session: {session_id}] Started: {user_query[:100]}")


def log_session_complete(session_id: str, processing_time: float):
    """Log when a conversation session completes."""
    logger = EchoBoardLogger.get_logger("conversations")
    logger.info(f"[Session: {session_id}] Completed in {processing_time:.2f}s")


def log_vector_search(query: str, results_count: int):
    """Log vector similarity search."""
    logger = EchoBoardLogger.get_logger("vector_store")
    logger.info(f"Search: '{query[:100]}' -> {results_count} results")


def log_database_operation(operation: str, table: str, success: bool):
    """Log database operation."""
    logger = EchoBoardLogger.get_logger("database")
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"[{status}] {operation} on {table}")


# Setup default loggers when module is imported
EchoBoardLogger.setup_default_loggers()
