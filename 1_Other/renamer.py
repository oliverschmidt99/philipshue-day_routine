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
groups = b.get_group()


# Gruppeninformationen abrufen

# Ausgabe der Gruppennamen und IDs
for name, group_id in groups.items():
    print(f"Gruppenname: {name}, ID: {group_id}","\n")
