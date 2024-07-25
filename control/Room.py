from control.huebridge import *
from control.Sensor import *
import logging

sen = b.get_sensor_objects("name")
light_names = b.get_light_objects("name")
lights = b.lights

class Scene:
    def __init__(self, bri, sat, ct, t_time) -> None:
        """:parameters:  'bri' : 0-254, 'sat' : 0-254, 'ct': 154-500"""
        self.bri = bri
        self.sat = sat
        self.ct = ct
        self.t_time = t_time

class Room(Sensor):

    def __init__(self, group_ids, switch_ids, sensor_id, name_room) -> None:
        self.group_ids = group_ids
        self.switch_ids = switch_ids
        self.sensor_id = sensor_id
        self.name_room = name_room


        if self.sensor_id is not None:
            self.motion = Motion(
                sensor_id=self.sensor_id,
                name_room=self.name_room,
                bridge_ip=BRIDGE_IP,
                room_instance=self,
            )
            self.brightness = Brightness(
                sensor_id=self.sensor_id + 1,
                name_room=self.name_room,
                bridge_ip=BRIDGE_IP,
                room_instance=self,
            )
            self.temperature = Temperature(
                sensor_id=self.sensor_id + 2, name_room=self.name_room, bridge_ip=BRIDGE_IP
            )
        


    def turn_off_groups(self):
        for group_id in self.group_ids:
            logging.info(f"State\t\toff\t\t{self.name_room}")
            b.set_group(group_id, "on", False)

    def turn_on_groups(self, scene: Scene):
        for group_id in self.group_ids:
            logging.info(f"State\t\ton\t\t{self.name_room}")
            b.set_group(group_id, "on", True)
            b.set_group(group_id, "bri", scene.bri, transitiontime=scene.t_time)
            b.set_group(group_id, "sat", scene.sat)
            b.set_group(group_id, "ct", scene.ct)



