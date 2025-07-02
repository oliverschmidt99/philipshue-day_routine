from control.scene import Scene

class Room:
    """
    Repräsentiert einen Raum und steuert die zugehörigen Lampengruppen
    über das phue Bridge-Objekt.
    """
    def __init__(self, bridge, log, name, group_ids, **kwargs):
        self.bridge = bridge
        self.log = log
        self.name = name
        self.group_ids = group_ids

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
            try:
                # Die phue-Bibliothek erwartet die group_id als Integer
                self.bridge.set_group(int(group_id), state)
            except Exception as e:
                self.log.error(f"Fehler beim Setzen von Gruppe {group_id} in Raum '{self.name}': {e}")
