from phue import Bridge
import time
import datetime
import ephem
import pytz
import logging
import json
import os

BRIDGE_IP = "192.168.178.42"

b = Bridge(BRIDGE_IP)
b.connect()
b.get_api()

sen = b.get_sensor_objects("name")
light_names = b.get_light_objects("name")
lights = b.lights


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


bri_very_bright = 254
bri_bright = 160
bri_half = 70
bri_low = 20
bri_very_low = 10


# Liste von den Zonen, Zimmern und Flure
Flur_Haustür = 7
Flur_Niko = 5
Flur_Olli = 8
Flur_Zwischenraum = 6
Outdoor_Auffahrt = 84
Outdoor_Eingangstür = 17
Outdoor_Kueche_Wand = 10
Outdoor_Terrasse = 12
Zimmer_Bibliothek = 81
Zimmer_Elena = 2
Zimmer_Laundry = 13
Zimmer_Niko = 3
Zimmer_Olli = 1
Zone_Auffahrt = 83
Zone_Flure = 82
Zone_Outdoor = 24
Zone_Treppenhaus_Olli_Niko = 85
Zone_Treppenhaus_Elena = 86
Zone_Night_Light = 87

zone_runway = {
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


def turn_off_groups(group_ids):
    for group_id in group_ids:
        # Schalte die Gruppe aus
        b.set_group(group_id, "on", False)
        print(f"Gruppe {group_id} wurde ausgeschaltet.")


def turn_on_groups(group_ids, brightness, t_time):
    for group_id in group_ids:
        # Schalte die Gruppe ein
        b.set_group(group_id, "on", True)
        b.set_group(group_id, "bri", brightness, transitiontime=t_time)
        print(f"Gruppe {group_id} wurde eingeschaltet.")


def get_motion_sensor_status(sensor_id):
    # Abrufen der Sensorinformationen
    sensor_info = b.get_sensor(sensor_id)

    # Überprüfen, ob Bewegung erkannt wurde
    motion_detected = sensor_info["state"]["presence"]

    return motion_detected


def coming_home():
    current_datetime = datetime.datetime.now()
    end_time = current_datetime + datetime.timedelta(seconds=5)

    on = get_motion_sensor_status(190)

    if on:
        logging.info("Mode - Coming Home - On")

        while datetime.datetime.now() < end_time:
            # Turn on lights in zone_runway
            for lamp in zone_runway:
                b.set_light(lamp, "on", True)
                b.set_light(lamp, "bri", bri_very_bright)
                time.sleep(1)
        time.sleep(180)
        return True


def main_function():
    logging.info("Restart\n")

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
                print("DAY")
                turn_off_groups(
                    [
                        Zone_Outdoor,
                        Zone_Flure,
                        Outdoor_Auffahrt,
                        Outdoor_Eingangstür,
                        Outdoor_Kueche_Wand,
                        Outdoor_Terrasse,
                    ]
                )

        else:
            if sunrise_time_deltatime < datetime.datetime.now().time() <= sunrise_time:
                if Morning != 1:
                    Morning += 1
                    Evening = 0
                    logging.info("Mode - Morning")
                    print("MORNING")
                    turn_on_groups(
                        [
                            Zone_Outdoor,
                            Zone_Flure,
                            Outdoor_Auffahrt,
                            Outdoor_Eingangstür,
                            Outdoor_Kueche_Wand,
                            Outdoor_Terrasse,
                        ],
                        bri_bright,
                        100,
                    )

                if coming_home() == True:
                    Morning = 0

            elif sunset_time <= datetime.datetime.now().time() < sunset_time_deltatime:
                if Evening != 1:
                    Evening += 1
                    Day = 0
                    logging.info("Mode - Evening")
                    print("EVENING")
                    turn_on_groups(
                        [
                            Zone_Outdoor,
                            Zone_Flure,
                            Outdoor_Auffahrt,
                            Outdoor_Eingangstür,
                            Outdoor_Kueche_Wand,
                            Outdoor_Terrasse,
                        ],
                        bri_half,
                        100,
                    )

                if coming_home() == True:
                    Evening = 0

            else:
                if Night != 1:
                    Night += 1
                    Morning = 0
                    logging.info("Mode - Night")
                    print("NIGHT")
                    turn_off_groups(
                        [
                            Zone_Outdoor,
                            Zone_Flure,
                            Outdoor_Auffahrt,
                            Outdoor_Eingangstür,
                            Outdoor_Kueche_Wand,
                            Outdoor_Terrasse,
                        ]
                    )
                    turn_on_groups([Zone_Night_Light], bri_low, 200)

                if coming_home() == True:
                    Night = 0


if __name__ == "__main__":
    main_function()
