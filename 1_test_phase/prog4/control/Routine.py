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
    def __init__(
            self, 
            bri_check,
            min_light_level,
            motion_check,
            wait_time,
            scene: Scene,
            x_scene: Scene,
            __check_a__ = False,
            __check_b__= False
        ) -> None:

        self.bri_check          = bri_check
        self.min_light_level    = min_light_level
        self.motion_check       = motion_check
        self.wait_time          = wait_time
        self.scene              = scene
        self.x_scene            = x_scene
        self.check_a            = __check_a__
        self.check_b            = __check_b__
    


class Routine():

    def __init__(
        self,
        room:               Room,
        daily_time:         Daily_time,
        morning:            Section_Routine,
        day:                Section_Routine,
        afternoon:          Section_Routine,
        night:              Section_Routine,
        __mod_morning__     = 0,
        __mod_day__         = 0,
        __mod_afternoon__   = 0,
        __mod_night__       = 0,
    ) -> None:

        self.room           = room
        self.daily_time     = daily_time
        self.morning        = morning
        self.day            = day
        self.afternoon      = afternoon
        self.night          = night
        self.mod_morning    = __mod_morning__
        self.mod_day        = __mod_day__
        self.mod_afternoon  = __mod_afternoon__
        self.mod_night      = __mod_night__

    def run_routine(self):

        time_span = self.daily_time.get_time_span()

        if time_span == 1:  # Day
            
            if self.mod_day != 1:
                self.mod_day += 1
                self.mod_night = 0
                logging.info(f"Daymod\t\tDay\t\t{self.room.name_room}")
                self.room.turn_groups(status=None, scene=self.day.scene)                
                
            if self.day.bri_check is (None or False):
                pass
            else:
                #print("run_routine", self.afternoon.check_a)
                self.day.check_a = self.room.sensor.turn_on_low_light(self.day.x_scene,self.day.scene, self.day.min_light_level, self.day.check_a)


            if self.day.motion_check is (None or False):
                pass
            else:
               self.day.check_b = self.room.sensor.turn_off_after_motion(self.day.x_scene,self.day.scene, self.day.wait_time, self.day.check_b)


           
        elif time_span == 2:  # Morning
            
            if self.morning is None:
                return
            if self.mod_morning != 1:
                self.mod_morning += 1
                self.mod_afternoon = 0
                logging.info(f"Daymod\t\tMorning\t\t{self.room.name_room}")
                self.room.turn_groups(status=None, scene=self.morning.scene)                
                
            if self.morning.bri_check is (None or False):
                pass
            else:
                #print("run_routine", self.afternoon.check_a)
                self.morning.check_a = self.room.sensor.turn_on_low_light(self.morning.x_scene,self.morning.scene, self.morning.min_light_level, self.morning.check_a)


            if self.morning.motion_check is (None or False):
                pass
            else:
               self.morning.check_b = self.room.sensor.turn_off_after_motion(self.morning.x_scene,self.morning.scene, self.morning.wait_time, self.morning.check_b)




        elif time_span == 3:  # Afternoon
            
            if self.mod_afternoon != 1:
                self.mod_afternoon += 1
                self.mod_day = 0
                logging.info(f"Daymod\t\tAfternoon\t{self.room.name_room}")
                self.room.turn_groups(status=None, scene=self.afternoon.scene)                
                
            if self.afternoon.bri_check is (None or False):
                pass
            else:
                #print("run_routine", self.afternoon.check_a)
                self.afternoon.check_a = self.room.sensor.turn_on_low_light(self.afternoon.x_scene,self.afternoon.scene, self.afternoon.min_light_level, self.afternoon.check_a)


            if self.afternoon.motion_check is (None or False):
                pass
            else:
               self.afternoon.check_b = self.room.sensor.turn_off_after_motion(self.afternoon.x_scene,self.afternoon.scene, self.afternoon.wait_time, self.afternoon.check_b)




        elif time_span == 4:  # Night

            if self.mod_night != 1:  # one time
                self.mod_night += 1
                self.mod_morning = 0
                logging.info(f"Daymod\t\tNight\t\t{self.room.name_room}")
                self.room.turn_groups(status=None, scene=self.night.scene)

            if self.night.bri_check is (None or False):
                pass
            else:
                #print("run_routine", self.afternoon.check_a)
                self.night.check_a = self.room.sensor.turn_on_low_light(self.night.x_scene,self.night.scene, self.night.min_light_level, self.night.check_a)


            if self.night.motion_check is (None or False):
                pass
            else:
               self.night.check_b = self.room.sensor.turn_off_after_motion(self.night.x_scene,self.night.scene, self.night.wait_time, self.night.check_b)


        
        else:
            raise InvalidTimeSpanException(time_span)
