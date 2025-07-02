import logging
import sys

class Logger:
    """
    Eine einfache Wrapper-Klasse für das Python-Logging, um
    Nachrichten in eine Datei und auf die Konsole zu schreiben.
    """
    def __init__(self, file_name):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Verhindern, dass Handler mehrfach hinzugefügt werden, falls die Klasse erneut instanziiert wird
        if not self.logger.handlers:
            # Handler für das Schreiben in eine Datei
            file_handler = logging.FileHandler(file_name, mode='w', encoding='utf-8')
            file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

            # Handler für die Ausgabe auf der Konsole
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_formatter = logging.Formatter('%(asctime)s - %(message)s')
            stream_handler.setFormatter(stream_formatter)
            self.logger.addHandler(stream_handler)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message, exc_info=False):
        self.logger.error(message, exc_info=exc_info)
