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

    def turn_off_after_motion(self, scene, x_scene, wait_time, check):
        try:
            current_motion = self.get_motion()
            
            if current_motion is None:
                logging.error(f"Error: Unable to retrieve motion state for {self.name_room}")
                return check
            
            if current_motion:
                self.__last_active_time__ = time.time()
                if not check:
                    logging.info(f"State\t\tmotion detected\t\t{self.name_room}")
                    check = True
                    self.room_instance.turn_groups(scene, True)
                # Das Licht ist bereits an, daher keine weitere Aktion erforderlich
            else:
                # Überprüfe, ob die Wartezeit abgelaufen ist, bevor das Licht ausgeschaltet wird
                if time.time() > self.__last_active_time__ + wait_time:
                    if check:
                        logging.info(f"State\t\tno motion, turning off\t{self.name_room}")
                        check = False
                        self.room_instance.turn_groups(x_scene, x_scene.status)
                # Das Licht ist bereits aus, daher keine weitere Aktion erforderlich
            
            return check
        
        except Exception as e:
            logging.error(f"Error in turn_off_after_motion: {e}")
            return check
    


    def turn_on_low_light(self, scene, x_scene, min_light_level, check):
        try:
            current_brightness = self.get_brightness()
            #print(current_brightness)

            if current_brightness is None:
                logging.error(f"Error: Unable to retrieve brightness for {self.name_room}")
                return check
            
            if current_brightness < min_light_level:
                if not check:
                    logging.info(f"State\t\tdark\t\t{self.name_room}")
                    logging.info(f"Brightness\t\t{current_brightness}")
                    check = True
                    self.room_instance.turn_groups(x_scene, True)
            else:
                if check:
                    logging.info(f"State\t\tbright\t\t{self.name_room}")
                    logging.info(f"Brightness\t\t{current_brightness}")
                    check = False
                    self.room_instance.turn_groups(scene, None)
            
            return check
            
        except Exception as e:
            logging.error(f"Error in turn_on_low_light: {e}")

            
