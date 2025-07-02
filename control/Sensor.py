class Sensor:
    """
    Liest und stellt Daten von einem Hue Bewegungsmelder bereit.
    """
    def __init__(self, bridge, sensor_id):
        self.bridge = bridge
        self.sensor_id = sensor_id
        self.last_state = {}

    def _update_state(self):
        """Holt den aktuellen Zustand des Sensors von der Bridge."""
        data = self.bridge.get_sensor(self.sensor_id)
        if data and 'state' in data:
            self.last_state = data['state']
            return True
        return False

    def get_motion(self) -> bool:
        """Gibt zurück, ob eine Bewegung erkannt wurde."""
        if self._update_state():
            return self.last_state.get('presence', False)
        return False

    def get_brightness(self) -> int:
        """Gibt den Helligkeitswert (lightlevel) zurück."""
        if self._update_state():
            return self.last_state.get('lightlevel', 0)
        return 0

    def get_temperature(self) -> float:
        """Gibt die Temperatur in Grad Celsius zurück."""
        if self._update_state():
            # Der Sensor liefert die Temperatur * 100
            return self.last_state.get('temperature', 0) / 100.0
        return 0.0
