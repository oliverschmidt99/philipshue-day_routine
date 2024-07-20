from control.huebridge import *
from control.Daily_routine import *
from control.Room import *

import numpy as np


sen = b.get_sensor_objects("name")
light_names = b.get_light_objects("name")
lights = b.lights


if __name__ == "__main__":

    room_olli = Room([1], [5, 99], [2, 3, 4])
    room_olli_daytime = Daily_time(8, 0, 0, 22, 0, 0)

    while True:
        a = room_olli_daytime.get_time_span()
        print(a)
