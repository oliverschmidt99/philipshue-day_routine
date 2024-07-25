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



    """
    olli = Routine(
        room=room_olli,
        daily_time=Daily_time(6, 0, 19, 0),
        morning=Scene(bri=200, sat=250, ct=400, t_time=10),
        day=Scene(bri=0, sat=0, ct=0, t_time=0),
        afternoon=Scene(bri=254, sat=250, ct=300, t_time=10),
        night=Scene(bri=100, sat=250, ct=500, t_time=10),
        mod_morning=0,
        mod_day=0,
        mod_afternoon=0,
        mod_night=0,
        bri_check=True,
    )
    """
    

    
    zone_outside = Room(
        group_ids=[1], switch_ids=[5, 99], sensor_id=194, name_room="zone_outside"
    )
    zone_outside_rt = Routine(
        room=zone_outside,
        daily_time=Daily_time(5, 0, 21, 30),
        morning=Scene(bri=BRI_MAX, sat=250, ct=0, t_time=1000),
        day=Scene(bri=BRI_OFF, sat=0, ct=0, t_time=0),
        afternoon=Scene(bri=BRI_MAX, sat=0, ct=0, t_time=1000),
        night=Scene(bri=BRI_OFF, sat=0, ct=0, t_time=1000),
        mod_morning=0,
        mod_day=0,
        mod_afternoon=0,
        mod_night=0,
        bri_check=False,
    )  # rt -> routine

    zone_inside = Room(
        group_ids=[87], switch_ids=[5, 99], sensor_id=190, name_room="zone_inside"
    )
    zone_inside_rt = Routine(
        room=zone_inside,
        daily_time=Daily_time(5, 0, 22, 0),
        morning=Scene(bri=BRI_MID, sat=250, ct=300, t_time=10),
        day=Scene(bri=BRI_OFF, sat=0, ct=0, t_time=0),
        afternoon=Scene(bri=BRI_MAX, sat=250, ct=300, t_time=10),
        night=Scene(bri=BRI_LOW, sat=250, ct=300, t_time=10),
        mod_morning=0,
        mod_day=0,
        mod_afternoon=0,
        mod_night=0,
        bri_check=True,
    )  # rt -> routine
    

    while True:

        zone_outside_rt.run_routine()
        zone_inside_rt.run_routine()

        

        time.sleep(2)
