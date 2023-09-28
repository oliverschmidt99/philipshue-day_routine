
from phue import Bridge
import time
import datetime
import ephem
import pytz
import logging

BRIDGE_IP = "192.168.178.34"

b = Bridge(BRIDGE_IP)
b.connect()
b.get_api()

sen = b.get_sensor_objects("name")
light_names = b.get_light_objects("name")
lights = b.lights


Dummy = ["Elena/Deckelampe"
		]
Olli = [
        "Olli/Sony TV/Links/Hue Play",
        "Olli/Sony TV/Rechts/Hue Play",
        "Olli/Regal/Hue Go",
        "Olli/Schreibtisch/Hue Go",
        "Olli/Decke 1/Hue color"
        ]
outside = [
        "Draußen/Terrasse/Tür/Ost",
        "Draußen/Terrasse/L/Ost",
        "Draußen/Terrasse/R/Ost",
        "Draußen/Küche/L/Nord",
        "Draußen/Küche/R/Nord",
        "Draußen/Haustür/West",
        "Draußen/Carport/Vorne 1/",
        "Draußen/Carport/Vorne 2/",
        "Draußen/Auffahrt/Außen/1",
        "Draußen/Auffahrt/Außen/2",
        "Draußen/Auffahrt/Innen/1",
        "Draußen/Auffahrt/Innen/2",
        "Draußen/Auffahrt/Innen/3",
        "Draußen/Auffahrt/Innen/4"
        ]
zone_daymode = [
        "Draußen/Terrasse/Tür/Ost",
        "Draußen/Terrasse/L/Ost",
        "Draußen/Terrasse/R/Ost",
        "Draußen/Küche/L/Nord",
        "Draußen/Küche/R/Nord",
        "Draußen/Haustür/West",
        "Draußen/Carport/Vorne 1/",
        "Draußen/Carport/Vorne 2/",
        "Bibliothek/Hue white spot/R",
        "Bibliothek/Hue white spot/L",
        "Zwischenraum/Schrank/lightstrip",
        "Flur/Haustür/Tisch/Hue white",
        "Draußen/Auffahrt/Außen/1",
        "Draußen/Auffahrt/Außen/2",
        "Draußen/Auffahrt/Innen/1",
        "Draußen/Auffahrt/Innen/2",
        "Draußen/Auffahrt/Innen/3",
        "Draußen/Auffahrt/Innen/4"
        ]
zone_nightmode = [
        "Bibliothek/Hue white spot/R",
        "Bibliothek/Hue white spot/L",
        "Zwischenraum/Schrank/lightstrip",
        "Flur/Haustür/Tisch/Hue white",
        "Flur/Olli/Decke/"
        ]
zone_outside = [
        "Draußen/Terrasse/Tür/Ost",
        "Draußen/Terrasse/L/Ost",
        "Draußen/Terrasse/R/Ost",
        "Draußen/Küche/L/Nord",
        "Draußen/Küche/R/Nord",
        "Draußen/Haustür/West",
        "Draußen/Carport/Vorne 1/",
        "Draußen/Carport/Vorne 2/"
        ]
zone_runway = [
		"Draußen/Auffahrt/Innen/1",
		"Draußen/Auffahrt/Innen/2",
        "Draußen/Auffahrt/Außen/1",
        "Draußen/Auffahrt/Innen/3",
        "Draußen/Auffahrt/Außen/2",
        "Draußen/Auffahrt/Innen/4",
        "Draußen/Carport/Vorne 1/",
        "Draußen/Carport/Vorne 2/"
        ]
zone_cominghome = [
        "Draußen/Terrasse/Tür/Ost",
        "Draußen/Terrasse/L/Ost",
        "Draußen/Terrasse/R/Ost",
        "Draußen/Küche/L/Nord",
        "Draußen/Küche/R/Nord",
        "Draußen/Haustür/West",
        "Draußen/Carport/Vorne 1/",
        "Draußen/Carport/Vorne 2/",
        "Olli/Sony TV/Links/Hue Play",
        "Olli/Sony TV/Rechts/Hue Play"               
        ]
zone_waylight = [
		"Bibliothek/Hue white spot/R",
		"Bibliothek/Hue white spot/L",
		"Zwischenraum/Schrank/lightstrip",
		"Flur/Haustür/Tisch/Hue white"
		]



Pfad = '/home/olli/Schreibtisch/SAP/hue/daly/outside/outside.log'
#'/home/oliver/Desktop/autostart/outside.log'
#/home/olli/Schreibtisch/SAP/hue/daly/outside/outside.log
logging.basicConfig(filename=Pfad, level=logging.INFO, format='%(asctime)s %(message)s')


def sunrise():
    # Geografische Koordinaten für den gewünschten Standort
    latitude = 53.595283
    longitude = 7.340012

    # Datum und Zeitzone für die Berechnung des Sonnenaufgangs
    date = datetime.date.today()
    timezone = pytz.timezone('Europe/Berlin')

    # Berechnung der Uhrzeit für den Sonnenaufgang
    obs = ephem.Observer()
    obs.lat = str(latitude)
    obs.lon = str(longitude)
    obs.date = date.strftime('%Y/%m/%d')
    sun = ephem.Sun()
    sunrise = obs.next_rising(sun)

    # Konvertierung des Sonnenaufgangs in die lokale Zeitzone
    sunrise = pytz.utc.localize(sunrise.datetime()).astimezone(timezone)

    # Formatierung des Sonnenaufgangs
    formatted_sunrise_time = sunrise.strftime('%H:%M:%S')
    return formatted_sunrise_time



def sunset():
        # Geografische Koordinaten für den gewünschten Standort
        latitude = 53.595283
        longitude = 7.340012 

        # Datum und Zeitzone für die Berechnung des Sonnenuntergangs
        date = datetime.date.today()
        timezone = pytz.timezone('Europe/Berlin')

        # Berechnung der Uhrzeit für den Sonnenuntergang
        obs = ephem.Observer()
        obs.lat = str(latitude)
        obs.lon = str(longitude)
        obs.date = date.strftime('%Y/%m/%d')
        sun = ephem.Sun()
        sunset = obs.next_setting(sun)

        # Konvertierung der Sonnenuntergangszeit in die lokale Zeitzone
        sunset = pytz.utc.localize(sunset.datetime()).astimezone(timezone)

        # Formatierung der Sonnenuntergangszeit
        formatted_sunset_time = sunset.strftime('%H:%M:%S')
        return formatted_sunset_time


def main_function():
    
    logging.info("\nRestart")

    Morning = 0
    Day = 0
    Afternoon = 0
    Night = 0

    while True:

        formatted_sunrise_time = sunrise()
        formatted_sunset_time = sunset()
        deltatime = datetime.timedelta(hours=1)

        sunrise_time = datetime.datetime.strptime(formatted_sunrise_time, "%H:%M:%S").time()
        sunrise_time_deltatime = datetime.datetime.combine(datetime.datetime.today(), sunrise_time) - deltatime
        sunrise_time_deltatime = sunrise_time_deltatime.time()
        
        sunset_time = datetime.datetime.strptime(formatted_sunset_time, "%H:%M:%S").time()
        sunset_time_deltatime = datetime.datetime.combine(datetime.datetime.today(), sunset_time) + deltatime
        sunset_time_deltatime = sunset_time_deltatime.time()


        if sunrise_time < datetime.datetime.now().time() < sunset_time:

            if Day != 1:
                Day +=1
                Night = 0
                logging.info("Day - Mode") 

            for light in zone_daymode:
                b.set_light(light, 'on', False)

        else:


            if sunset_time <= datetime.datetime.now().time() < sunset_time_deltatime:

                if Afternoon != 1:
                    Afternoon +=1
                    Day = 0
                    logging.info("Evening - Mode")
                
                b.set_light(zone_waylight,'on', True)
                b.set_light(zone_outside,'on', True)
                b.set_light(zone_runway, 'on', True)

                b.set_light(zone_outside,'bri', 60)
                b.set_light(zone_waylight, 'bri', 50)
                b.set_light(zone_runway, 'bri', 20)

            elif sunrise_time_deltatime < datetime.datetime.now().time() <= sunrise_time:
                
                if Morning != 1:
                    Morning +=1
                    Afternoon = 0
                    logging.info("Morning - Mode")

                b.set_light(zone_waylight,'on', True)
                b.set_light(zone_outside,'on', True)
                b.set_light(zone_runway, 'on', True)

                b.set_light(zone_outside,'bri', 60)
                b.set_light(zone_waylight, 'bri', 50)
                b.set_light(zone_runway, 'bri', 20)

            else:
                
                if Night != 1:
                    Night +=1
                    Morning = 0
                    logging.info("Night - Mode")

                b.set_light(zone_outside,'on', False)
                b.set_light(zone_runway,'on', False)
                b.set_light(zone_waylight,'on', True)

                b.set_light(zone_waylight, 'bri', 20)
                

            on = b.get_light(Dummy[0], 'on')
            b.set_light(Dummy[0], 'on', False)

            if on == True:

                logging.info("Comminghome - Mode")
                time.sleep(18)
                for light in zone_runway:
                    light_names[light].on = True
                    light_names[light].brightness = 250
                    time.sleep(1)
                time.sleep(10)
                b.set_light(zone_cominghome,'on', True)
                b.set_light(zone_cominghome,'bri', 180)
                
                time.sleep(600)


main_function()
