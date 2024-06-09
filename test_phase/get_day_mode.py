import datetime
import ephem
import pytz

from sensors import sensor


from huebridge import *
from lamp import *
from data_work import *
from sensors import *


bri_very_bright = 254
bri_bright = 160
bri_half = 70
bri_low = 20
bri_very_low = 10


zonen_json = open_json(pfad_json_zonen)

zone_comminghome = {
    "Draußen/Auffahrt/Innen/1",
    "Draußen/Auffahrt/Außen/1",
    "Draußen/Auffahrt/Innen/2",
    "Draußen/Auffahrt/Außen/2",
    "Draußen/Auffahrt/Innen/3",
    "Draußen/Auffahrt/Innen/4",
    "Draußen/Carport/Vorne/1",
    "Draußen/Carport/Vorne/2",
    "Draußen/Carport/Hinten/1",
    "Draußen/Carport/Hinten/2",
}


sen_carport = sensor(2, [8], 120)


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


def get_Day_mode():

    daten = open_json(pfad_json_settings)
    sunrise_time_deltatime = datetime.datetime.combine(
        datetime.datetime.today(), datetime.time()
    ).time()
    sunset_time_deltatime = datetime.datetime.combine(
        datetime.datetime.today(), datetime.time()
    ).time()

    for time_entry in daten["time"]:
        stunden = time_entry["H"]
        minuten = time_entry["M"]
        sekunden = time_entry["S"]
        var_name = time_entry["var"]

        if "sunrise_time_" in var_name:
            sunrise_time_deltatime = datetime.datetime.combine(
                datetime.datetime.today(), datetime.time(stunden, minuten, sekunden)
            ).time()
        elif "sunset_time_" in var_name:
            sunset_time_deltatime = datetime.datetime.combine(
                datetime.datetime.today(), datetime.time(stunden, minuten, sekunden)
            ).time()

    formatted_sunrise_time = sunrise()
    formatted_sunset_time = sunset()

    sunrise_time = datetime.datetime.strptime(formatted_sunrise_time, "%H:%M:%S").time()
    sunset_time = datetime.datetime.strptime(formatted_sunset_time, "%H:%M:%S").time()

    if sunrise_time < datetime.datetime.now().time() < sunset_time:
        return 1
    else:
        if sunrise_time_deltatime < datetime.datetime.now().time() <= sunrise_time:
            return 2
        elif sunset_time <= datetime.datetime.now().time() < sunset_time_deltatime:
            return 3
        else:
            return 3


def Day(day):

    if day != 1:
        turn_off_groups(
            [
                zonen_json["Zone_Outdoor"][0]["group_id"],
                zonen_json["Zone_Flure"][0]["group_id"],
            ]
        )

    return day


def Morning(morning):
    turn_on_groups(
        [
            zonen_json["Zone_Outdoor"][0]["group_id"],
            zonen_json["Zone_Flure"][0]["group_id"],
        ],
        bri_bright,
        100,
    )

    return morning


def Evening(evening):

    # print(sen_carport.get_motion_sensor_status())
    sen_carport.turn_off_after_motion(250, 20)

    turn_on_groups(
        [
            zonen_json["Zone_Outdoor"][0]["group_id"],
            zonen_json["Zone_Flure"][0]["group_id"],
        ],
        bri_half,
        100,
    )

    return evening


def Night(night):
    turn_off_groups(
        [
            zonen_json["Zone_Outdoor"][0]["group_id"],
            zonen_json["Zone_Flure"][0]["group_id"],
        ]
    )
    turn_on_groups(
        [zonen_json["Zone_Night_Light"][0]["group_id"]],
        bri_very_low,
        200,
    )
