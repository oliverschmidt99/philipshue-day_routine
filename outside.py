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


Dummy = ["Elena/Deckelampe"]
Olli = [
    {"lamp": "Olli/Sony TV/Links/Hue Play", "t_x":  120},
    {"lamp": "Olli/Sony TV/Rechts/Hue Play", "t_x": 120},
    {"lamp": "Olli/Regal/Hue Go", "t_x":            120},
    {"lamp": "Olli/Schreibtisch/Hue Go", "t_x": 120},
    {"lamp": "Olli/Decke 1/Hue color", "t_x": 120}
]
outside = [
    {"lamp": "Draußen/Terrasse/Tür/Ost", "t_x": 120},
    {"lamp": "Draußen/Terrasse/L/Ost", "t_x": 120},
    {"lamp": "Draußen/Terrasse/R/Ost", "t_x": 120},
    {"lamp": "Draußen/Küche/L/Nord", "t_x": 120},
    {"lamp": "Draußen/Küche/R/Nord", "t_x": 120},
    {"lamp": "Draußen/Haustür/West", "t_x": 120},
    {"lamp": "Draußen/Carport/Vorne 1/", "t_x": 120},
    {"lamp": "Draußen/Carport/Vorne 2/", "t_x": 120},
    {"lamp": "Draußen/Auffahrt/Außen/1", "t_x": 120},
    {"lamp": "Draußen/Auffahrt/Außen/2", "t_x": 120},
    {"lamp": "Draußen/Auffahrt/Innen/1", "t_x": 120},
    {"lamp": "Draußen/Auffahrt/Innen/2", "t_x": 120},
    {"lamp": "Draußen/Auffahrt/Innen/3", "t_x": 120},
    {"lamp": "Draußen/Auffahrt/Innen/4", "t_x": 120}
]
zone_daymode = [
    {"lamp": "Draußen/Terrasse/Tür/Ost", "t_x": 120},
    {"lamp": "Draußen/Terrasse/L/Ost", "t_x": 120},
    {"lamp": "Draußen/Terrasse/R/Ost", "t_x": 120},
    {"lamp": "Draußen/Küche/L/Nord", "t_x": 120},
    {"lamp": "Draußen/Küche/R/Nord", "t_x": 120},
    {"lamp": "Draußen/Haustür/West", "t_x": 120},
    {"lamp": "Draußen/Carport/Vorne 1/", "t_x": 120},
    {"lamp": "Draußen/Carport/Vorne 2/", "t_x": 120},
    {"lamp": "Bibliothek/Hue white spot/R", "t_x": 120},
    {"lamp": "Bibliothek/Hue white spot/L", "t_x": 120},
    {"lamp": "Zwischenraum/Schrank/lightstrip", "t_x": 120},
    {"lamp": "Flur/Haustür/Tisch/Hue white", "t_x": 120},
    {"lamp": "Draußen/Auffahrt/Außen/1", "t_x": 120},
    {"lamp": "Draußen/Auffahrt/Außen/2", "t_x": 120},
    {"lamp": "Draußen/Auffahrt/Innen/1", "t_x": 120},
    {"lamp": "Draußen/Auffahrt/Innen/2", "t_x": 120},
    {"lamp": "Draußen/Auffahrt/Innen/3", "t_x": 120},
    {"lamp": "Draußen/Auffahrt/Innen/4", "t_x": 120}
]
zone_outside = [
    {"lamp": "Draußen/Terrasse/Tür/Ost", "t_x": 120},
    {"lamp": "Draußen/Terrasse/L/Ost", "t_x": 120},
    {"lamp": "Draußen/Terrasse/R/Ost", "t_x": 120},
    {"lamp": "Draußen/Küche/L/Nord", "t_x": 120},
    {"lamp": "Draußen/Küche/R/Nord", "t_x": 120},
    {"lamp": "Draußen/Haustür/West", "t_x": 120},
    {"lamp": "Draußen/Carport/Vorne 1/", "t_x": 120},
    {"lamp": "Draußen/Carport/Vorne 2/", "t_x": 120}
]
zone_runway = [
    {"lamp": "Draußen/Auffahrt/Innen/1", "t_x": 120},
    {"lamp": "Draußen/Auffahrt/Innen/2", "t_x": 120},
    {"lamp": "Draußen/Auffahrt/Außen/1", "t_x": 120},
    {"lamp": "Draußen/Auffahrt/Innen/3", "t_x": 120},
    {"lamp": "Draußen/Auffahrt/Außen/2", "t_x": 120},
    {"lamp": "Draußen/Auffahrt/Innen/4", "t_x": 120},
    {"lamp": "Draußen/Carport/Vorne 1/", "t_x": 120},
    {"lamp": "Draußen/Carport/Vorne 2/", "t_x": 120}
]
zone_cominghome = [
    {"lamp": "Draußen/Terrasse/Tür/Ost", "t_x": 120},
    {"lamp": "Draußen/Terrasse/L/Ost", "t_x": 120},
    {"lamp": "Draußen/Terrasse/R/Ost", "t_x": 120},
    {"lamp": "Draußen/Küche/L/Nord", "t_x": 120},
    {"lamp": "Draußen/Küche/R/Nord", "t_x": 120},
    {"lamp": "Draußen/Haustür/West", "t_x": 120},
    {"lamp": "Draußen/Carport/Vorne 1/", "t_x": 120},
    {"lamp": "Draußen/Carport/Vorne 2/", "t_x": 120},
    {"lamp": "Olli/Sony TV/Links/Hue Play", "t_x": 120},
    {"lamp": "Olli/Sony TV/Rechts/Hue Play", "t_x": 120}
]
zone_waylight = [
    {"lamp": "Bibliothek/Hue white spot/R", "t_x": 120},
    {"lamp": "Bibliothek/Hue white spot/L", "t_x": 120},
    {"lamp": "Zwischenraum/Schrank/lightstrip", "t_x": 120},
    {"lamp": "Flur/Haustür/Tisch/Hue white", "t_x": 120}
]
zone_nightmode = [
    {"lamp": "Bibliothek/Hue white spot/R", "t_x": 12},
    {"lamp": "Bibliothek/Hue white spot/L", "t_x": 12},
    {"lamp": "Zwischenraum/Schrank/lightstrip", "t_x": 12},
    {"lamp": "Flur/Haustür/Tisch/Hue white", "t_x": 12},
    {"lamp": "Flur/Olli/Decke/", "t_x": 12}
]


lamp_states = {}
for item in zone_daymode + zone_outside + zone_runway + zone_cominghome + zone_waylight + zone_nightmode + Olli:
    lamp_states[item["lamp"]] = {"on": False, "last_turned_on_time": None, "brightness": None}

Pfad = '/home/oliver/Dokumente/autostart/outside.log'
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


def check_lamp_state(lamp_array):
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
        t_x = [item["t_x"] for item in lamp_array if item["lamp"] == lamp]

        if t_x:
            t_x = t_x[0]
            if (current_datetime - last_turned_on_time).total_seconds() > t_x:
                b.set_light(lamp, 'on', False)
                lamp_states[lamp]["on"] = False
                lamp_states[lamp]["last_turned_on_time"] = None
    #return true_lamps


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

            check_lamp_state(zone_daymode)
            

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

                for lamp in zone_waylight:
                    b.set_light(lamp,'on', True)
                    b.set_light(lamp, 'bri', 60)
                for lamp in zone_outside:
                    b.set_light(lamp,'on', True)
                    b.set_light(lamp, 'bri', 50)
                for lamp in zone_runway:
                    b.set_light(lamp,'on', True)
                    b.set_light(lamp, 'bri', 20)
            else:
                
                if Night != 1:
                    Night +=1
                    Morning = 0
                    logging.info("Night - Mode")

                check_lamp_state(zone_outside)
                check_lamp_state(zone_runway)

                for lamp in zone_waylight:
                    b.set_light(lamp,'on', True)
                    b.set_light(lamp, 'bri', 20)
                

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


if __name__ == "__main__":
    main_function()
