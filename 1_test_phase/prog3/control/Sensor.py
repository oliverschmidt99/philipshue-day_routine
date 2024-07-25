from control.huebridge import *
from control.Room import *

import logging
import time


class Sensor:

    def __init__(self,  sensor_id, name_room):
        
        self.sensor_id = sensor_id

        self.sensor_data = b.get_sensor(sensor_id)
        self.name_room = name_room

    def get_sensor(self, sensor_id):
        return b.get_sensor(sensor_id)

    def get_attribute(self, attribute_name):
        sen = self.get_sensor(self.sensor_id)
        return sen["state"].get(attribute_name, None)


class Motion(Sensor):

    last_active_time = 0

    def __init__(self, sensor_id, name_room, room_instance):
        super().__init__( sensor_id, name_room)
        self.room_instance = room_instance

    def get_motion(self):
        return self.get_attribute("presence")

    def turn_off_after_motion(self, brightness, t_time, wait_time):
        if self.get_motion():
            print("Moin")
            self.room_instance.turn_on_groups(brightness, t_time)
            self.last_active_time = time.time()
            return
        if self.last_active_time + wait_time <= time.time():
            print("bye")
            self.room_instance.turn_off_groups()


class Brightness(Sensor):

    def __init__(self, sensor_id, name_room, room_instance):
        super().__init__(sensor_id, name_room)
        self.room_instance = room_instance

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
