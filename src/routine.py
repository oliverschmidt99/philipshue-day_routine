"""
Verwaltet die Zustandslogik und Ausführung einer einzelnen,
konfigurierbaren Tageslicht-Routine für einen Raum.
"""
import time
from datetime import datetime, timedelta
from .daily_time_span import DailyTimeSpan
from .state_machine import StateMachine
from .logger import AppLogger

class Routine:
    """Verwaltet die Logik für eine einzelne Tageslicht-Routine."""

    def __init__(
        self, name, room, sensor, config, scenes, sun_times, log: AppLogger, global_settings, **kwargs
    ):
        self.name = name
        self.room = room
        self.sensor = sensor
        self.config = config
        self.scenes = scenes
        self.sun_times = sun_times
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
        self.last_trigger_check = None

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
            self._handle_motion(now, period_config)

        # Führe die Trigger-Prüfung nur einmal pro Minute aus
        if self.last_trigger_check is None or (now - self.last_trigger_check).total_seconds() > 60:
            self._check_triggers(now)
            self.last_trigger_check = now

    def _handle_motion(self, now: datetime, period_config: dict):
        """Verarbeitet die Bewegungslogik."""
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

    def _check_triggers(self, now: datetime):
        """Überprüft und führt zeit- und bedingungsbasierte Trigger aus."""
        triggers = self.config.get("triggers", [])
        for trigger in triggers:
            if trigger.get("type") == "time":
                self._handle_time_trigger(trigger, now)
            elif trigger.get("type") == "condition":
                self._handle_conditional_trigger(trigger, now)

    def _handle_time_trigger(self, trigger: dict, now: datetime):
        """Verarbeitet einen Zeit-Trigger."""
        trigger_time = None
        t_time = trigger.get("time")
        
        if isinstance(t_time, str) and ":" in t_time:
            try:
                h, m = map(int, t_time.split(":"))
                trigger_time = now.replace(hour=h, minute=m, second=0, microsecond=0)
            except ValueError:
                self.log.warning(f"Ungültiges Zeitformat für Trigger: {t_time}")
                return
        
        elif self.sun_times:
            event = trigger.get("event") # "sunrise" or "sunset"
            offset_minutes = trigger.get("offset_minutes", 0)
            if event in self.sun_times:
                trigger_time = self.sun_times[event] + timedelta(minutes=offset_minutes)

        if trigger_time and trigger_time.hour == now.hour and trigger_time.minute == now.minute:
            self.log.info(f"Routine '{self.name}': Zeit-Trigger '{trigger.get('name')}' wird ausgeführt.")
            self._apply_scene(trigger.get("scene_name"))
            
    def _handle_conditional_trigger(self, trigger: dict, now: datetime):
        """Verarbeitet einen bedingungsbasierten Trigger."""
        self.log.debug(f"Bedingungs-Trigger '{trigger.get('name')}' wird geprüft (Logik noch nicht implementiert).")


    def _apply_scene(self, scene_name: str | None):
        """Wendet eine Szene auf den Raum an, falls sie existiert."""
        if not scene_name or not self.room:
            return

        scene_to_apply = self.scenes.get(scene_name)
        if scene_to_apply:
            self.log.info(f"Routine '{self.name}': Wende Szene '{scene_name}' an.")
            throttle_s = self.global_settings.get("command_throttle_s", 1.0)
            self.room.apply_state(
                scene_to_apply.get_state(), command_throttle_s=throttle_s
            )
            self.last_scene_name = scene_name
        else:
            self.log.warning(
                f"Routine '{self.name}': Szene '{scene_name}' nicht gefunden."
            )

    def get_status(self) -> dict:
        """Gibt den aktuellen Status der Routine für die UI zurück."""
        motion_status = "Deaktiviert"
        if self.config.get(self.current_period, {}).get("motion_check"):
            motion_status = (
                "In Bewegung" if self.is_in_motion_state else "Keine Bewegung"
            )

        return {
            "name": self.name,
            "enabled": self.enabled,
            "period": self.current_period,
            "motion_status": motion_status,
            "last_scene": self.last_scene_name,
            "daily_time": self.config.get("daily_time", {}),
        }