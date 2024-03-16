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
    "Draußen/Auffahrt/Innen/1",
    "Draußen/Auffahrt/Innen/2",
    "Draußen/Auffahrt/Außen/1",
    "Draußen/Auffahrt/Innen/3",
    "Draußen/Auffahrt/Innen/4",
    "Draußen/Auffahrt/Außen/2",
    "Draußen/Carport/Vorne/1",
    "Draußen/Carport/Vorne/2",
    "Draußen/Carport/Hinten/1",
    "Draußen/Carport/Hinten/2",
}


def get_all_sensors_info():
    # Abrufen von Informationen über alle Sensoren
    all_sensors_info = b.get_sensor()
    
    # Ausgabe der erhaltenen Informationen für jeden Sensor
    for sensor_id, sensor_info in all_sensors_info.items():
        print(f"Sensor ID: {sensor_id}")
        print(f"Sensor ID: {sensor_info}")
        print()  # Leerzeile für bessere Lesbarkeit



def get_motion_sensor_brightness(sensor_id):
    # Abrufen der Helligkeit des Motion Sensors
    sensor_info = b.get_sensor(sensor_id)
    brightness = sensor_info['state']['lightlevel']
    
    return brightness


def get_motion_sensor_temperature(sensor_id):
    # Abrufen der Helligkeit des Motion Sensors
    sensor_info = b.get_sensor(sensor_id)
    temperature = sensor_info['state']['temperature']
    
    return temperature

sen_bri = 191  # Beispiel: ID 1 für den ersten Motion Sensor
sen_temp = 195
#while True:
#    brightness = get_motion_sensor_brightness(sen_bri)
#    temperature = get_motion_sensor_temperature(sen_temp)
#    
#    print("")
#    print(f"Aktuelle Helligkeit des Motion Sensors: {brightness}")
#    print(f"Aktuelle Temperatur des Motion Sensors: {temperature}")



# Aufruf der Funktion
get_all_sensors_info()

b.set_sensor(2, 'name', "Zimmer_Olli_Sen_motion")
b.set_sensor(3, 'name', "Zimmer_Olli_Sen_bri")
b.set_sensor(4, 'name', "Zimmer_Olli_Sen_temp")
#
#b.set_sensor(193, 'name', "Outdoor_Terrasse_Sen_motion")
#b.set_sensor(194, 'name', "Outdoor_Terrasse_Sen_bri")
#b.set_sensor(195, 'name', "Outdoor_Terrasse_Sen_temp")

