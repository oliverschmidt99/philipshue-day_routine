import logging
import sys

class Logger:
    """
    Eine einfache Wrapper-Klasse für das Python-Logging, um
    Nachrichten in eine Datei und auf die Konsole zu schreiben.
    """
    def __init__(self, file_name):
        # Wir holen den Logger mit einem eindeutigen Namen, um Konflikte zu vermeiden
        self.logger = logging.getLogger(f"hue_routine_logger_{file_name}")
        self.logger.setLevel(logging.DEBUG) # Das Gesamtlevel bleibt DEBUG, damit wir die Funktion im Code nutzen können

        # Verhindern, dass Handler mehrfach hinzugefügt werden
        if not self.logger.handlers:
            # Handler für das Schreiben in eine Datei (inkl. Debug-Meldungen)
            file_handler = logging.FileHandler(file_name, mode='w', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            # Detaillierterer Formatter für die Datei, um die Herkunft der Nachricht zu sehen
            file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

            # Handler für die Ausgabe auf der Konsole
            stream_handler = logging.StreamHandler(sys.stdout)
            # Zeigt nur INFO und höhere Level auf der Konsole an, um sie nicht zu überfluten
            stream_handler.setLevel(logging.INFO) 
            stream_formatter = logging.Formatter('%(asctime)s - %(message)s')
            stream_handler.setFormatter(stream_formatter)
            self.logger.addHandler(stream_handler)

    def debug(self, message):
        """Loggt eine Debug-Nachricht."""
        self.logger.debug(message)

    def info(self, message):
        """Loggt eine Info-Nachricht."""
        self.logger.info(message)

    def warning(self, message):
        """Loggt eine Warnung."""
        self.logger.warning(message)

    def error(self, message, exc_info=False):
        """Loggt einen Fehler."""
        self.logger.error(message, exc_info=exc_info)
