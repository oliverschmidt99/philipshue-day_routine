import logging
try:
    # Importiert die notwendigen Klassen aus der phue-Bibliothek
    from phue import Bridge, Group, Sensor
except ImportError:
    # Fallback, falls phue nicht installiert ist
    print("FEHLER: Die 'phue' Bibliothek wurde nicht gefunden. Bitte installiere sie mit 'pip install phue'")
    Bridge, Group, Sensor = None, None, None

from .logger import setup_logger

logger = setup_logger('HueBridgeLogger')

class HueBridge:
    """
    Verwaltet die Verbindung und Interaktion mit der Philips Hue Bridge.
    Diese Version enthält Workarounds für Kompatibilitätsprobleme
    beim Abrufen von Gruppen und Sensoren in der phue-Bibliothek.
    """
    def __init__(self, ip, username=None):
        self.bridge = None
        self.ip = ip
        self.username = username

        if not Bridge:
            logger.critical("HueBridge kann nicht initialisiert werden, da die 'phue' Bibliothek fehlt.")
            return

        try:
            self.bridge = Bridge(ip, username=username)
            self.bridge.get_api()
            logger.info(f"Erfolgreich mit Hue Bridge verbunden unter IP: {self.ip}")
        except Exception as e:
            logger.error(f"Verbindung zur Hue Bridge unter IP {ip} fehlgeschlagen: {e}")
            self.bridge = None

    def is_configured(self):
        """Prüft, ob die Verbindung zur Bridge erfolgreich hergestellt wurde."""
        return self.bridge is not None

    def get_groups(self):
        """
        Ruft alle Gruppen (Räume) von der Bridge ab.
        Behebt den 'list' object has no attribute 'keys' Fehler, indem
        die Gruppen direkt aus den API-Daten erstellt werden.
        """
        if not self.is_configured() or not Group:
            return []
        try:
            # Direkter und stabilerer Weg, die Gruppen-Daten zu erhalten
            groups_data = self.bridge.request('GET', f'/api/{self.username}/groups')
            if not isinstance(groups_data, dict):
                logger.warning(f"Unerwartete Antwort vom /groups Endpunkt: {groups_data}")
                return []
            return [Group(self.bridge, int(gid)) for gid in groups_data.keys()]
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Gruppen von der Bridge: {e}")
            return []

    def get_sensors(self):
        """Ruft alle Sensoren von der Bridge ab, mit stabilerer Fehlerbehandlung."""
        if not self.is_configured() or not Sensor:
            return []
        try:
            # Direkter und stabilerer Weg, die Sensor-Daten zu erhalten
            sensors_data = self.bridge.request('GET', f'/api/{self.username}/sensors')
            if not isinstance(sensors_data, dict):
                logger.warning(f"Unerwartete Antwort vom /sensors Endpunkt: {sensors_data}")
                return []
            
            sensor_objects = []
            for sensor_id in sensors_data.keys():
                try:
                    # Stellt sicher, dass die ID ein Integer ist, bevor das Objekt erstellt wird
                    sensor_objects.append(Sensor(self.bridge, int(sensor_id)))
                except (ValueError, TypeError):
                    logger.warning(f"Ungültige Sensor-ID übersprungen: {sensor_id}")
                    continue
            return sensor_objects
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Sensoren von der Bridge: {e}")
            return []

    def get_api(self):
        return self.bridge.get_api() if self.is_configured() else {}
