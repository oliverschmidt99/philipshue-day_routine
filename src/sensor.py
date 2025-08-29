# src/sensor.py
from .logger import Logger


class Sensor:
    """
    Liest Daten von einem Hue-Bewegungssensor und stellt sie bereit.
    Verwendet die +1/+2 Logik, um die zugehörigen Licht- und Temperatursensoren zu finden.
    """

    def __init__(self, bridge, sensor_id, log: Logger):
        """Initialisiert das Sensor-Objekt und die zugehörigen IDs."""
        self.bridge = bridge
        self.log = log
        try:
            self.motion_sensor_id = int(sensor_id)
        except (ValueError, TypeError):
            self.log.error(
                f"Ungültige Sensor-ID erhalten: {sensor_id}. Dieser Sensor wird nicht funktionieren."
            )
            self.motion_sensor_id = None

        if self.motion_sensor_id is not None:
            # Annahme, dass der Helligkeitssensor die ID+1 und der Temperatursensor
            # die ID+2 hat, basierend auf dem Standard-Verhalten der Hue Bridge.
            self.light_sensor_id = self.motion_sensor_id + 1
            self.temp_sensor_id = self.motion_sensor_id + 2
            self.log.info(
                f"Initialisiere Sensor-Einheit für Bewegungs-ID: {self.motion_sensor_id}"
            )
        else:
            self.light_sensor_id = None
            self.temp_sensor_id = None

    def _get_state_value(self, sensor_id, key, default_value):
        """Holt einen bestimmten Wert aus dem 'state'-Dictionary eines bestimmten Sensors."""
        if sensor_id is None:
            return default_value
        try:
            # Das ganze Sensor-Objekt holen, um zu prüfen, ob es existiert.
            sensor_data = self.bridge.get_sensor(sensor_id)

            if sensor_data is None:
                self.log.debug(f"Sensor {sensor_id} nicht auf der Bridge gefunden.")
                return None

            state = sensor_data.get("state")
            if state:
                return state.get(key, default_value)

            self.log.warning(f"Kein 'state' für Sensor {sensor_id} empfangen.")
            return None
        except Exception as e:
            self.log.error(
                f"Fehler beim Abrufen des Zustands für Sensor {sensor_id}: {e}"
            )
            return None

    def get_motion(self) -> bool:
        """Gibt True zurück, wenn eine Bewegung erkannt wird, sonst False."""
        presence = self._get_state_value(self.motion_sensor_id, "presence", False)
        # Wenn der Sensor nicht gefunden wird (None), gehe von keiner Bewegung aus.
        return presence is True

    def get_brightness(self) -> int | None:
        """Gibt den Helligkeitswert (lightlevel) vom zugehörigen Lichtsensor zurück."""
        return self._get_state_value(self.light_sensor_id, "lightlevel", None)

    def get_temperature(self) -> float | None:
        """Gibt die Temperatur in Grad Celsius vom zugehörigen Temperatursensor zurück."""
        temp_raw = self._get_state_value(self.temp_sensor_id, "temperature", None)
        return temp_raw / 100.0 if temp_raw is not None else None
