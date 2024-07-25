from control.huebridge import *
import logging

sen = b.get_sensor_objects("name")
light_names = b.get_light_objects("name")
lights = b.lights


class Room:

    def __init__(
        self,
        group_ids,
        switch_ids,
        sensors_ids,
        name_room,
    ):
        self.group_ids = group_ids
        self.switch_ids = switch_ids
        self.sensors_ids = sensors_ids
        self.name_room = name_room

    def turn_off_groups(self):

        for group_id in self.group_ids:
            logging.info(f"State\t\toff\t\t{self.name_room}")
            b.set_group(group_id, "on", False)

    def turn_on_groups(self, brightness, t_time):
        for group_id in self.group_ids:
            logging.info(f"State\t\ton\t\t{self.name_room}")
            b.set_group(group_id, "on", True)
            b.set_group(group_id, "bri", brightness, transitiontime=t_time)
