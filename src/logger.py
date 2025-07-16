import logging
import sys

class Logger:
    """
    Initialisiert und konfiguriert einen Logger, der sowohl in die Konsole
    als auch in eine Datei schreibt.
    """
    def __init__(self, log_file='info.log', level=logging.DEBUG):
        """
        Initialisiert den Logger. Stellt sicher, dass Handler nicht dupliziert werden.
        
        Args:
            log_file (str): Der Dateipfad für die Log-Datei.
            level (int): Das Logging-Level (z.B. logging.DEBUG, logging.INFO).
        """
        self.logger = logging.getLogger("HueRoutineAppLogger")
        
        # Konfiguriere den Logger nur, wenn er noch keine Handler hat.
        # Das verhindert doppelte Log-Einträge bei mehrmaliger Instanziierung.
        if not self.logger.handlers:
            self.logger.setLevel(level)
            self.logger.propagate = False

            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - [%(module)s.py:%(lineno)d] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            # Konsolen-Handler
            ch = logging.StreamHandler(sys.stdout)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

            # Datei-Handler
            fh = logging.FileHandler(log_file, mode='a', encoding='utf-8')
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
