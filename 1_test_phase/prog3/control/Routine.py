from control.huebridge import *
from control.Daily_time_span import *
from control.Room import *

import numpy as np
import logging


class InvalidTimeSpanException(Exception):
    def __init__(self, time_span, message="Invalid time span provided."):
        self.time_span = time_span
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} Time span: {self.time_span}"
    
class Section_Routine():
    def __init__(self, bri_check, min_light_level, motion_check, wait_time, scene: Scene, x_scene: Scene) -> None:
        self.bri_check          = bri_check
        self.min_light_level    = min_light_level
        self.motion_check       = motion_check
        self.wait_time          = wait_time
        self.scene              = scene
        self.x_scene            = x_scene
    


class Routine():

    def __init__(
        self,
        room: Room,
        daily_time: Daily_time,
        morning: Section_Routine,
        day: Section_Routine,
        afternoon: Section_Routine,
        night: Section_Routine,
        mod_morning=0,
        mod_day=0,
        mod_afternoon=0,
        mod_night=0,
        check_a=False,
        check_b=False,
    ):

        self.room = room
        self.daily_time = daily_time
        self.morning = morning
        self.day = day
        self.afternoon = afternoon
        self.night = night
        self.mod_morning = mod_morning
        self.mod_day = mod_day
        self.mod_afternoon = mod_afternoon
        self.mod_night = mod_night
        self.check_a = check_a
        self.check_b = check_b

    def run_routine(self):

        time_span = self.daily_time.get_time_span()

        if time_span == 1:  # Day
            
            if self.mod_day != 1:
                self.mod_day += 1
                self.mod_night = 0
                logging.info(f"Daymod\t\tDay\t\t{self.room.name_room}")
                if self.day.scene.bri == 0:
                    self.room.turn_off_groups()
                else:
                    self.room.turn_on_groups(self.day.scene)

            if self.day.bri_check is None or False:
                return
            else:
                print(self.check_a)
                self.check_a = self.room.sensor.turn_on_low_light(self.day.x_scene, self.day.min_light_level, self.room, self.check_a)
 

            if self.day.motion_check == None or self.day.motion_check == False:
                return
            else:
                self.room.sensor.turn_off_after_motion(self.day.x_scene, self.day.wait_time)

            




        elif time_span == 2:  # Morning
            
            if self.morning is None:
                return
            if self.mod_morning != 1:
                self.mod_morning += 1
                self.mod_afternoon = 0
                logging.info(f"Daymod\t\tMorning\t\t{self.room.name_room}")

                if self.morning.scene.bri == 0:
                    self.room.turn_off_groups()
                else:
                    self.room.turn_on_groups(self.morning.scene)

            if self.morning.bri_check:
                self.room.sensor.turn_off_after_motion(self.morning.scene, self.morning.wait_time)
            elif self.morning.bri_check is None:
                pass

            if self.morning.motion_check:
                pass
            elif self.morning.motion_check is None:
                pass
            
        elif time_span == 3:  # Afternoon
            
            if self.mod_afternoon != 1:
                self.mod_afternoon += 1
                self.mod_day = 0
                logging.info(f"Daymod\t\tAfternoon\t{self.room.name_room}")                
                
                if self.afternoon.bri == 0:
                    self.room.turn_off_groups()
                else:
                    self.room.turn_on_groups(self.afternoon.scene)

        elif time_span == 4:  # Night

            if self.mod_night != 1:  # one time
                self.mod_night += 1
                self.mod_morning = 0
                logging.info(f"Daymod\t\tNight\t\t{self.room.name_room}")
                
                if self.night.scene.bri == 0:
                    self.room.turn_off_groups()
                else:
                    self.room.turn_on_groups(self.night.scene)
        
        else:
            raise InvalidTimeSpanException(time_span)
