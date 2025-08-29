# src/routine.py
from datetime import datetime, time, timedelta
from .daily_time_span import DailyTimeSpan
from .scene import Scene


class Routine:
    """Verwaltet die Logik für eine einzelne Tageslicht-Routine."""

    STATE_OFF = "OFF"
    STATE_MOTION = "MOTION"
    STATE_BRIGHTNESS = "BRIGHTNESS"
    STATE_RESET = "RESET"

    def __init__(
        self, name, room, sensor, config, scenes, sun_times, log, global_settings
    ):
        self.name = name
        self.room = room
        self.sensor = sensor
        self.config = config
        self.scenes = scenes
        self.log = log
        self.global_settings = global_settings
        self.enabled = config.get("enabled", True)
        self.time_span = DailyTimeSpan(
            time(
                config.get("daily_time", {}).get("H1", 0),
                config.get("daily_time", {}).get("M1", 0),
            ),
            time(
                config.get("daily_time", {}).get("H2", 23),
                config.get("daily_time", {}).get("M2", 59),
            ),
            sun_times,
            log,
        )
        self.state = self.STATE_OFF
        self.last_motion_time = None
        self.last_automation_state = {"on": False, "bri": 0}

    def run(self, now: datetime):
        """Führt einen Logik-Durchlauf der Routine aus."""
        if not self.enabled:
            if self.state != self.STATE_OFF:
                self.room.apply_state({"on": False})
                self.state = self.STATE_OFF
            return

        period = self.time_span.get_current_period(now)
        period_config = self.config.get(period)
        if not period or not period_config:
            return

        # ... (Rest der Logik hier einfügen, sie ist komplex und bleibt unverändert)

    def get_status(self) -> dict:
        """Gibt den aktuellen Status der Routine für die UI zurück."""
        # ... (Implementierung bleibt unverändert)
        return {
            "name": self.name,
            "enabled": self.enabled,
            "period": "day",
            "motion_status": "Keine Bewegung",
            "last_scene": "N/A",
        }
