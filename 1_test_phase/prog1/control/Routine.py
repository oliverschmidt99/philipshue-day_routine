from control.huebridge import *
from control.Daily_time_span import *
from control.Room import *

import numpy as np


class Routine:

    def __init__(
        self,
        daily_time: Daily_time,  # Ein Objekt der Klasse Daily_time, das die Tageszeit verwaltet
        room: Room,  # Ein Objekt der Klasse Room, das einen Raum repräsentiert
        bri_morning,  # Helligkeitseinstellung für den Morgen
        bri_day,  # Helligkeitseinstellung für den Tag
        bri_afternoon,  # Helligkeitseinstellung für den Nachmittag
        bri_night,  # Helligkeitseinstellung für die Nacht
        mod_mornig,
        mod_day,
        mod_afternoon,
        mod_night,
    ):
        # Initialisierung der Instanzvariablen
        self.daily_time = daily_time
        self.room = room
        self.bri_day = bri_day
        self.bri_morning = bri_morning
        self.bri_afternoon = bri_afternoon
        self.bri_night = bri_night
        self.mod_mornig = mod_mornig
        self.mod_day = mod_day
        self.mod_afternoon = mod_afternoon
        self.mod_night = mod_night

    def adjust_lighting(self):
        # Bestimme die aktuelle Tageszeitspanne
        time_span = self.daily_time.get_time_span()

        # Passe die Beleuchtung basierend auf der aktuellen Tageszeit an
        if time_span == 1:
            if self.mod_day != 1:
                self.mod_day += 1
                self.mod_night = 0
                logging.info(f"Daymod\t\tDay\t\t{self.room.name_room}")
                self.mod = 2
                if self.bri_day == 0:
                    self.room.turn_off_groups()
                else:
                    self.room.turn_on_groups(self.bri_day, 10)

        elif time_span == 2:
            if self.mod_mornig != 1:
                self.mod_mornig += 1
                self.mod_afternoon = 0
                logging.info(f"Daymod\t\tMorning\t\t{self.room.name_room}")
                self.mod = 3
                if self.bri_morning == 0:
                    self.room.turn_off_groups()
                else:
                    self.room.turn_on_groups(self.bri_morning, 10)

        elif time_span == 3:
            if self.mod_afternoon != 1:
                self.mod_afternoon += 1
                self.mod_day = 0
                logging.info(f"Daymod\t\tAfternoon\t\t{self.room.name_room}")
                self.mod = 4
                if self.bri_afternoon == 0:
                    self.room.turn_off_groups()
                else:
                    self.room.turn_on_groups(self.bri_afternoon, 10)

        elif time_span == 4:
            if self.mod_night != 1:
                self.mod_night += 1
                self.mod_mornig = 0
                logging.info(f"Daymod\t\tNight\t\t{self.room.name_room}")
                self.mod = 1
                if self.bri_night == 0:
                    self.room.turn_off_groups()
                else:
                    self.room.turn_on_groups(self.bri_night, 10)
