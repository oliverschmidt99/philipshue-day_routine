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

class Section_Routine:
    def __init__(
            self,
            bri_check,
            min_light_level,
            motion_check,
            wait_time,
            scene: Scene,
            x_scene: Scene,
            __check_a__=False,
            __check_b__=False
    ) -> None:
        self.bri_check = bri_check
        self.min_light_level = min_light_level
        self.motion_check = motion_check
        self.wait_time = wait_time
        self.scene = scene
        self.x_scene = x_scene
        self.check_a = __check_a__
        self.check_b = __check_b__

class Routine:
    def __init__(
        self,
        room: Room,
        daily_time: Daily_time,
        morning: Section_Routine,
        day: Section_Routine,
        afternoon: Section_Routine,
        night: Section_Routine,
        __mod_morning__=0,
        __mod_day__=0,
        __mod_afternoon__=0,
        __mod_night__=0,
    ) -> None:
        self.room = room
        self.daily_time = daily_time
        self.morning = morning
        self.day = day
        self.afternoon = afternoon
        self.night = night
        self.last_time_span = None
        self.mod_morning = __mod_morning__
        self.mod_day = __mod_day__
        self.mod_afternoon = __mod_afternoon__
        self.mod_night = __mod_night__

    def run_routine(self):
        try:
            time_span = self.daily_time.get_time_span()
            
            # Fortfahren nur, wenn sich der time_span geändert hat
            if time_span != self.last_time_span:
                routine_section = self.get_routine_section(time_span)
                
                if routine_section is None:
                    return

                # Einmalige Logik für den Übergang zu einem neuen Tagesabschnitt
                if routine_section['mod'] == 0:
                    routine_section['mod'] += 1
                    self.reset_other_mods(time_span)
                    logging.info(f"Daymod\t\t{routine_section['name']}\t\t{self.room.name_room}")
                    self.room.turn_groups(status=None, scene=routine_section['section'].scene)
                
                # Helligkeitsprüfung und Bewegungserkennung
                self.handle_brightness_check(routine_section['section'])
                self.handle_motion_check(routine_section['section'])

                # Aktualisieren des letzten time_span
                self.last_time_span = time_span

        except Exception as e:
            logging.error(f"Error in run_routine: {e}")

    def get_routine_section(self, time_span):
        if time_span == 1:
            return {'name': 'Day', 'mod': self.mod_day, 'section': self.day}
        elif time_span == 2:
            return {'name': 'Morning', 'mod': self.mod_morning, 'section': self.morning}
        elif time_span == 3:
            return {'name': 'Afternoon', 'mod': self.mod_afternoon, 'section': self.afternoon}
        elif time_span == 4:
            return {'name': 'Night', 'mod': self.mod_night, 'section': self.night}
        else:
            raise InvalidTimeSpanException(time_span)

    def reset_other_mods(self, current_time_span):
        if current_time_span == 1:
            self.mod_night = 0
        elif current_time_span == 2:
            self.mod_afternoon = 0
        elif current_time_span == 3:
            self.mod_day = 0
        elif current_time_span == 4:
            self.mod_morning = 0

    def handle_brightness_check(self, section):
        if section.bri_check:
            section.check_a = self.room.sensor.turn_on_low_light(
                section.scene, section.x_scene, section.min_light_level, section.check_a
            )

    def handle_motion_check(self, section):
        if section.motion_check:
            section.check_b = self.room.sensor.turn_off_after_motion(
                section.scene, section.x_scene, section.wait_time, section.check_b
            )
