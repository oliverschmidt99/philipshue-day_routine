"""
Ein Wrapper für die phue-Bibliothek, um die API zu kapseln und die
Testbarkeit sowie die zukünftige Wartung zu erleichtern.
"""
from phue import Bridge, PhueException
from requests.exceptions import RequestException

# Der HTTPS-Patch wurde entfernt.

class HueBridge:
    """
    Eine Klasse, die eine einzelne Verbindung zur Philips Hue Bridge verwaltet
    und die Methoden der phue-Bibliothek kapselt.
    """

    def __init__(self, ip: str = None, username: str = None, logger=None):
        """
        Initialisiert die Bridge-Verbindung.
        """
        self.ip = ip
        self.username = username
        self._bridge = None
        self.log = logger

        if ip and username:
            try:
                self._bridge = Bridge(ip, username=username)
            except (PhueException, RequestException) as e:
                self._log_error(f"Fehler bei der Initialisierung der Bridge: {e}")

    def _log_error(self, message: str, exc_info=False):
        """Protokolliert eine Fehlermeldung, falls ein Logger vorhanden ist."""
        if self.log:
            self.log.error(message, exc_info=exc_info)
        else:
            print(f"ERROR: {message}")

    def connect(self) -> bool:
        """
        Stellt die Verbindung zur Bridge her und authentifiziert die App.
        """
        if not self.ip:
            self._log_error("Verbindung fehlgeschlagen: IP-Adresse nicht gesetzt.")
            return False
        try:
            # Standard-Verbindungsaufruf ohne Patch. config_file_path=None erzwingt eine neue Registrierung.
            b = Bridge(self.ip, config_file_path=None)

            if b.username:
                self._bridge = b
                self.username = b.username
                if self.log:
                    self.log.info(f"Erfolgreich mit Bridge {self.ip} verbunden und App-Key erhalten.")
                return True
            else:
                self._log_error("Verbindung fehlgeschlagen: Bridge hat keinen App-Key zurückgegeben.")
                return False

        except PhueException as e:
            error_message = str(e)
            if "101" in error_message:
                error_message = "Der Link-Button auf der Bridge wurde nicht gedrückt."
            self._log_error(f"Phue-Fehler beim Verbinden: {error_message}")
            return False
        except RequestException as e:
            self._log_error(f"Netzwerkfehler beim Verbinden: {e}")
            return False
        except Exception as e:
            self._log_error(f"Ein unerwarteter Fehler ist beim Verbinden aufgetreten: {e}", exc_info=True)
            return False


    def is_connected(self) -> bool:
        """
        Überprüft, ob eine funktionierende Verbindung zur Bridge besteht.
        """
        if not self._bridge:
            return False
        try:
            self._bridge.get_api()
            return True
        except (PhueException, RequestException):
            return False

    def get_full_api_state(self) -> dict | None:
        """
        Gibt den gesamten Zustand der Bridge als Dictionary zurück.
        """
        if not self._bridge:
            return None
        try:
            return self._bridge.get_api()
        except (PhueException, RequestException) as e:
            self._log_error(f"Fehler beim Abrufen des API-Status: {e}")
            return None

    def get_sensor(self, sensor_id: int) -> dict | None:
        """
        Holt die Daten für einen einzelnen Sensor.
        """
        if not self._bridge:
            return None
        try:
            return self._bridge.get_sensor(sensor_id)
        except (PhueException, RequestException) as e:
            self._log_error(f"Fehler beim Abrufen von Sensor {sensor_id}: {e}")
            return None

    def get_group(self, group_id: int) -> dict | None:
        """
        Holt die Daten für eine einzelne Gruppe (Raum/Zone).
        """
        if not self._bridge:
            return None
        try:
            return self._bridge.get_group(group_id)
        except (PhueException, RequestException) as e:
            self._log_error(f"Fehler beim Abrufen von Gruppe {group_id}: {e}")
            return None

    def set_group_state(self, group_id: int, state: dict):
        """
        Setzt den Zustand einer Lichtgruppe.
        """
        if not self._bridge:
            return
        try:
            self._bridge.set_group(group_id, state)
        except (PhueException, RequestException) as e:
            self._log_error(f"Fehler beim Setzen des Zustands für Gruppe {group_id}: {e}")