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


class SectionRoutine:
    def __init__(
        self,
        bri_check: bool,
        max_light_level: float,
        motion_check: bool,
        wait_time: int,
        scene: Scene,
        x_scene: Scene,
        check_a: bool = False,
        check_b: bool = False,
    ) -> None:
        self.bri_check = bri_check
        self.max_light_level = max_light_level
        self.motion_check = motion_check
        self.wait_time = wait_time
        self.scene = scene
        self.x_scene = x_scene
        self.check_a = check_a
        self.check_b = check_b


class Routine:
    def __init__(
        self,
        room: Room,
        daily_time: Daily_time,
        morning: SectionRoutine,
        day: SectionRoutine,
        afternoon: SectionRoutine,
        night: SectionRoutine,
        mod_morning: int = 0,
        mod_day: int = 0,
        mod_afternoon: int = 0,
        mod_night: int = 0,
    ) -> None:
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

    def run_routine(self) -> None:
        time_span = self.daily_time.get_time_span()

        if time_span == 1:
            self._run_section(self.day, "Day", self.mod_day, "mod_day", "mod_night")
        elif time_span == 2:
            if self.morning:
                self._run_section(
                    self.morning,
                    "Morning",
                    self.mod_morning,
                    "mod_morning",
                    "mod_afternoon",
                )
        elif time_span == 3:
            self._run_section(
                self.afternoon,
                "Afternoon",
                self.mod_afternoon,
                "mod_afternoon",
                "mod_day",
            )
        elif time_span == 4:
            self._run_section(
                self.night, "Night", self.mod_night, "mod_night", "mod_morning"
            )
        else:
            raise InvalidTimeSpanException(time_span)

    def _run_section(
        self,
        section: SectionRoutine,
        period_name: str,
        mod_val: int,
        mod_attr: str,
        reset_attr: str,
    ) -> None:
        if mod_val != 1:
            setattr(self, mod_attr, 1)
            setattr(self, reset_attr, 0)
            logging.info(f"Daymod\t\t{period_name}\t\t{self.room.name_room}")
            self.room.turn_groups(status=None, scene=section.scene)

        if section.bri_check:
            section.check_a = self.room.sensor.turn_fade_on_light(
                scene=section.scene,
                x_scene=section.x_scene,
                max_light_level=section.max_light_level,
                check=section.check_a,
            )

        if section.motion_check:
            section.check_b = self.room.sensor.turn_off_after_motion(
                scene=section.scene,
                x_scene=section.x_scene,
                wait_time=section.wait_time,
                check=section.check_b,
            )
