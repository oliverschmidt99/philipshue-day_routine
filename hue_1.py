from phue import Bridge
from datetime import datetime, timedelta
import time
import datetime
import ephem
import pytz
import logging
import json

BRIDGE_IP = "192.168.178.34"

b = Bridge(BRIDGE_IP)
b.connect()
b.get_api()

sen = b.get_sensor_objects("name")
light_names = b.get_light_objects("name")
lights = b.lights


Pfad_json = "/home/oliver/Dokumente/autostart/zonen.json"
Pfad_log = "/home/oliver/Dokumente/autostart/outside.log"
# '/home/oliver/Desktop/autostart/outside.log'
# /home/olli/Schreibtisch/SAP/hue/daly/outside/outside.log
logging.basicConfig(
    filename=Pfad_log, level=logging.INFO, format="%(asctime)s %(message)s"
)


# Data structure to track lamp state and time last turned on
def initialize_lamp_states(zonen_states):
    lamp_states = {
        item["lamp"]: {"on": False, "last_turned_on_time": None, "brightness": None, "t_x": item.get("t_x", 0)}
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
            print(lamp, "1")
            b.set_light(lamp, "bri", bri)
        if sat is not None:
            print(lamp, "2")
            b.set_light(lamp, "sat", sat)
        if ct is not None:
            print(lamp, "3")
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
        on_state = b.get_light(lamp, 'on')

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
            print("Ich bin hier")
            b.set_light(lamp, 'on', False)
            lamp_states[lamp]["on"] = False
            lamp_states[lamp]["last_turned_on_time"] = None

    return true_lamps




def main_function():
    zonen_json = open_json(Pfad_json)
    logging.info("\nRestart")
    lamp_states = initialize_lamp_states(zonen_json["Olli"])
    Morning = 0
    Day = 0
    Afternoon = 0
    Night = 0
    while True:
        """
        formatted_sunrise_time = sunrise()
        formatted_sunset_time = sunset()
        deltatime = datetime.timedelta(hours=1)

        sunrise_time = datetime.datetime.strptime(formatted_sunrise_time, "%H:%M:%S").time()
        sunrise_time_deltatime = datetime.datetime.combine(datetime.datetime.today(), sunrise_time) - deltatime
        sunrise_time_deltatime = sunrise_time_deltatime.time()

        sunset_time = datetime.datetime.strptime(formatted_sunset_time, "%H:%M:%S").time()
        sunset_time_deltatime1 = datetime.datetime.combine(datetime.datetime.today(), sunset_time) + deltatime
        sunset_time_deltatime = sunset_time_deltatime.time()
        """
        # turn_on_lights(zonen_json["Olli"], 250, 100, 500)
        
        true_lamps = check_lamp_state(zonen_json["Olli"], lamp_states)

        time.sleep(2)
        print("True Lamps:", true_lamps)


if __name__ == "__main__":
    main_function()
