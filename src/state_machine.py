"""
Repräsentiert eine zustandsbasierte Automation (Endlicher Automat).
"""

from datetime import datetime
from .logger import AppLogger

class StateMachine:
    """Verwaltet die Logik für eine State-Machine-Automation."""

    def __init__(self, name, config, log: AppLogger, bridge, sensors, rooms, scenes, **kwargs):
        self.name = name
        self.config = config
        self.log = log
        self.bridge = bridge
        self.sensors = sensors
        self.rooms = rooms
        self.scenes = scenes
        self.enabled = config.get("enabled", True)
        self.current_state = config.get("initial_state")
        self.last_state_change = datetime.now()

        # Initialen Zustand beim Start anwenden
        self._apply_state_action(self.current_state)

    def run(self, now: datetime):
        """Führt einen Logik-Durchlauf des Automaten aus."""
        if not self.enabled:
            return

        for transition in self.config.get("transitions", []):
            if transition.get("from") == self.current_state:
                if self._check_conditions(transition.get("conditions", []), now):
                    self.log.info(f"Automat '{self.name}': Übergang von '{self.current_state}' zu '{transition.get('to')}' ausgelöst.")
                    self.current_state = transition.get("to")
                    self.last_state_change = now
                    self._apply_state_action(self.current_state)
                    # Wichtig: Nach einem erfolgreichen Übergang brechen wir ab.
                    break

    def _check_conditions(self, conditions: list, now: datetime) -> bool:
        """Prüft, ob alle Bedingungen für einen Übergang erfüllt sind."""
        # Platzhalter für die Bedingungslogik
        return False

    def _apply_state_action(self, state_name: str):
        """Führt die Aktion aus, die mit einem Zustand verbunden ist."""
        state_config = next((s for s in self.config.get("states", []) if s.get("name") == state_name), None)
        if not state_config:
            return

        action = state_config.get("action")
        if not action:
            return

        scene_name = action.get("scene_name")
        target_name = self.config.get("target_room")

        if scene_name and target_name:
            room = self.rooms.get(target_name)
            scene = self.scenes.get(scene_name)
            if room and scene:
                self.log.info(f"Automat '{self.name}': Wende Szene '{scene_name}' für Zustand '{state_name}' in Raum '{target_name}' an.")
                room.apply_state(scene.get_state())

    def get_status(self) -> dict:
        """Gibt den aktuellen Status des Automaten für die UI zurück."""
        return {
            "name": self.name,
            "type": "state_machine",
            "enabled": self.enabled,
            "currentState": self.current_state
        }