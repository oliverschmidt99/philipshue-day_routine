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
BRI_MAX = 240


if __name__ == "__main__":
    print("This program is running")
    logging.info("\nThis program is running\n")

    # define Scenes
    warm_max    = Scene(status=True, bri=BRI_MAX, sat=0, ct=500, t_time=100)
    warm_mid    = Scene(status=True, bri=BRI_MID, sat=0, ct=500, t_time=100)
    warm_low    = Scene(status=True, bri=BRI_LOW, sat=0, ct=500, t_time=100)

    cold_max    = Scene(status=True, bri=BRI_MAX, sat=0, ct=154, t_time=100)
    cold_mid    = Scene(status=True, bri=BRI_MID, sat=0, ct=154, t_time=100)
    cold_low    = Scene(status=True, bri=BRI_LOW, sat=0, ct=154, t_time=100)
    
    off         = Scene(status=False, bri=BRI_OFF, sat=0, ct=0, t_time=100)
    none        = Scene(status=None, bri=BRI_OFF, sat=0, ct=0, t_time=100)
  
    # define Rooms
    room_olli   = Room(group_ids=[1], switch_ids=[5, 99], sensor_id=2, name_room="room_olli")
    zone_outside = Room(group_ids=[24], switch_ids=[5, 99], sensor_id=194, name_room="zone_outside")
    zone_inside = Room(group_ids=[87], switch_ids=[5, 99], sensor_id=194, name_room="zone_inside") 
    
    # define Routines
    """
    rt_olli = Routine(room       =room_olli,
                daily_time =Daily_time(5, 0, 22,30),
                morning    =Section_Routine(bri_check=False,min_light_level=0,motion_check=False,wait_time=10,scene=none,x_scene=none),
                day        =Section_Routine(bri_check=True,min_light_level=20000,motion_check=False,wait_time=20,scene=off,x_scene=warm),
                afternoon  =Section_Routine(bri_check=False,min_light_level=0,motion_check=False,wait_time=10,scene=none,x_scene=none),
                night      =Section_Routine(bri_check=False,min_light_level=20000,motion_check=False,wait_time=10,scene=None,x_scene=warm),
                )
    """
                
    rt_outside = Routine(
                room       =zone_outside,
                daily_time =Daily_time(5, 30, 22,30),
                morning    =Section_Routine(bri_check=False,min_light_level=20000,motion_check=True,wait_time=240,scene=warm_mid,x_scene=warm_max),
                day        =Section_Routine(bri_check=True,min_light_level=25000,motion_check=False,wait_time=0,scene=off,x_scene=warm_mid),
                afternoon  =Section_Routine(bri_check=False,min_light_level=10000,motion_check=True,wait_time=240,scene=warm_mid,x_scene=warm_max),
                night      =Section_Routine(bri_check=False,min_light_level=20000,motion_check=True,wait_time=120,scene=off,x_scene=warm_mid),
                )
   
    rt_inside = Routine(
                room       =zone_inside,
                daily_time =Daily_time(5, 0, 23,0),
                morning    =Section_Routine(bri_check=False,min_light_level=20000,motion_check=False,wait_time=240,scene=warm_mid,x_scene=warm_max),
                day        =Section_Routine(bri_check=True,min_light_level=25000,motion_check=False,wait_time=0,scene=off,x_scene=warm_mid),
                afternoon  =Section_Routine(bri_check=False,min_light_level=10000,motion_check=False,wait_time=240,scene=warm_mid,x_scene=warm_max),
                night      =Section_Routine(bri_check=False,min_light_level=20000,motion_check=False,wait_time=120,scene=off,x_scene=warm_mid),
                )
   


    while True:

        rt_outside.run_routine()
        rt_inside.run_routine()


        time.sleep(2)
