from control.huebridge import *
from control.Room import *
from control.Daily_time_span import *


import logging
import time



class Sensor():
    __last_active_time__ = 0

    def __init__(self, sensor_id, name_room, room_instance):
        self.sensor_id_motion       = sensor_id
        self.sensor_id_brightness   = sensor_id + 1
        self.sensor_id_temperature  = sensor_id + 2
        try:
            self.sensor_data = b.get_sensor(sensor_id)
        except Exception as e:
            print(f"Error initializing sensor data: {e}")
            self.sensor_data = None
        self.name_room = name_room
        self.room_instance = room_instance

    def get_sensor(self, sensor_id):
        try:
            return b.get_sensor(sensor_id)
        except Exception as e:
            print(f"Error getting sensor data for sensor_id {sensor_id}: {e}")
            return None

    def get_attribute(self, attribute_name, sen_id):
        try:
            sen = self.get_sensor(sen_id)
            if sen is not None:
                return sen["state"].get(attribute_name, None)
            else:
                print("Sensor data is not available.")
                return None
        except Exception as e:
            print(f"Error getting attribute {attribute_name}: {e}")
            return None

    def get_motion(self):
        try:
            return self.get_attribute("presence", self.sensor_id_motion)
        except Exception as e:
            print(f"Error getting motion attribute: {e}")
            return None

    def get_brightness(self):
        try:
            return self.get_attribute("lightlevel", self.sensor_id_brightness)
        except Exception as e:
            print(f"Error getting brightness attribute: {e}")
            return None

    def get_temperature(self):
        try:
            temperature = self.get_attribute("temperature", self.sensor_id_temperature)
            if temperature is not None:
                # Convert temperature from deci-degrees Celsius to degrees Celsius
                temperature = temperature / 100.0
            return temperature
        except Exception as e:
            print(f"Error getting temperature attribute: {e}")
            return None

    def turn_off_after_motion(self, scene, wait_time):
        #try:
            if self.get_motion():
                print("Moin")
                self.room_instance.turn_on_groups(scene)
                self.last_active_time = time.time()
                return
            if self.last_active_time + wait_time <= time.time():
                print("bye")
                self.room_instance.turn_off_groups()
        #except Exception as e:
        #    print(f"Error in turn_off_after_motion: {e}")
    
    def turn_on_low_light(self, scene, min_light_level, room, check):
        #try:
            if self.get_brightness() < min_light_level:
                print("a ", self.get_brightness())
                if check is False:
                    room.turn_on_groups(scene)
                    print(check)
                    check = True
                    return check
                else:
                    return check
            else:
                if check is True:
                    print("b ", self.get_brightness())
                    room.turn_off_groups()
                    check = False
                    return check
            
        #except Exception as e:
        #    print(f"Error in turn_on_low_light: {e}")

            
