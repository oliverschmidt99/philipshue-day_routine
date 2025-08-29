# src/logger.py
import logging
import sys
import os


class Logger:
    """
    Initialisiert und konfiguriert einen Logger, der sowohl in die Konsole
    als auch in eine Datei schreibt.
    """

    def __init__(self, log_file, level=logging.INFO):
        self.logger = logging.getLogger("HueRoutineAppLogger")

        if not self.logger.handlers:
            self.logger.setLevel(level)
            self.logger.propagate = False

            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - [%(module)s.py:%(lineno)d] - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            # Konsolen-Handler
            ch = logging.StreamHandler(sys.stdout)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

            # Datei-Handler
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            fh = logging.FileHandler(log_file, mode="a", encoding="utf-8")
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message, exc_info=False):
        self.logger.error(message, exc_info=exc_info)

    def debug(self, message):
        self.logger.debug(message)
