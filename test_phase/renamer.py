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

# Holen Sie sich alle Sensordaten
sensors = b.get_sensor()

# Ausgabe der Sensor-IDs und Namen
for sensor_id, sensor_data in sensors.items():
    print(f"Sensor ID: {sensor_id}, Sensor Name: {sensor_data['name']}")
