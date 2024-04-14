from huebridge import *
import time
from lamp import turn_on_groups, turn_off_groups
import datetime
from data_work import open_json


def get_motion_sensor_status(sensor_id):
    sensor_info = b.get_sensor(sensor_id)
    motion_detected = sensor_info.get("state", {}).get("presence", False)
    return motion_detected


def turn_off_after_motion(sensor_id, wait_time, group_ids, brightness, t_time):
    if get_motion_sensor_status(sensor_id) == True:
        print("Moin")
        current_time = datetime.datetime.now()
        new_wait_time = current_time + datetime.timedelta(
            seconds=wait_time
        )  # Change here
        turn_on_groups(group_ids, brightness, t_time)
        return new_wait_time

    current_time = datetime.datetime.now()  # Moved outside of the if statement
    if wait_time <= current_time:  # Compare wait_time with current_time
        print("bye")
        turn_off_groups(group_ids)
        over = None
        return over


def motion_sensor_thread(sensor_id, wait_time, group_ids, brightness, t_time):
    while True:
        wait_time, over = turn_off_after_motion(
            sensor_id, wait_time, group_ids, brightness, t_time
        )
        if wait_time is None:
            break
        time.sleep(10)
