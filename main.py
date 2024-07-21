from control.huebridge import *
from control.Daily_time_span import *
from control.Room import *
from control.Routine import *

import numpy as np
import time
import logging
import os

sen = b.get_sensor_objects("name")
light_names = b.get_light_objects("name")
lights = b.lights


aktueller_pfad = os.path.dirname(__file__)
datei_log = "info.log"
pfad_log = os.path.join(aktueller_pfad, datei_log)
logging.basicConfig(
    filename=pfad_log, level=logging.INFO, format="%(asctime)s %(message)s"
)

# Const
BRI_OFF = 0
BRI_LOW = 50
BRI_MID = 100
BRI_MAX = 255


if __name__ == "__main__":
    print("This program is running")
    logging.info("\nThis program is running\n")

    # room_olli = Room([1], [5, 99], [2, 3, 4])
    # room_olli_daytime = Daily_time(8, 0, 0, 22, 0, 0)
    # routine_olli = Routine(room_olli_daytime, room_olli, 50, 100, 100, 200)

    zone_outside = Room([24], None, [190, 193], "zone_outside")
    zone_outside_ts = Daily_time(6, 0, 23, 0)  # ts -> time span;
    zone_outside_rt = Routine(
        daily_time=zone_outside_ts,
        room=zone_outside,
        bri_morning=BRI_MAX,
        bri_day=BRI_OFF,
        bri_afternoon=BRI_MAX,
        bri_night=BRI_OFF,
        mod_mornig=0,
        mod_day=0,
        mod_afternoon=0,
        mod_night=0,
    )  # rt -> routine

    zone_inside = Room([87], None, None, "zone_inside")
    zone_inside_ts = Daily_time(5, 30, 23, 30)  # ts -> time span;
    zone_inside_rt = Routine(
        daily_time=zone_inside_ts,
        room=zone_inside,
        bri_morning=BRI_MAX,
        bri_day=BRI_OFF,
        bri_afternoon=BRI_MID,
        bri_night=BRI_LOW,
        mod_mornig=0,
        mod_day=0,
        mod_afternoon=0,
        mod_night=0,
    )  # rt -> routine

    while True:
        time.sleep(0.5)
        zone_outside_rt.adjust_lighting()
        zone_inside_rt.adjust_lighting()
