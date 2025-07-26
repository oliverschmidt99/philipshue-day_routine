from datetime import datetime, time, timedelta
from .daily_time_span import DailyTimeSpan
from .scene import Scene
import copy


class Routine:
    """Verwaltet die Logik für eine einzelne Tageslicht-Routine in einem Raum."""

    STATE_OFF = "OFF"
    STATE_MOTION = "MOTION"
    STATE_BRIGHTNESS_ACTIVE = "BRIGHTNESS_ACTIVE"
    STATE_RESET = "RESET"

    def __init__(
        self,
        name,
        room,
        sensor,
        routine_config,
        scenes,
        sun_times,
        log,
        global_settings,
    ):
        self.name = name
        self.room = room
        self.sensor = sensor
        self.config = routine_config
        self.scenes = scenes
        self.sun_times = sun_times
        self.log = log
        self.global_settings = global_settings
        self.enabled = self.config.get("enabled", True)
        self.time_span = self._create_time_span(self.config)
        self.state = self.STATE_OFF
        self.last_motion_time = None
        self.is_brightness_control_active = False
        self.do_not_disturb_active = False
        self.log.info(f"Routine '{self.name}' für Raum '{self.room.name}' geladen.")

    def _create_time_span(self, config):
        daily_time_conf = config.get("daily_time", {})
        H1 = daily_time_conf.get("H1", 0)
        M1 = daily_time_conf.get("M1", 0)
        H2 = daily_time_conf.get("H2", 23)
        M2 = daily_time_conf.get("M2", 59)
        return DailyTimeSpan(time(H1, M1), time(H2, M2), self.sun_times, self.log)

    def _check_do_not_disturb(self, period_config):
        if not period_config.get("do_not_disturb", False):
            if self.do_not_disturb_active:
                self.log.info(f"[{self.name}] 'Bitte nicht stören' wird beendet.")
                self.do_not_disturb_active = False
            return False

        actual_state_on = self.room.is_any_light_on()
        if actual_state_on is None:
            return self.do_not_disturb_active

        expected_state_on = False
        if self.is_brightness_control_active:
            expected_state_on = True
            expected_scene_name = f"Regelung (CT: {period_config.get('bri_ct')})"
        else:
            expected_scene_name = period_config.get("scene_name")
            expected_scene = self.scenes.get(expected_scene_name)
            if not expected_scene:
                return False
            expected_state_on = expected_scene.status

        if actual_state_on != expected_state_on:
            if not self.do_not_disturb_active:
                self.log.warning(
                    f"[{self.name}] Manuelle Änderung erkannt! Erwartet: '{expected_scene_name}' (An: {expected_state_on}), Ist: An: {actual_state_on}. 'Bitte nicht stören' wird aktiviert."
                )
                self.do_not_disturb_active = True
        else:
            if self.do_not_disturb_active:
                self.log.info(
                    f"[{self.name}] Lichtzustand entspricht wieder der Erwartung. 'Bitte nicht stören' wird beendet."
                )
                self.do_not_disturb_active = False
        return self.do_not_disturb_active

    def _handle_brightness_control(self, period_config, current_period):
        if not self.sensor or not period_config.get("bri_check", False):
            if self.is_brightness_control_active:
                self.is_brightness_control_active = False
            return False
        light_level = self.sensor.get_brightness()
        if light_level is None:
            self.log.warning(f"[{self.name}] Helligkeitssensor liefert keinen Wert.")
            return self.is_brightness_control_active
        threshold = period_config.get("max_light_level", 0)
        if threshold <= 0:
            return False
        hysteresis_percent = self.global_settings.get("hysteresis_percent", 25)
        hysteresis_value = int(threshold * (hysteresis_percent / 100.0))
        turn_on_threshold = threshold - hysteresis_value
        turn_off_threshold = threshold + hysteresis_value

        if light_level > turn_off_threshold:
            if self.is_brightness_control_active:
                self.log.info(
                    f"[{self.name}] Helligkeit ({light_level}) > Schwelle ({turn_off_threshold}). Deaktiviere Licht."
                )
                self.room.apply_state({"on": False})
                self.is_brightness_control_active = False
            return True
        elif light_level < turn_on_threshold:
            # ===== KORRIGIERTE FORMEL FÜR INVERSE HELLIGKEIT =====
            bri = 1 + (253 * (threshold - light_level) / threshold)
            bri = max(1, min(254, int(bri)))
            # =======================================================

            new_state = {"on": True, "bri": bri}
            bri_ct = period_config.get("bri_ct")
            if bri_ct:
                new_state["ct"] = bri_ct
            if not self.is_brightness_control_active:
                self.log.info(
                    f"[{self.name}] Helligkeit ({light_level}) < Schwelle ({turn_on_threshold}). Starte Regelung -> Helligkeit: {bri}, CT: {bri_ct}"
                )
            else:
                self.log.debug(
                    f"[{self.name}] Update Helligkeitsregelung. Sensor: {light_level} -> Lampe: {bri}"
                )
            self.room.apply_state(new_state)
            self.is_brightness_control_active = True
            return True
        else:
            self.log.debug(
                f"[{self.name}] Helligkeit ({light_level}) in Hysterese-Zone. Halte Zustand."
            )
            return True

    def run(self, now):
        if not self.enabled:
            if self.state != self.STATE_OFF:
                self.room.apply_state({"on": False})
                self.state = self.STATE_OFF
                self.do_not_disturb_active = False
            return
        current_period = self.time_span.get_current_period(now)
        if not current_period:
            return
        period_config = self.config.get(current_period)
        if not period_config:
            return

        if self.sensor and period_config.get("motion_check", False):
            if self.sensor.get_motion():
                if self.state != self.STATE_MOTION:
                    self.log.info(
                        f"[{self.name}] Bewegung erkannt -> Szene: '{period_config['x_scene_name']}'."
                    )
                    scene_to_set = self.scenes.get(period_config["x_scene_name"])
                    if scene_to_set:
                        self.room.apply_state(scene_to_set.get_state())
                    self.state = self.STATE_MOTION
                    self.is_brightness_control_active = False
                    self.do_not_disturb_active = False
                self.last_motion_time = now
                return

        if self.state == self.STATE_MOTION:
            wait_time_conf = period_config.get("wait_time", {"min": 0, "sec": 5})
            timeout_seconds = (wait_time_conf.get("min", 0) * 60) + wait_time_conf.get(
                "sec", 5
            )
            if self.last_motion_time and now - self.last_motion_time > timedelta(
                seconds=timeout_seconds
            ):
                self.log.info(
                    f"[{self.name}] Keine Bewegung für {timeout_seconds}s. Kehre zum Normalzustand zurück."
                )
                self.state = self.STATE_RESET
            else:
                return

        if self._check_do_not_disturb(period_config):
            return

        if self._handle_brightness_control(period_config, current_period):
            return

        if self.state != current_period and not self.is_brightness_control_active:
            self.log.info(
                f"---------- Zustands-Wechsel für '{self.name}' -> '{current_period}' ----------"
            )
            scene_to_set = self.scenes.get(period_config["scene_name"])
            if scene_to_set:
                self.log.info(f"Setze Normal-Szene: '{period_config['scene_name']}'.")
                self.room.apply_state(scene_to_set.get_state())
            self.state = current_period

    def get_status(self):
        motion_detected = self.sensor.get_motion() if self.sensor else False
        last_scene_name = "N/A"
        current_period_for_status = self.time_span.get_current_period(
            datetime.now().astimezone()
        )
        if self.do_not_disturb_active:
            last_scene_name = "Manuell (DnD aktiv)"
        elif (
            self.state == self.STATE_MOTION
            and current_period_for_status
            and self.config.get(current_period_for_status)
        ):
            last_scene_name = self.config[current_period_for_status].get(
                "x_scene_name", "N/A"
            )
        elif (
            self.is_brightness_control_active
            and current_period_for_status
            and self.config.get(current_period_for_status)
        ):
            last_scene_name = f"Geregelt (CT: {self.config[current_period_for_status].get('bri_ct', 'N/A')})"
        elif self.state != self.STATE_OFF and self.config.get(self.state):
            last_scene_name = self.config[self.state].get("scene_name", "N/A")
        return {
            "name": self.name,
            "enabled": self.enabled,
            "period": current_period_for_status,
            "motion_status": (
                "Bewegung erkannt" if motion_detected else "Keine Bewegung"
            ),
            "last_scene": last_scene_name,
            "brightness": self.sensor.get_brightness() if self.sensor else "N/A",
            "temperature": self.sensor.get_temperature() if self.sensor else "N/A",
            "last_motion_iso": (
                self.last_motion_time.isoformat() if self.last_motion_time else None
            ),
            "daily_time": self.config.get("daily_time", {}),
        }
