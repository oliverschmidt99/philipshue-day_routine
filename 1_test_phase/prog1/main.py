from control.huebridge import *
from control.Daily_time_span import *
from control.Room import *
from control.Routine import *

import numpy as np
import time
import logging
import os


aktueller_pfad = os.path.dirname(__file__)
datei_log = "info.log"
pfad_log = os.path.join(aktueller_pfad, datei_log)
logging.basicConfig(
    filename=pfad_log, level=logging.INFO, format="%(asctime)s %(message)s"
)

# Const
BRI_OFF = 0
BRI_LOW = 50
BRI_MID = 150
BRI_MAX = 255


if __name__ == "__main__":
    print("This program is running")
    logging.info("\nThis program is running\n")

    room_olli = Room(
        group_ids=[1], switch_ids=[5, 99], sensor_id=2, name_room="room_olli"
    )

    olli = Routine(
        daily_time=Daily_time(8, 0, 22, 0),
        room=room_olli,
        bri_afternoon=BRI_MAX,
        bri_day=BRI_MAX,
        bri_morning=BRI_MAX,
        bri_night=BRI_MID,
        mod_afternoon=0,
        mod_day=0,
        mod_mornig=0,
        mod_night=0,
    )

    """
    zone_outside = Room([24], None, [190, 193], "zone_outside")
    zone_outside_ts = Daily_time(6, 0, 23, 30)  # ts -> time span;
    zone_outside_rt = Routine(
        daily_time=zone_outside_ts,
        room=zone_outside,
        bri_morning=BRI_MAX,
        bri_day=BRI_OFF,
        bri_afternoon=BRI_MAX,
        bri_night=BRI_LOW,
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
        bri_afternoon=BRI_MAX,
        bri_night=BRI_LOW,
        mod_mornig=0,
        mod_day=0,
        mod_afternoon=0,
        mod_night=0,
    )  # rt -> routine
    """
    while True:

        olli.adjust_lighting()

        a = room_olli.temperature.get_temperature()
        print(a)
        b = room_olli.brightness.get_brightness()
        print(b)
        c = room_olli.motion.get_motion()
        print(c)
        time.sleep(2)
