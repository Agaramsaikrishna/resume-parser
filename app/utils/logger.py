import logging
import os

def setup_logger(name: str = __name__, level: str = "INFO") -> logging.Logger:
    """
    Setup and return a logger using Python's built-in logging.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level.upper())

    if not logger.handlers:  # prevent adding multiple handlers
        ch = logging.StreamHandler()
        ch.setLevel(level.upper())
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s:%(funcName)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger
