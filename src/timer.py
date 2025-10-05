"""
Repräsentiert eine Timer-basierte Automation.
"""
from datetime import datetime, timedelta
from .logger import AppLogger

class Timer:
    """Verwaltet die Logik für eine Timer-Automation."""

    def __init__(self, name, config, log: AppLogger, bridge, rooms, scenes, **kwargs):
        self.name = name
        self.config = config
        self.log = log
        self.bridge = bridge
        self.rooms = rooms
        self.scenes = scenes
        self.enabled = config.get("enabled", True)
        self.is_active = False
        self.end_time = None

    def run(self, now: datetime):
        """Führt einen Logik-Durchlauf des Timers aus."""
        if not self.enabled:
            return

        # 1. Timer starten, falls er nicht aktiv ist und die Trigger-Bedingung erfüllt ist
        if not self.is_active and self._check_triggers():
            duration_minutes = self.config.get("duration_minutes", 10)
            self.end_time = now + timedelta(minutes=duration_minutes)
            self.is_active = True
            self.log.info(f"Timer '{self.name}' gestartet. Läuft ab in {duration_minutes} Minuten.")

        # 2. Timer ausführen, wenn er aktiv ist und die Zeit abgelaufen ist
        if self.is_active and now >= self.end_time:
            self._execute_action()
            self.is_active = False
            self.end_time = None

    def _check_triggers(self) -> bool:
        """Prüft die Startbedingungen des Timers."""
        # Platzhalter für die Trigger-Logik
        return False

    def _execute_action(self):
        """Führt die End-Aktion des Timers aus."""
        action = self.config.get("action")
        if not action:
            return

        target_name = action.get("target_room")
        scene_name = action.get("scene_name")

        if target_name and scene_name:
            room = self.rooms.get(target_name)
            scene = self.scenes.get(scene_name)
            if room and scene:
                self.log.info(f"Timer '{self.name}': Zeit abgelaufen. Führe Aktion für Raum '{target_name}' aus.")
                room.apply_state(scene.get_state())

    def get_status(self) -> dict:
        """Gibt den aktuellen Status des Timers für die UI zurück."""
        return {
            "name": self.name,
            "type": "timer",
            "enabled": self.enabled,
            "isActive": self.is_active,
            "endTime": self.end_time.isoformat() if self.end_time else None
        }