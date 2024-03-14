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


zone_runway = {
    'Draußen/Auffahrt/Innen/1',
    'Draußen/Auffahrt/Innen/2',
    'Draußen/Auffahrt/Außen/1',
    'Draußen/Auffahrt/Innen/3',
    'Draußen/Auffahrt/Innen/4',
    'Draußen/Auffahrt/Außen/2',
    'Draußen/Carport/Vorne/1',
    'Draußen/Carport/Vorne/2',
    'Draußen/Carport/Hinten/1',
    'Draußen/Carport/Hinten/2',
}


def coming_home():
    current_datetime = datetime.datetime.now()
    end_time = current_datetime + datetime.timedelta(seconds=5)

    on = get_motion_sensor_status(193)

    if on:
        logging.info("Mode - Coming Home - On")

        while datetime.datetime.now() < end_time:
            # Turn on lights in zone_runway
            for lamp in zone_runway:
                b.set_light(lamp, "on", True)
                b.set_light(lamp, "bri", 250)
                time.sleep(2)


def get_motion_sensor_status(sensor_id):
    # Abrufen der Sensorinformationen
    sensor_info = b.get_sensor(sensor_id)
    
    # Überprüfen, ob Bewegung erkannt wurde
    motion_detected = sensor_info['state']['presence']
    
    return motion_detected

groups = b.get_group()

# Drucke die Namen aller Gruppen
for group_id, group_info in groups.items():
    print("Gruppen-ID:", group_id)
    print("Gruppenname:", group_info["name"])
    print()

# Beispielaufruf der Funktion für den ersten Motion Sensor
motion_sensor_id = 193  # Beispiel: ID 1 für den ersten Motion Sensor
while True:
    coming_home()
    motion_detected = get_motion_sensor_status(motion_sensor_id)
    print(f"Bewegung erkannt: {motion_detected}")
    time.sleep(1)




