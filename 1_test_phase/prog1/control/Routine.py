from control.huebridge import *
from control.Daily_time_span import *
from control.Room import *

import numpy as np


class Routine:

    def __init__(
        self,
        room: Room,
        daily_time: Daily_time,
        morning: Scene,
        day: Scene,
        afternoon: Scene,
        night: Scene,
        mod_morning,
        mod_day,
        mod_afternoon,
        mod_night,
        bri_check,
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
        self.bri_check = bri_check

    def run_routine(self):

        time_span = self.daily_time.get_time_span()
        now_bri = self.room.brightness.get_brightness()

        print(now_bri)

        if time_span == 1:  # Day
            if self.bri_check and now_bri < 10000:
                print("1 1")
                if self.mod_day == 1:
                    print("1 2")
                    self.mod_day += 1
                    self.room.turn_on_groups(self.day)
            else:
                self.mod_day -= 2

            if self.mod_day != 1:
                print("2 1")
                self.mod_day += 1
                self.mod_night = 0
                logging.info(f"Daymod\t\tDay\t\t{self.room.name_room}")
                if self.day.bri == 0:
                    print("2 2")
                    self.room.turn_off_groups()
                else:
                    self.room.turn_on_groups(self.night)

        elif time_span == 2:
            if self.mod_morning != 1:
                self.mod_morning += 1
                self.mod_afternoon = 0
                logging.info(f"Daymod\t\tMorning\t\t{self.room.name_room}")

                if self.morning.bri == 0:
                    self.room.turn_off_groups()
                else:
                    self.room.turn_on_groups(self.morning)

        elif time_span == 3:
            if self.mod_afternoon != 1:
                self.mod_afternoon += 1
                self.mod_day = 0
                logging.info(f"Daymod\t\tAfternoon\t\t{self.room.name_room}")
                if self.afternoon.bri == 0:
                    self.room.turn_off_groups()
                else:
                    self.room.turn_on_groups(self.afternoon)

        elif time_span == 4:
            if self.mod_night != 1:
                self.mod_night += 1
                self.mod_morning = 0
                logging.info(f"Daymod\t\tNight\t\t{self.room.name_room}")
                if self.night.bri == 0:
                    self.room.turn_off_groups()
                else:
                    self.room.turn_on_groups(self.night)
