from phue import Bridge
import time
import datetime
import ephem
import pytz
import logging
import json
import os

from phue import Bridge

BRIDGE_IP = "192.168.178.42"

b = Bridge(BRIDGE_IP)
b.connect()
b.get_api()

sen = b.get_sensor_objects("name")
light_names = b.get_light_objects("name")
lights = b.lights

aktueller_pfad = os.path.dirname(__file__)

datei_zonen = "zonen.json"
datei_settings = "settings.json"
datei_log = "outside.log"

pfad_json_zonen = os.path.join(aktueller_pfad, datei_zonen)
pfad_json_settings = os.path.join(aktueller_pfad, datei_settings)
pfad_log = os.path.join(aktueller_pfad, datei_log)

logging.basicConfig(
    filename=pfad_log, level=logging.INFO, format="%(asctime)s %(message)s"
)

bri_very_bright = 254
bri_bright = 160
bri_half = 70
bri_low = 20
bri_very_low = 10


# Liste von Sensoren

Zimmer_Olli_Sen_motion = 2
Zimmer_Olli_Sen_bri = 3
Zimmer_Olli_Sen_temp = 4

Outdoor_Carport_Sen_motion = 190
Outdoor_Carport_Sen_bri = 191
Outdoor_Carport_Sen_temp = 192

Outdoor_Terrasse_Sen_motion = 193
Outdoor_Terrasse_Sen_bri = 194
Outdoor_Terrasse_Sen_temp = 195

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


def open_json(pfad):
    with open(pfad, "r") as datei:
        daten = json.load(datei)
    return daten


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


def turn_off_groups(group_ids):
    for group_id in group_ids:
        b.set_group(group_id, "on", False)
        print(f"Gruppe {group_id} wurde ausgeschaltet.")


def turn_on_groups(group_ids, brightness, t_time):
    for group_id in group_ids:
        b.set_group(group_id, "on", True)
        b.set_group(group_id, "bri", brightness, transitiontime=t_time)
        print(f"Gruppe {group_id} wurde eingeschaltet.")


def coming_home():
    current_datetime = datetime.datetime.now()
    end_time = current_datetime + datetime.timedelta(seconds=20)
    on = get_motion_sensor_status(Outdoor_Carport_Sen_motion)
    if on:
        logging.info("Mode - Coming Home - On")
        while datetime.datetime.now() < end_time:
            for lamp in zone_comminghome:
                b.set_light(lamp, "on", True)
                b.set_light(lamp, "bri", bri_very_bright)
                time.sleep(1)
        logging.info("Mode - Coming Home - off")
        return True


def get_motion_sensor_status(sensor_id):
    sensor_info = b.get_sensor(sensor_id)
    motion_detected = sensor_info["state"]["presence"]
    return motion_detected


def check_lamp_state(lamp_array, lamp_states):
    current_datetime = datetime.datetime.now()
    true_groups = []
    for item in lamp_array:
        group_id = item["group_id"]
        on_state = b.get_group(group_id, "on")
        if on_state:
            true_groups.append(group_id)
            lamp_states[group_id]["on"] = True
            if lamp_states[group_id]["last_turned_on_time"] is None:
                lamp_states[group_id]["last_turned_on_time"] = current_datetime
    for group_id in true_groups:
        last_turned_on_time = lamp_states[group_id]["last_turned_on_time"]
        t_x = lamp_states[group_id]["t_x"]
        if last_turned_on_time is not None:
            if (current_datetime - last_turned_on_time).total_seconds() > t_x:
                logging.info("Mode - Turn_off_light %s", group_id)
                b.set_group(group_id, "on", False)
                lamp_states[group_id]["on"] = False
                lamp_states[group_id]["last_turned_on_time"] = None
        else:
            logging.warning("Last turned on time is None for group %s", group_id)


def initialize_lamp_states(zonen_states):
    lamp_states = {
        item["group_id"]: {
            "on": False,
            "last_turned_on_time": None,
            "brightness": None,
            "t_x": item.get("t_x", 0),
        }
        for item in zonen_states
    }
    return lamp_states


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
    check_lamp_state(zonen_json["Zone_Flure"], lamp_states_Zone_Flure)
    check_lamp_state(zonen_json["Zone_Outdoor"], lamp_states_Zone_Outdoor)
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
    coming_home()

    montion = get_motion_sensor_status(Outdoor_Terrasse_Sen_motion)
    if montion == True:
        turn_on_groups(
            [
                zonen_json["Outdoor_Terrasse"][0]["group_id"],
                zonen_json["Outdoor_Kueche_Wand"][0]["group_id"],
            ],
            bri_very_bright,
            10,
        )
    return morning


def Evening(evening):
    turn_on_groups(
        [
            zonen_json["Zone_Outdoor"][0]["group_id"],
            zonen_json["Zone_Flure"][0]["group_id"],
        ],
        bri_half,
        100,
    )

    montion = get_motion_sensor_status(Outdoor_Terrasse_Sen_motion)
    if montion == True:
        turn_on_groups(
            [
                zonen_json["Outdoor_Terrasse"][0]["group_id"],
                zonen_json["Outdoor_Kueche_Wand"][0]["group_id"],
            ],
            bri_very_bright,
            10,
        )

    coming_home()
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

    montion = get_motion_sensor_status(Outdoor_Terrasse_Sen_motion)
    if montion == True:
        turn_on_groups(
            [
                zonen_json["Outdoor_Terrasse"][0]["group_id"],
                zonen_json["Outdoor_Kueche_Wand"][0]["group_id"],
            ],
            bri_very_bright,
            10,
        )

    coming_home()
    check_lamp_state(zonen_json["Zone_Flure"], lamp_states_Zone_Flure)
    check_lamp_state(zonen_json["Zone_Outdoor"], lamp_states_Zone_Outdoor)
    return night


def main_function():

    day_mode = 0
    morning = 0
    day = 0
    evening = 0
    night = 0

    while True:

        day_mode = get_Day_mode()
        if day_mode == 1:
            if day != 1:
                day = Day(day)
                day += 1
                night = 0
                logging.info("Mode - Day")
                print("DAY")
            day = Day(day)

        if day_mode == 2:
            if morning != 1:
                morning = Morning(morning)
                morning += 1
                evening = 0
                logging.info("Mode - Morning")
                print("MORNING")
            morning = Morning(morning)

        if day_mode == 3:
            if evening == 0:
                evening = Evening(evening)
                evening += 1
                day = 0
                logging.info("Mode - Evening")
                print("EVENING")
            evening = Evening(evening)

        if day_mode == 4:
            if night != 1:
                night = Night(night)
                night += 1
                morning = 0
                logging.info("Mode - Night")
                print("NIGHT")
            night = Night(night)


if __name__ == "__main__":
    zonen_json = open_json(pfad_json_zonen)
    lamp_states_Zone_Flure = initialize_lamp_states(zonen_json["Zone_Flure"])
    lamp_states_Zone_Outdoor = initialize_lamp_states(zonen_json["Zone_Outdoor"])
    main_function()
