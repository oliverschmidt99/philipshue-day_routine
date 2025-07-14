class Sensor:
    """
    Liest und stellt Daten von einem Hue Bewegungsmelder
    über das phue Bridge-Objekt bereit.
    """
    def __init__(self, bridge, sensor_id, log):
        self.bridge = bridge
        self.sensor_id = int(sensor_id) # phue erwartet Integer
        self.log = log
        # Prüfe beim Start, ob der Sensor überhaupt existiert, um Konfigurationsfehler früh zu erkennen.
        if not self._get_sensor_data():
             self.log.error(f"Initialisierung für Sensor {self.sensor_id} fehlgeschlagen. Sensor konnte auf der Bridge nicht gefunden werden.")

    def _get_sensor_data(self):
        """Holt die aktuellen Rohdaten des Sensors (als dict) von der Bridge."""
        try:
            # Die get_sensor() Methode der phue-Bibliothek gibt ein Dictionary zurück.
            sensor_data = self.bridge.get_sensor(self.sensor_id)
            if not sensor_data:
                self.log.warning(f"Keine Daten für Sensor {self.sensor_id} von der Bridge empfangen.")
            return sensor_data
        except Exception as e:
            self.log.error(f"Netzwerk- oder Bibliotheksfehler beim Abrufen der Daten für Sensor {self.sensor_id}: {e}")
            return None

    def _get_state_value(self, key, default_value):
        """Holt einen spezifischen Wert aus dem 'state'-Dictionary des Sensors."""
        sensor_data = self._get_sensor_data()
        
        # Prüfe, ob die Daten und der 'state'-Schlüssel vorhanden sind.
        if sensor_data and 'state' in sensor_data:
            return sensor_data['state'].get(key, default_value)
        
        # Wenn keine Daten oder kein 'state' vorhanden ist, gib den Standardwert zurück.
        # Das verhindert, dass das Programm bei einem temporären Lesefehler abstürzt.
        return default_value

    def get_motion(self) -> bool:
        """Gibt zurück, ob eine Bewegung erkannt wurde."""
        return self._get_state_value('presence', False)

    def get_brightness(self) -> int:
        """Gibt den Helligkeitswert (lightlevel) zurück."""
        return self._get_state_value('lightlevel', 0)

    def get_temperature(self) -> float:
        """Gibt die Temperatur in Grad Celsius zurück."""
        temp = self._get_state_value('temperature', 0)
        # Der Sensor liefert die Temperatur * 100
        return temp / 100.0
