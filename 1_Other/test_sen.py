from phue import Bridge

import time

BRIDGE_IP = "192.168.178.42"

b = Bridge(BRIDGE_IP)
b.connect()
b.get_api()

sen = b.get_sensor_objects("name")
light_names = b.get_light_objects("name")
lights = b.lights
groups = b.get_group()

sen_id = 3


def get_brightness(sensor_id):
    """
    Diese Funktion gibt die Helligkeit (Lux) eines Sensors zurück.

    :param b: Ein verbundener Bridge-Instanz
    :param sensor_id: Die ID des Sensors
    :return: Die Helligkeit (Lux-Wert) oder None, wenn keine 'lightlevel' Informationen verfügbar sind
    """
    try:
        # Sensordaten abrufen
        sensor_data = b.get_sensor(sensor_id)

        # Helligkeitswert (Lux) extrahieren
        if "state" in sensor_data and "lightlevel" in sensor_data["state"]:
            lux_value = sensor_data["state"]["lightlevel"]
            return lux_value
        else:
            return None

    except Exception as e:
        return None


if __name__ == "__main__":
    while True:
        time.sleep(2)
        a = get_brightness(sen_id)
        print(a)
