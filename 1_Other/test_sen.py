from phue import Bridge
import time


class Sensor:
    def __init__(self, bridge_ip, sensor_id):
        self.bridge = Bridge(bridge_ip)
        self.sensor_id = sensor_id
        self.bridge.connect()
        self.sensor_data = self.bridge.get_sensor(sensor_id)

    def get_sensor(self, sensor_id):
        return self.bridge.get_sensor(sensor_id)

    def get_attribute(self, attribute_name):
        sen = self.get_sensor(self.sensor_id)
        return sen["state"].get(attribute_name, None)


class Motion(Sensor):
    def __init__(self, bridge_ip, sensor_id):
        super().__init__(bridge_ip, sensor_id)

    def get_motion(self):
        return self.get_attribute("presence")


class Brightness(Sensor):
    def __init__(self, bridge_ip, sensor_id):
        super().__init__(bridge_ip, sensor_id)

    def get_brightness(self):
        return self.get_attribute("lightlevel")


class Temperature(Sensor):
    def __init__(self, bridge_ip, sensor_id):
        super().__init__(bridge_ip, sensor_id)

    def get_temperature(self):
        temperature = self.get_attribute("temperature")
        if temperature is not None:
            # Convert temperature from deci-degrees Celsius to degrees Celsius
            temperature = temperature / 100.0
        return temperature


# Beispiel für die Verwendung:
if __name__ == "__main__":
    BRIDGE_IP = "192.168.178.42"  # Ersetze dies mit der IP-Adresse deiner Hue Bridge
    MOTION_SENSOR_ID = 190  # Ersetze dies mit der ID deines Bewegungssensors
    BRIGHTNESS_SENSOR_ID = 191  # Ersetze dies mit der ID deines Helligkeitssensors
    TEMPERATURE_SENSOR_ID = 192  # Ersetze dies mit der ID deines Temperatursensors

    motion_sensor = Motion(BRIDGE_IP, MOTION_SENSOR_ID)
    brightness_sensor = Brightness(BRIDGE_IP, BRIGHTNESS_SENSOR_ID)
    temperature_sensor = Temperature(BRIDGE_IP, TEMPERATURE_SENSOR_ID)
    while True:
        print(f"Bewegung erkannt: {motion_sensor.get_motion()}")
        print(f"Helligkeit: {brightness_sensor.get_brightness()}")
        print(f"Temperatur: {temperature_sensor.get_temperature()}°C")
        time.sleep(1)
