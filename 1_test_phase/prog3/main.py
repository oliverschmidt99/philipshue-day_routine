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
BRI_MAX = 254


if __name__ == "__main__":
    print("This program is running")
    logging.info("\nThis program is running\n")

    # define Scenes
    warm        = Scene(bri=BRI_MAX, sat=0, ct=500, t_time=0)
    cold        = Scene(bri=BRI_MAX, sat=0, ct=154, t_time=0)
    off         = Scene(bri=BRI_OFF, sat=0, ct=0, t_time=0)
  
    # define Rooms
    room_olli   = Room(group_ids=[1], switch_ids=[5, 99], sensor_id=2, name_room="room_olli")
    # define Routines

    rt = Routine(room       =room_olli,
                 daily_time =Daily_time(5, 0, 21,30),
                 morning    =Section_Routine(bri_check=True,min_light_level=20000,motion_check=False,wait_time=10,scene=cold,x_scene=warm),
                 day        =Section_Routine(bri_check=True,min_light_level=20000,motion_check=False,wait_time=10,scene=off,x_scene=warm),
                 afternoon  =Section_Routine(bri_check=True,min_light_level=20000,motion_check=False,wait_time=10,scene=off,x_scene=warm),
                 night      =Section_Routine(bri_check=True,min_light_level=20000,motion_check=False,wait_time=10,scene=off,x_scene=warm),
                )
   
   
    """

    
    zone_outside = Room(
        group_ids=[24], switch_ids=[5, 99], sensor_id=194, name_room="zone_outside"
    )
    zone_outside_rt = Routine(
        room=zone_outside,
        daily_time=Daily_time(5, 0, 21, 30),
        morning=Scene(bri=BRI_MAX, sat=250, ct=0, t_time=1000),
        day=Scene(bri=BRI_OFF, sat=0, ct=0, t_time=0),
        afternoon=Scene(bri=BRI_MAX, sat=0, ct=0, t_time=1000),
        night=Scene(bri=BRI_OFF, sat=0, ct=0, t_time=1000),
        bri_check=False,
    )  # rt -> routine

    zone_inside = Room(
        group_ids=[87], switch_ids=[5, 99], sensor_id=194, name_room="zone_inside"
    )
    zone_inside_rt = Routine(
        room=zone_inside,
        daily_time=Daily_time(5, 0, 22, 0),
        morning=Scene(bri=BRI_MID, sat=250, ct=300, t_time=10),
        day=Scene(bri=BRI_OFF, sat=0, ct=0, t_time=0),
        afternoon=Scene(bri=BRI_MAX, sat=250, ct=300, t_time=10),
        night=Scene(bri=BRI_LOW, sat=250, ct=300, t_time=10),
        bri_check=True,
    )  # rt -> routine
    """

    while True:

        rt.run_routine()

        time.sleep(2)
