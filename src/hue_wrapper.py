"""
Ein Wrapper für die huesdk-Bibliothek, um die API zu kapseln und die
Testbarkeit sowie die zukünftige Wartung zu erleichtern.
Die nach außen gerichteten Methoden sind an die alte phue-Bibliothek angelehnt,
um die Umstellung des restlichen Codes zu minimieren.
"""
import warnings
from huesdk import Hue

class HueBridge:
    """
    Eine Klasse, die eine einzelne Verbindung zur Philips Hue Bridge verwaltet
    und die Methoden der huesdk-Bibliothek kapselt.
    """

    def __init__(self, ip: str = None, username: str = None, logger=None):
        """
        Initialisiert die Bridge-Verbindung mit der huesdk-Bibliothek.
        """
        self.ip = ip
        self.username = username
        self.log = logger
        self._bridge = None

        warnings.filterwarnings("ignore", message="Unverified HTTPS request")

        if ip and username:
            try:
                self._bridge = Hue(bridge_ip=self.ip, username=self.username)
            except Exception as e:
                self._log_error(f"Fehler bei der Initialisierung der Bridge: {e}")

    def _log_error(self, message: str, exc_info=False):
        if self.log:
            self.log.error(message, exc_info=exc_info)
        else:
            print(f"ERROR: {message}")

    @staticmethod
    def connect(ip: str) -> str | None:
        try:
            return Hue.connect(bridge_ip=ip)
        except Exception:
            return None

    def is_connected(self) -> bool:
        if not self._bridge:
            return False
        try:
            self._bridge.get_lights()
            return True
        except Exception:
            return False

    def get_api(self) -> dict | None:
        if not self._bridge:
            return None
        try:
            return self._bridge.get(f'/{self.username}')
        except Exception as e:
            self._log_error(f"Fehler beim Abrufen des API-Status: {e}")
            return None

    def get_sensor(self, sensor_id: int) -> dict | None:
        if not self._bridge:
            return None
        try:
            return self._bridge.get(f'/{self.username}/sensors/{sensor_id}')
        except Exception as e:
            self._log_error(f"Fehler beim Abrufen von Sensor {sensor_id}: {e}")
            return None

    def get_group(self, group_id: int) -> dict | None:
        if not self._bridge:
            return None
        try:
            return self._bridge.get(f'/{self.username}/groups/{group_id}')
        except Exception as e:
            self._log_error(f"Fehler beim Abrufen von Gruppe {group_id}: {e}")
            return None

    def set_group(self, group_id: int, state: dict):
        if not self._bridge:
            return
        try:
            self._bridge.put(f'/{self.username}/groups/{group_id}/action', state)
        except Exception as e:
            self._log_error(f"Fehler beim Setzen des Zustands für Gruppe {group_id}: {e}")