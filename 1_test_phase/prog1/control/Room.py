from control.huebridge import *
from control.Sensor import *
import logging

sen = b.get_sensor_objects("name")
light_names = b.get_light_objects("name")
lights = b.lights


class Room(Sensor):

    def __init__(
        self,
        group_ids,
        switch_ids,
        sensor_id,
        name_room,
    ):
        self.group_ids = group_ids
        self.switch_ids = switch_ids
        self.sensor_id = sensor_id
        self.name_room = name_room

        self.motion = Motion(sensor_id=self.sensor_id, name_room=self.name_room)
        self.brightness = Brightness(
            sensor_id=self.sensor_id + 1, name_room=self.name_room
        )
        self.temperature = Temperature(
            sensor_id=self.sensor_id + 2, name_room=self.name_room
        )

    def turn_off_groups(self):

        for group_id in self.group_ids:
            logging.info(f"State\t\toff\t\t{self.name_room}")
            b.set_group(group_id, "on", False)

    def turn_on_groups(self, brightness, t_time):
        for group_id in self.group_ids:
            logging.info(f"State\t\ton\t\t{self.name_room}")
            b.set_group(group_id, "on", True)
            b.set_group(group_id, "bri", brightness, transitiontime=t_time)
