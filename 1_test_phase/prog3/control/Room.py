from control.huebridge import *
from control.Sensor import *
import logging

sen = b.get_sensor_objects("name")
light_names = b.get_light_objects("name")
lights = b.lights


class Scene:
    def __init__(self, status , bri, sat, ct, t_time) -> None:
        """:parameters:  'bri' : 0-254, 'sat' : 0-254, 'ct': 154-500"""
        self.status = status
        self.bri = bri
        self.sat = sat
        self.ct = ct
        self.t_time = t_time


class Room():

    def __init__(self, group_ids, switch_ids, sensor_id, name_room) -> None:
        self.group_ids = group_ids
        self.switch_ids = switch_ids
        self.sensor_id = sensor_id
        self.name_room = name_room

        if self.sensor_id is not None:
            self.sensor = Sensor(
                sensor_id=self.sensor_id,
                name_room=self.name_room,
                room_instance=self,
            )

        
    def turn_groups(self, scene: Scene, status):
        
        if status is not None:
            scene.status = status

        
        if scene.status is True:
            for group_id in self.group_ids:
                logging.info(f"State\t\ton\t\t\t{self.name_room}")
                b.set_group(group_id, "on", True)
                b.set_group(group_id, "bri", scene.bri, transitiontime=scene.t_time)
                b.set_group(group_id, "sat", scene.sat)
                b.set_group(group_id, "ct", scene.ct)
        elif scene.status is False:
            for group_id in self.group_ids:
                logging.info(f"State\t\toff\t\t{self.name_room}")
                b.set_group(group_id, "on", False)
