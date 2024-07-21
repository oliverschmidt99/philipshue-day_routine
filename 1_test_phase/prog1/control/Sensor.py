from control.huebridge import *
from control.Room import *

import logging


class Sensor:

    def __init__(self, sensor_id, name_room):
        self.sensor_id = sensor_id
        self.name_room = name_room
        self.sensor_data = self.get_sensor(sensor_id)

    def get_sensor(self, sensor_id):
        return b.get_sensor(sensor_id)

    def get_attribute(self, attribute_name):
        sen = self.get_sensor(self.sensor_id)
        return sen["state"].get(attribute_name, None)


class Motion(Sensor):
    def __init__(self, sensor_id, name_room):
        super().__init__(sensor_id, name_room)

    def get_motion(self):
        return self.get_attribute("presence")


class Brightness(Sensor):
    def __init__(self, sensor_id, name_room):
        super().__init__(sensor_id, name_room)

    def get_brightness(self):
        return self.get_attribute("lightlevel")


class Temperature(Sensor):
    def __init__(self, sensor_id, name_room):
        super().__init__(sensor_id, name_room)

    def get_temperature(self):
        temperature = self.get_attribute("temperature")
        if temperature is not None:
            # Convert temperature from deci-degrees Celsius to degrees Celsius
            temperature = temperature / 100.0
        return temperature
