from huebridge import *
import datetime
import logging


from data_work import *

def turn_off_groups(group_ids):
    for group_id in group_ids:
        b.set_group(group_id, "on", False)
        print(f"Gruppe {group_id} wurde ausgeschaltet.")


def turn_on_groups(group_ids, brightness, t_time):
    for group_id in group_ids:
        b.set_group(group_id, "on", True)
        b.set_group(group_id, "bri", brightness, transitiontime=t_time)
        print(f"Gruppe {group_id} wurde eingeschaltet.")


def check_lamp_state(lamp_array, lamp_states):
    current_datetime = datetime.datetime.now()
    true_groups = []
    for item in lamp_array:
        group_id = item["group_id"]
        on_state = b.get_group(group_id, "on")
        if on_state:
            true_groups.append(group_id)
            lamp_states[group_id]["on"] = True
            if lamp_states[group_id]["last_turned_on_time"] is None:
                lamp_states[group_id]["last_turned_on_time"] = current_datetime
    for group_id in true_groups:
        last_turned_on_time = lamp_states[group_id]["last_turned_on_time"]
        t_x = lamp_states[group_id]["t_x"]
        if last_turned_on_time is not None:
            if (current_datetime - last_turned_on_time).total_seconds() > t_x:
                logging.info("Mode - Turn_off_light %s", group_id)
                b.set_group(group_id, "on", False)
                lamp_states[group_id]["on"] = False
                lamp_states[group_id]["last_turned_on_time"] = None
        else:
            logging.warning("Last turned on time is None for group %s", group_id)


def initialize_lamp_states(zonen_states):
    lamp_states = {
        item["group_id"]: {
            "on": False,
            "last_turned_on_time": None,
            "brightness": None,
            "t_x": item.get("t_x", 0),
        }
        for item in zonen_states
    }
    return lamp_states

