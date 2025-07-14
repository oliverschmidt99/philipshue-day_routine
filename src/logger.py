# src/logger.py
# (Inhaltlich unverändert, nur Kommentare bereinigt)

import logging
import sys

class Logger:
    """A simple wrapper for Python's logging to write to file and console."""
    def __init__(self, file_name, level=logging.DEBUG):
        """Initializes the logger."""
        self.logger = logging.getLogger(f"hue_routine_logger_{file_name}")
        self.logger.setLevel(level)

        if not self.logger.handlers:
            # File handler
            file_handler = logging.FileHandler(file_name, mode='w', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

            # Console handler
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setLevel(logging.INFO) 
            stream_formatter = logging.Formatter('%(asctime)s - %(message)s')
            stream_handler.setFormatter(stream_formatter)
            self.logger.addHandler(stream_handler)

    def debug(self, message):
        """Logs a debug message."""
        self.logger.debug(message)

    def info(self, message):
        """Logs an info message."""
        self.logger.info(message)

    def warning(self, message):
        """Logs a warning message."""
        self.logger.warning(message)

    def error(self, message, exc_info=False):
        """Logs an error message."""
        self.logger.error(message, exc_info=exc_info)

# ---