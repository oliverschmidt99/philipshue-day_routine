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
    filename=pfad_log, level=logging.INFO, format="%(asctime)s | %(message)-10s")


# Const
BRI_OFF = 0
BRI_LOW = 75
BRI_MID = 120
BRI_MAX = 250


if __name__ == "__main__":
    print("This program is running")
    logging.info("\n\nThis program is running\n")


    # define Scenes
    warm_max    = Scene(status=True, bri=BRI_MAX, sat=150, ct=350, t_time=50)
    warm_mid    = Scene(status=True, bri=BRI_MID, sat=150, ct=350, t_time=50)
    warm_low    = Scene(status=True, bri=BRI_LOW, sat=150, ct=350, t_time=50)
    warm_very_low    = Scene(status=True, bri=30, sat=150, ct=500, t_time=20)


    cold_max    = Scene(status=True, bri=BRI_MAX, sat=0, ct=154, t_time=100)
    cold_mid    = Scene(status=True, bri=BRI_MID, sat=0, ct=154, t_time=100)
    cold_low    = Scene(status=True, bri=BRI_LOW, sat=0, ct=154, t_time=100)
    
    off         = Scene(status=False, bri=BRI_OFF, sat=0, ct=0, t_time=100)
  
    # define Rooms
    room_olli   = Room(group_ids=[89], switch_ids=[5, 99], sensor_id=2, name_room="room_olli")
    zone_outside = Room(group_ids=[24], switch_ids=[5, 99], sensor_id=190, name_room="zone_outside")
    zone_inside = Room(group_ids=[87], switch_ids=[5, 99], sensor_id=190, name_room="zone_inside") 
    
    # define Routines
    rt_olli = Routine(
                room       =room_olli,
                daily_time =Daily_time(7, 0, 23,0),
                morning    =SectionRoutine(bri_check=False,min_light_level=0,motion_check=False,wait_time=10,scene=off,x_scene=off),
                day        =SectionRoutine(bri_check=True,min_light_level=14000,motion_check=False,wait_time=5,scene=off,x_scene=warm_max),
                afternoon  =SectionRoutine(bri_check=False,min_light_level=14000,motion_check=False,wait_time=120,scene=off,x_scene=warm_mid),
                night      =SectionRoutine(bri_check=False,min_light_level=0,motion_check=True,wait_time=45,scene=off,x_scene=warm_very_low),
                )
                
    rt_outside = Routine(
                room       =zone_outside,
                daily_time =Daily_time(6, 30, 22,0),
                morning    =SectionRoutine(bri_check=False,min_light_level =20000,motion_check=True,wait_time=240,scene=warm_mid,x_scene=warm_max),
                day        =SectionRoutine(bri_check=True,min_light_level  =14000,motion_check=False,wait_time=0,scene=off,x_scene=warm_mid),
                afternoon  =SectionRoutine(bri_check=True,min_light_level =14000,motion_check=True,wait_time=240,scene=warm_mid,x_scene=warm_max),
                night      =SectionRoutine(bri_check=False,min_light_level =20000,motion_check=True,wait_time=120,scene=off,x_scene=warm_low),
                )
   
    rt_inside = Routine(
                room       =zone_inside,
                daily_time =Daily_time(6, 0, 22,30),
                morning    =SectionRoutine(bri_check=False,min_light_level=20000,motion_check=False,wait_time=240,scene=warm_mid,x_scene=warm_max),
                day        =SectionRoutine(bri_check=True,min_light_level=18000,motion_check=False,wait_time=0,scene=off,x_scene=warm_mid),
                afternoon  =SectionRoutine(bri_check=True,min_light_level=18000,motion_check=False,wait_time=240,scene=warm_mid,x_scene=warm_max),
                night      =SectionRoutine(bri_check=False,min_light_level=20000,motion_check=False,wait_time=120,scene=warm_low,x_scene=warm_mid),
                )
   


    while True:

        rt_olli.run_routine()
        rt_outside.run_routine()
        rt_inside.run_routine()

        time.sleep(1)
