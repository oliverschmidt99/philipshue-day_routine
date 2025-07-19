class Sensor:
    """
    Liest Daten von einem Hue-Bewegungssensor und stellt sie bereit.
    Verwendet die +1/+2 Logik, um die zugehörigen Licht- und Temperatursensoren zu finden.
    """

    def __init__(self, bridge, sensor_id, log):
        """Initialisiert das Sensor-Objekt und die zugehörigen IDs."""
        self.bridge = bridge
        self.log = log
        self.motion_sensor_id = int(sensor_id)
        
        # Annahme, dass der Helligkeitssensor die ID+1 und der Temperatursensor
        # die ID+2 hat, basierend auf dem Standard-Verhalten der Hue Bridge.
        self.light_sensor_id = self.motion_sensor_id + 1
        self.temp_sensor_id = self.motion_sensor_id + 2

        self.log.info(f"Initialisiere Sensor-Einheit für Bewegungs-ID: {self.motion_sensor_id}")
        self.log.info(f"-> Annahme für Lichtsensor-ID: {self.light_sensor_id}")
        self.log.info(f"-> Annahme für Temperatursensor-ID: {self.temp_sensor_id}")


    def _get_state_value(self, sensor_id, key, default_value):
        """Holt einen bestimmten Wert aus dem 'state'-Dictionary eines bestimmten Sensors."""
        if sensor_id is None:
            return default_value
        try:
            # Direkt den State abfragen, ist effizienter
            state = self.bridge.get_sensor(sensor_id, 'state')
            if state:
                self.log.debug(f"Sensor {sensor_id} raw state: {state}")
                return state.get(key, default_value)
            self.log.warning(f"Kein 'state' für Sensor {sensor_id} empfangen.")
            return None # Gibt None bei Fehler zurück
        except Exception as e:
            # Es ist normal, dass ein Sensor nicht gefunden wird, wenn er nicht existiert.
            # Daher wird hier eine Debug-Nachricht anstelle eines Fehlers verwendet.
            self.log.debug(f"Fehler beim Abrufen des Zustands für Sensor {sensor_id}: {e}")
            return None # Gibt None bei Fehler zurück

    def get_motion(self) -> bool:
        """Gibt True zurück, wenn eine Bewegung erkannt wird, sonst False."""
        presence = self._get_state_value(self.motion_sensor_id, 'presence', False)
        return presence if presence is not None else False

    def get_brightness(self) -> int:
        """Gibt den Helligkeitswert (lightlevel) vom zugehörigen Lichtsensor zurück."""
        lightlevel = self._get_state_value(self.light_sensor_id, 'lightlevel', 0)
        return lightlevel

    def get_temperature(self) -> float:
        """Gibt die Temperatur in Grad Celsius vom zugehörigen Temperatursensor zurück."""
        temp = self._get_state_value(self.temp_sensor_id, 'temperature', 0)
        return temp / 100.0 if temp is not None else None