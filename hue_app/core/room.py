from .scene import Scene

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
                # Stellt sicher, dass die ID ein Integer ist
                self.bridge.set_group(int(group_id), state)
            except Exception as e:
                self.log.error(f"Fehler beim Setzen von Gruppe {group_id} in Raum '{self.name}': {e}")

    def is_any_light_on(self) -> bool:
        """
        Prüft, ob in einer der Gruppen dieses Raumes mindestens ein Licht an ist.
        """
        for group_id in self.group_ids:
            try:
                # Hole den Zustand der Gruppe von der Bridge
                group_state = self.bridge.get_group(int(group_id))
                # Die 'any_on' Eigenschaft im 'state' gibt an, ob irgendein Licht in der Gruppe an ist
                if group_state and group_state.get('state', {}).get('any_on', False):
                    self.log.debug(f"Raum '{self.name}', Gruppe {group_id}: Licht ist bereits an.")
                    return True
            except Exception as e:
                self.log.error(f"Fehler beim Abrufen des Gruppenstatus für Gruppe {group_id}: {e}")
                # Im Fehlerfall gehen wir davon aus, dass das Licht aus ist, um die Automatisierung nicht zu blockieren
                continue
        return False
