from control.scene import Scene

class Room:
    """
    Repräsentiert einen Raum mit den zugehörigen Lampengruppen.
    """
    def __init__(self, bridge, log, name, group_ids, switch_ids, sensor_id):
        self.bridge = bridge
        self.log = log
        self.name = name
        self.group_ids = group_ids
        self.switch_ids = switch_ids
        self.sensor_id = sensor_id

    def turn_groups(self, scene: Scene, t_time_overwrite: int = None):
        """
        Schaltet alle Lampengruppen in diesem Raum auf eine bestimmte Szene.
        """
        if not isinstance(scene, Scene):
            self.log.error(f"Ungültiger Szenentyp für Raum '{self.name}' empfangen.")
            return

        state = scene.get_state(t_time_overwrite)
        self.log.info(f"Raum '{self.name}': Setze Gruppen {self.group_ids} auf Zustand: {state}")

        for group_id in self.group_ids:
            self.bridge.set_group(group_id, state)
