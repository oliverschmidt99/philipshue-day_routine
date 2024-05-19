from huebridge import *
import time
from lamp import turn_on_groups, turn_off_groups

class sensor:
    sensor_id = 0
    group_ids = 0
    wait_time = 0
    last_active_time = 0
    def __init__(
        self,
        sensor_id,
        group_ids,
        wait_time,
    ):
        self.sensor_id = sensor_id
        self.group_ids = group_ids
        self.wait_time = wait_time

    def get_motion_sensor_status(self):
        sensor_info = b.get_sensor(self.sensor_id)
        motion_detected = sensor_info.get("state", {}).get("presence", False)
        return motion_detected

    def turn_off_after_motion(self, brightness, t_time):

        if self.get_motion_sensor_status(self.sensor_id) == True:
            print("Moin")
            turn_on_groups(self.group_ids, brightness, t_time)
            self.last_active_time = time.time()
            return

        # Compare wait_time with current_time
        if self.last_active_time + self.wait_time >= time():
            print("bye")
            turn_off_groups(self.group_ids)








    # def motion_sensor_thread(self, brightness, t_time):
    #     while True:
    #         wait_time = self.turn_off_after_motion(
    #             self.sensor_id, self.wait_time, self.group_ids, brightness, t_time
    #         )
    #         if wait_time is None:
    #             break
    #         time.sleep(10)


    # def get_motion_sensor_status(sensor_id):
    #     sensor_info = b.get_sensor(sensor_id)
    #     motion_detected = sensor_info.get("state", {}).get("presence", False)
    #
    #     return motion_detected
    #
    #
    # def turn_off_after_motion(self,sensor_id, wait_time, group_ids, brightness, t_time):
    #     new_wait_time = None
    #     if self.get_motion_sensor_status(sensor_id) == True:
    #         print("Moin")
    #         turn_on_groups(group_ids, brightness, t_time)
    #
    #         self.last_control_time = time.time()
    #
    #         return
    #     else:
    #         current_time = datetime.datetime.now()  # Moved outside of the if statement
    #         time_since_last_control = time() - self.last_control_time
    #         if self.last_control_time >= time() - wait_time:  # Compare wait_time with current_time
    #             print("bye")
    #             turn_off_groups(group_ids)
    #             return None
    #
    #
    #
    #
    #
    #     if self.get_motion_sensor_status(sensor_id) == True:
    #         print("Moin")
    #         current_time = datetime.datetime.now()
    #         new_wait_time = current_time + datetime.timedelta(
    #             seconds=wait_time
    #         )  # Change here
    #         turn_on_groups(group_ids, brightness, t_time)
    #
    #         return new_wait_time
    #
    #     else:
    #         current_time = datetime.datetime.now()  # Moved outside of the if statement
    #
    #         if wait_time <= current_time:  # Compare wait_time with current_time
    #             print("bye")
    #             turn_off_groups(group_ids)
    #             return None
    #     return new_wait_time
    #
    #
