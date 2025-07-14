# src/sensor.py
# (Inhaltlich unverändert, nur Kommentare bereinigt)

class Sensor:
    """Reads and provides data from a Hue motion sensor."""
    def __init__(self, bridge, sensor_id, log):
        """Initializes the Sensor object."""
        self.bridge = bridge
        self.sensor_id = int(sensor_id)
        self.log = log
        if not self._get_sensor_data():
             self.log.error(f"Failed to initialize sensor {self.sensor_id}. Not found on bridge.")

    def _get_sensor_data(self):
        """Fetches the raw sensor data dictionary from the bridge."""
        try:
            sensor_data = self.bridge.get_sensor(self.sensor_id)
            if not sensor_data:
                self.log.warning(f"No data received for sensor {self.sensor_id}.")
            return sensor_data
        except Exception as e:
            self.log.error(f"Error fetching data for sensor {self.sensor_id}: {e}")
            return None

    def _get_state_value(self, key, default_value):
        """Gets a specific value from the sensor's 'state' dictionary."""
        sensor_data = self._get_sensor_data()
        if sensor_data and 'state' in sensor_data:
            return sensor_data['state'].get(key, default_value)
        return default_value

    def get_motion(self) -> bool:
        """Returns True if motion is detected, False otherwise."""
        return self._get_state_value('presence', False)

    def get_brightness(self) -> int:
        """Returns the brightness value (lightlevel)."""
        return self._get_state_value('lightlevel', 0)

    def get_temperature(self) -> float:
        """Returns the temperature in degrees Celsius."""
        temp = self._get_state_value('temperature', 0)
        return temp / 100.0

# ---