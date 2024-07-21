from control.huebridge import *
from control.Room import *

import logging

sen = b.get_sensor_objects("name")
light_names = b.get_light_objects("name")
lights = b.lights


class Sensor:

    def __init__(self, sensor_id, name_room):
        self.sensor_id = sensor_id
        self.name_room = name_room


class Motion(Sensor):
    def __init__(self, sensor_id, name_room):
        super().__init__(sensor_id, name_room)

        self.sensor_id = sensor_id

    def get_motion(self):
        logging.info(f"Sen_State\t\tTrue\t\t{self.name_room}")
        sensor_info = b.get_sensor(self.sensor_id)
        motion_detected = sensor_info.get("state", {}).get("presence", False)
        return motion_detected


class Brightness(Sensor):
    def __init__(self, sensor_id, name_room):
        super().__init__(sensor_id, name_room)

        self.sensor_id = sensor_id + 1

    def get_brightness(self):
        logging.info(f"Sen_State\t\tTrue\t\t{self.name_room}")
        try:
            # Sensordaten abrufen
            sensor_data = b.get_sensor(self.sensor_id)

            # Helligkeitswert (Lux) extrahieren
            if "state" in sensor_data and "lightlevel" in sensor_data["state"]:
                lux_value = sensor_data["state"]["lightlevel"]
                return lux_value
            else:
                return None

        except Exception as e:
            return None


class Temperature(Sensor):
    def __init__(self, sensor_id, name_room):
        super().__init__(sensor_id, name_room)

        self.sensor_id = [sensor_id + 2]

    def get_temperature(self):
        logging.info(f"Sen_State\t\tTrue\t\t{self.name_room}")
        sensors = b.get_sensor_objects("id")
        sensor = sensors[self.sensor_id]
        if sensor.type == "ZLLTemperature":
            # Die Temperatur wird in Zehntelgrad angegeben, daher durch 100 teilen
            temperature = sensor.state["temperature"] / 100.0
            return temperature
