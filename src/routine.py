"""
Verwaltet die Zustandslogik und Ausführung einer einzelnen,
konfigurierbaren Tageslicht-Routine für einen Raum.
"""

from datetime import datetime, time, timedelta
from .daily_time_span import DailyTimeSpan


class Routine:
    """Verwaltet die Logik für eine einzelne Tageslicht-Routine."""

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

        daily_time_conf = config.get("daily_time", {})
        self.time_span = DailyTimeSpan(
            time(daily_time_conf.get("H1", 0), daily_time_conf.get("M1", 0)),
            time(daily_time_conf.get("H2", 23), daily_time_conf.get("M2", 59)),
            sun_times,
            log,
        )

        # Zustandsvariablen
        self.current_period = None
        self.is_in_motion_state = False
        self.last_motion_time = None
        self.do_not_disturb_active = False
        self.last_scene_name = "N/A"

    def run(self, now: datetime):
        """Führt einen Logik-Durchlauf der Routine aus."""
        if not self.enabled:
            return

        period = self.time_span.get_current_period(now)
        period_config = self.config.get(period)

        if period != self.current_period:
            self.log.info(f"Routine '{self.name}': Wechsel zu Zeitraum '{period}'.")
            self.current_period = period
            self.is_in_motion_state = False
            self.do_not_disturb_active = False
            if period_config and not period_config.get("motion_check"):
                self._apply_scene(period_config.get("scene_name"))
            return

        if not period_config:
            return

        if self.sensor and period_config.get("motion_check"):
            has_motion = self.sensor.get_motion()
            wait_time_conf = period_config.get("wait_time", {"min": 0, "sec": 5})
            wait_seconds = wait_time_conf.get("min", 0) * 60 + wait_time_conf.get(
                "sec", 5
            )

            if has_motion:
                self.last_motion_time = now
                if not self.is_in_motion_state:
                    self.log.info(f"Routine '{self.name}': Bewegung erkannt.")
                    self.is_in_motion_state = True
                    self._apply_scene(period_config.get("x_scene_name"))

            elif self.is_in_motion_state and self.last_motion_time:
                if now - self.last_motion_time > timedelta(seconds=wait_seconds):
                    self.log.info(
                        f"Routine '{self.name}': Wartezeit nach Bewegung abgelaufen."
                    )
                    self.is_in_motion_state = False
                    self.last_motion_time = None
                    self._apply_scene(period_config.get("scene_name"))

    def _apply_scene(self, scene_name: str | None):
        """Wendet eine Szene auf den Raum an, falls sie existiert."""
        if not scene_name or not self.room:
            return

        scene_to_apply = self.scenes.get(scene_name)
        if scene_to_apply:
            self.log.info(f"Routine '{self.name}': Wende Szene '{scene_name}' an.")
            self.room.apply_state(scene_to_apply.get_state())
            self.last_scene_name = scene_name
        else:
            self.log.warning(
                f"Routine '{self.name}': Szene '{scene_name}' nicht gefunden."
            )

    def get_status(self) -> dict:
        """Gibt den aktuellen Status der Routine für die UI zurück."""
        motion_status = "Deaktiviert"
        if self.sensor and self.config.get(self.current_period, {}).get("motion_check"):
            motion_status = (
                "In Bewegung" if self.is_in_motion_state else "Keine Bewegung"
            )

        # Hinzugefügte Logik zum Abrufen von Sensorwerten
        brightness = self.sensor.get_brightness() if self.sensor else "N/A"
        temperature = self.sensor.get_temperature() if self.sensor else "N/A"

        return {
            "name": self.name,
            "enabled": self.enabled,
            "period": self.current_period,
            "motion_status": motion_status,
            "last_scene": self.last_scene_name,
            "daily_time": self.config.get("daily_time", {}),
            "brightness": brightness,
            "temperature": temperature,
            "last_motion_iso": (
                self.last_motion_time.isoformat() if self.last_motion_time else None
            ),
        }
