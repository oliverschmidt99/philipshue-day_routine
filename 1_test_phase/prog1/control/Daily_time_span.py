from control.huebridge import *

import datetime
import ephem
import pytz
import numpy as np

sen = b.get_sensor_objects("name")
light_names = b.get_light_objects("name")
lights = b.lights


class Time_format:
    def __init__(self, H, M, S):
        self.H = H
        self.M = M
        self.S = S


class Daily_time(Time_format):

    def __init__(self, H1, M1, H2, M2):
        self.H1 = H1
        self.M1 = M1
        self.S1 = 0
        self.H2 = H2
        self.M2 = M2
        self.S2 = 0

    @staticmethod
    def sunrise():
        latitude = 53.595283
        longitude = 7.340012
        date = datetime.date.today()
        timezone = pytz.timezone("Europe/Berlin")
        obs = ephem.Observer()
        obs.lat = str(latitude)
        obs.lon = str(longitude)
        obs.date = date.strftime("%Y/%m/%d")
        sun = ephem.Sun()
        sunrise = obs.next_rising(sun)
        sunrise = pytz.utc.localize(sunrise.datetime()).astimezone(timezone)
        formatted_sunrise_time = sunrise.strftime("%H:%M:%S")
        return formatted_sunrise_time

    @staticmethod
    def sunset():
        latitude = 53.595283
        longitude = 7.340012
        date = datetime.date.today()
        timezone = pytz.timezone("Europe/Berlin")
        obs = ephem.Observer()
        obs.lat = str(latitude)
        obs.lon = str(longitude)
        obs.date = date.strftime("%Y/%m/%d")
        sun = ephem.Sun()
        sunset = obs.next_setting(sun)
        sunset = pytz.utc.localize(sunset.datetime()).astimezone(timezone)
        formatted_sunset_time = sunset.strftime("%H:%M:%S")
        return formatted_sunset_time

    def get_time_span(self):
        """get_time_span(self)

        returns
        :1 = Day
        :2 = Morning
        :3 = Afternoon
        :4 = Night
        """

        formatted_sunrise_time = Daily_time.sunrise()
        formatted_sunset_time = Daily_time.sunset()

        sunrise_time = datetime.datetime.strptime(
            formatted_sunrise_time, "%H:%M:%S"
        ).time()
        sunset_time = datetime.datetime.strptime(
            formatted_sunset_time, "%H:%M:%S"
        ).time()

        current_time = datetime.datetime.now().time()

        start_time = datetime.time(self.H1, self.M1, self.S1)
        end_time = datetime.time(self.H2, self.M2, self.S2)

        if sunrise_time < current_time < sunset_time:
            return 1
        else:
            if start_time < current_time <= sunrise_time:
                return 2
            elif sunset_time <= current_time < end_time:
                return 3
            else:
                return 3


class Daily_routine(Daily_time):

    def __init__(self, H1, M1, S1, H2, M2, S2):
        super().__init__(H1, M1, S1, H2, M2, S2)
