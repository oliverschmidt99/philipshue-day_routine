import logging

from huebridge import *
from get_day_mode import *
from data_work import *
from get_day_mode import *
from lamp import *
from sensors import sensor
from phue import Bridge

sen = b.get_sensor_objects("name")
light_names = b.get_light_objects("name")
lights = b.lights

datei_zonen = "zonen.json"
datei_settings = "settings.json"
datei_log = "outside.log"
datei_sen = "sensor_config.json"

aktueller_pfad = os.path.dirname(__file__)
pfad_json_zonen = os.path.join(aktueller_pfad, datei_zonen)
pfad_json_settings = os.path.join(aktueller_pfad, datei_settings)
pfad_log = os.path.join(aktueller_pfad, datei_log)


def main_function():

    data = open_json(datei_sen)
    sensors = [sensors(0, 0, 0)]

    for sensor_data in data:
        sensors.append(sensor(sensor_data))

    test1 = sensors(1, 1, 1)
    test1.sensor_ip
    while True:
        sensor[1].turn_off_after_motion(100, 1)
        for sensor in sensors:
            sensor.turn_off_after_motion(100, 1)
        break

    day_mode = 0
    morning = 0
    day = 0
    evening = 0
    night = 0

    conf_sen = open_json(datei_sen)
    print(conf_sen)
    while True:

        day_mode = get_Day_mode()
        if day_mode == 1:
            if day != 1:
                day = Day(day)
                day += 1
                night = 0
                print("DAY")
            day = Day(day)

        if day_mode == 2:
            if morning != 1:
                morning = Morning(morning)
                morning += 1
                evening = 0
                print("MORNING")
            morning = Morning(morning)

        if day_mode == 3:
            if evening == 0:
                evening = Evening(evening)
                evening += 1
                day = 0
                print("EVENING")
            evening = Evening(evening)

        if day_mode == 4:
            if night != 1:
                night = Night(night)
                night += 1
                morning = 0
                print("NIGHT")
            night = Night(night)


if __name__ == "__main__":
    main_function()
