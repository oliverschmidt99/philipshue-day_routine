from phue import Bridge
import time
import datetime
import ephem
import pytz
import logging
import json
import os

BRIDGE_IP = "192.168.178.34"

b = Bridge(BRIDGE_IP)
b.connect()
b.get_api()

sen = b.get_sensor_objects("name")
light_names = b.get_light_objects("name")
lights = b.lights


Dummy = ["Elena/Deckelampe"]

aktueller_pfad = os.path.dirname(__file__)

# Dateinamen definieren
datei_zonen = "zonen.json"
datei_settings = "settings.json"
datei_log = "outside.log"

# Dateipfade erstellen
pfad_json_zonen = os.path.join(aktueller_pfad, datei_zonen)
pfad_json_settings = os.path.join(aktueller_pfad, datei_settings)
pfad_log = os.path.join(aktueller_pfad, datei_log)

logging.basicConfig(
    filename=pfad_log, level=logging.INFO, format="%(asctime)s %(message)s"
)


# Data structure to track lamp state and time last turned on
def initialize_lamp_states(zonen_states):
    lamp_states = {
        item["lamp"]: {
            "on": False,
            "last_turned_on_time": None,
            "brightness": None,
            "t_x": item.get("t_x", 0),
        }
        for item in zonen_states
    }
    return lamp_states


def open_json(pfad):
    with open(pfad, "r") as datei:
        daten = json.load(datei)
    return daten


# parameters: 'on' : True|False , 'bri' : 0-254, 'sat' : 0-254, 'ct': 154-500
def turn_on_lights(lights, bri, sat, ct):
    """Adjust properties of one or more lights.

    light_id can be a single lamp or an array of lamps
    parameters: 'bri' : 0-254, 'sat' : 0-254, 'ct': 154-500

    """
    for item in lights:
        lamp = item["lamp"]
        b.set_light(lamp, "on", True)
        if bri is not None:
            b.set_light(lamp, "bri", bri)
        if sat is not None:
            b.set_light(lamp, "sat", sat)
        if ct is not None:
            b.set_light(lamp, "ct", ct)


def turn_off_lights(lights):
    for item in lights:
        lamp = item["lamp"]
        b.set_light(lamp, "on", False)


def sunrise():
    # Geografische Koordinaten für den gewünschten Standort
    latitude = 53.595283
    longitude = 7.340012

    # Datum und Zeitzone für die Berechnung des Sonnenaufgangs
    date = datetime.date.today()
    timezone = pytz.timezone("Europe/Berlin")

    # Berechnung der Uhrzeit für den Sonnenaufgang
    obs = ephem.Observer()
    obs.lat = str(latitude)
    obs.lon = str(longitude)
    obs.date = date.strftime("%Y/%m/%d")
    sun = ephem.Sun()
    sunrise = obs.next_rising(sun)

    # Konvertierung des Sonnenaufgangs in die lokale Zeitzone
    sunrise = pytz.utc.localize(sunrise.datetime()).astimezone(timezone)

    # Formatierung des Sonnenaufgangs
    formatted_sunrise_time = sunrise.strftime("%H:%M:%S")
    return formatted_sunrise_time


def sunset():
    # Geografische Koordinaten für den gewünschten Standort
    latitude = 53.595283
    longitude = 7.340012

    # Datum und Zeitzone für die Berechnung des Sonnenuntergangs
    date = datetime.date.today()
    timezone = pytz.timezone("Europe/Berlin")

    # Berechnung der Uhrzeit für den Sonnenuntergang
    obs = ephem.Observer()
    obs.lat = str(latitude)
    obs.lon = str(longitude)
    obs.date = date.strftime("%Y/%m/%d")
    sun = ephem.Sun()
    sunset = obs.next_setting(sun)

    # Konvertierung der Sonnenuntergangszeit in die lokale Zeitzone
    sunset = pytz.utc.localize(sunset.datetime()).astimezone(timezone)

    # Formatierung der Sonnenuntergangszeit
    formatted_sunset_time = sunset.strftime("%H:%M:%S")
    return formatted_sunset_time


def check_lamp_state(lamp_array, lamp_states):
    current_datetime = datetime.datetime.now()
    true_lamps = []

    for item in lamp_array:
        lamp = item["lamp"]
        on_state = b.get_light(lamp, "on")

        if on_state:
            true_lamps.append(lamp)
            lamp_states[lamp]["on"] = True

            # Check if the lamp was turned on for the first time or turned back on
            if lamp_states[lamp]["last_turned_on_time"] is None:
                lamp_states[lamp]["last_turned_on_time"] = current_datetime

    for lamp in true_lamps:
        last_turned_on_time = lamp_states[lamp]["last_turned_on_time"]
        t_x = lamp_states[lamp]["t_x"]

        if (current_datetime - last_turned_on_time).total_seconds() > t_x:
            logging.info("Mode - Turn_off_light %s", lamp)
            b.set_light(lamp, "on", False)
            lamp_states[lamp]["on"] = False
            lamp_states[lamp]["last_turned_on_time"] = None


def coming_home():
    current_datetime = datetime.datetime.now()
    end_time = current_datetime + datetime.timedelta(seconds=5)

    on = b.get_light(Dummy[0], "on")
    b.set_light(Dummy[0], "on", False)

    if on:
        logging.info("Mode - Coming Home - On")

        while datetime.datetime.now() < end_time:
            # Turn on lights in zone_runway
            for item in zonen_json["zone_runway"]:
                lamp = item["lamp"]
                b.set_light(lamp, "on", True)
                b.set_light(lamp, "bri", 250)
                time.sleep(2)

        # After the delay, turn on lights in zone_cominghome
        turn_on_lights(zonen_json["zone_cominghome"], 180, None, None)
        time.sleep(180)
        logging.info("Mode - Coming Home - off")


zonen_json = open_json(pfad_json_zonen)


def main_function():
    logging.info("Restart\n")

    lamp_states_zone_daymode = initialize_lamp_states(zonen_json["zone_daymode"])
    lamp_states_zone_outside = initialize_lamp_states(zonen_json["zone_outside"])

    Morning = 0
    Day = 0
    Evening = 0
    Night = 0

    sunrise_time_deltatime = datetime.datetime.combine(
        datetime.datetime.today(), datetime.time()
    ).time()
    sunset_time_deltatime = datetime.datetime.combine(
        datetime.datetime.today(), datetime.time()
    ).time()
    
    while True:
        daten = open_json(pfad_json_settings)

        for time_entry in daten["time"]:
            # Extrahiere die Stunden, Minuten und Sekunden
            stunden = time_entry["H"]
            minuten = time_entry["M"]
            sekunden = time_entry["S"]

            # Setze die Variable entsprechend
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

        sunrise_time = datetime.datetime.strptime(
            formatted_sunrise_time, "%H:%M:%S"
        ).time()

        sunset_time = datetime.datetime.strptime(
            formatted_sunset_time, "%H:%M:%S"
        ).time()

        if sunrise_time < datetime.datetime.now().time() < sunset_time:
            if Day != 1:
                Day += 1
                Night = 0
                logging.info("Mode - Day")
                turn_off_lights(zonen_json["zone_daymode"])
                turn_off_lights(zonen_json["zone_outside"])
                turn_off_lights(zonen_json["zone_waylight"])

            check_lamp_state(zonen_json["zone_daymode"], lamp_states_zone_daymode)

        else:
            if sunrise_time_deltatime < datetime.datetime.now().time() <= sunrise_time:
                if Morning != 1:
                    Morning += 1
                    Evening = 0
                    logging.info("Mode - Morning")
                    turn_on_lights(zonen_json["outside"], 254, None, None)
                    turn_on_lights(zonen_json["zone_waylight"], 180, None, None)
                coming_home()

            elif sunset_time <= datetime.datetime.now().time() < sunset_time_deltatime:
                if Evening != 1:
                    Evening += 1
                    Day = 0
                    logging.info("Mode - Evening")
                    turn_on_lights(zonen_json["zone_outside"], 254, None, None)
                    turn_on_lights(zonen_json["zone_waylight"], 180, None, None)
                coming_home()
            else:
                if Night != 1:
                    Night += 1
                    Morning = 0
                    logging.info("Mode - Night")
                    turn_on_lights(zonen_json["zone_waylight"], 80, None, None)
                check_lamp_state(zonen_json["zone_outside"], lamp_states_zone_outside)
                coming_home()


if __name__ == "__main__":
    main_function()
