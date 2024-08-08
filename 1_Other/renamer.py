from phue import Bridge


BRIDGE_IP = "192.168.178.42"

b = Bridge(BRIDGE_IP)
b.connect()
b.get_api()


b = Bridge(BRIDGE_IP)

# Authentifizieren, wenn dies die erste Verbindung ist
# b.connect()

def list_lights():
    lights = b.get_light_objects('id')
    for light_id, light in lights.items():
        print(f"ID: {light_id}, Name: {light.name}")

def list_sensors():
    sensors = b.get_sensor_objects('id')
    for sensor_id, sensor in sensors.items():
        print(f"ID: {sensor_id}, Name: {sensor.name}")

def list_groups():
    groups = b.get_group()
    for group_id, group in groups.items():
        print(f"ID: {group_id}, Name: {group['name']}")

def rename_light(light_id, new_name):
    b.set_light(light_id, 'name', new_name)
    print(f"Light {light_id} renamed to {new_name}")

def rename_sensor(sensor_id, new_name):
    b.set_sensor(sensor_id, 'name', new_name)
    print(f"Sensor {sensor_id} renamed to {new_name}")

def rename_group(group_id, new_name):
    b.set_group(group_id, 'name', new_name)
    print(f"Group {group_id} renamed to {new_name}")

def delete_light(light_id):
    b.delete_light(light_id)
    print(f"Light {light_id} deleted")

def delete_sensor(sensor_id):
    b.delete_sensor(sensor_id)
    print(f"Sensor {sensor_id} deleted")

def delete_group(group_id):
    b.delete_group(group_id)
    print(f"Group {group_id} deleted")

def get_user_choice(prompt, choices):
    while True:
        print(prompt)
        for key, value in choices.items():
            print(f"{key}: {value}")
        choice = input("Ihre Auswahl: ")
        if choice in choices:
            return choice
        else:
            print("Ungültige Auswahl, bitte erneut versuchen.")

def handle_item(item_type, list_function, rename_function, delete_function):
    list_function()
    item_id = input(f"Geben Sie die ID des {item_type} ein, das Sie bearbeiten möchten (oder 'skip' zum Überspringen): ")
    if item_id.lower() == 'skip':
        return

    action = get_user_choice(f"Möchten Sie das {item_type} umbenennen oder löschen?", {
        '1': 'Umbenennen',
        '2': 'Löschen',
        '3': 'Überspringen'
    })

    if action == '1':
        new_name = input(f"Geben Sie den neuen Namen für das {item_type} ein: ")
        rename_function(item_id, new_name)
    elif action == '2':
        delete_function(item_id)

def main():
    while True:
        choice = get_user_choice("Was möchten Sie sehen?", {
            '1': 'Lampen',
            '2': 'Sensoren',
            '3': 'Gruppen',
            '4': 'Beenden'
        })

        if choice == '1':
            handle_item('Lampe', list_lights, rename_light, delete_light)
        elif choice == '2':
            handle_item('Sensor', list_sensors, rename_sensor, delete_sensor)
        elif choice == '3':
            handle_item('Gruppe', list_groups, rename_group, delete_group)
        elif choice == '4':
            break

if __name__ == '__main__':
    main()
    

