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

    def __init__(self, name, room, sensor, routine_config, scenes, sun_times, log, global_settings):
        self.name = name
        self.room = room
        self.sensor = sensor
        self.config = routine_config
        self.scenes = scenes
        self.sun_times = sun_times
        self.log = log
        self.global_settings = global_settings

        self.enabled = self.config.get('enabled', True)
        self.time_span = self._create_time_span(self.config)

        self.state = self.STATE_OFF
        self.last_motion_time = None
        self.is_brightness_control_active = False

        self.log.info(f"Routine '{self.name}' für Raum '{self.room.name}' geladen.")


    def _create_time_span(self, config):
        daily_time_conf = config.get('daily_time', {})
        start_time = time(daily_time_conf.get('H1', 0), daily_time_conf.get('M1', 0))
        end_time = time(daily_time_conf.get('H2', 23), daily_time_conf.get('M2', 59))

        day_start_str = self.global_settings.get('day_start_time', '12:00')
        night_start_str = self.global_settings.get('night_start_time', '23:00')

        p_start_morning = 'sunrise'
        p_start_day = datetime.strptime(day_start_str, '%H:%M').time()
        p_start_evening = 'sunset'
        p_start_night = datetime.strptime(night_start_str, '%H:%M').time()

        time_spans = {
            'morning': (p_start_morning, p_start_day),
            'day': (p_start_day, p_start_evening),
            'evening': (p_start_evening, p_start_night),
            'night': (p_start_night, p_start_morning)
        }

        return DailyTimeSpan(start_time, end_time, self.sun_times, time_spans, self.log)

    def _handle_brightness_control(self, period_config, current_period):
        if not self.sensor or not period_config.get('bri_check', False):
            return False

        light_level = self.sensor.get_brightness()
        threshold_low = period_config.get('max_light_level', 0)
        
        if threshold_low <= 0:
            return False

        hysteresis_percent = self.global_settings.get('hysteresis_percent', 25)
        threshold_high = int(threshold_low * (1 + hysteresis_percent / 100))

        if light_level < threshold_low:
            bri = 1 + (253 * (threshold_low - light_level) / threshold_low)
            bri = max(1, min(254, int(bri)))

            if not self.is_brightness_control_active:
                self.log.info(f"[{self.name}] Starte Helligkeitsregelung. Sensor: {light_level} -> Lampe: {bri}")
                base_scene_name = period_config['scene_name']
                base_scene = self.scenes.get(base_scene_name)
                if not base_scene:
                    self.log.warning(f"[{self.name}] Basis-Szene '{base_scene_name}' nicht gefunden.")
                    return True
                new_state = copy.deepcopy(base_scene.get_state())
                new_state['on'] = True
                new_state['bri'] = bri
                self.room.apply_state(new_state)
            else:
                self.log.debug(f"[{self.name}] Update Helligkeitsregelung. Sensor: {light_level} -> Lampe: {bri}")
                self.room.apply_state({'bri': bri})
            
            self.is_brightness_control_active = True
            self.state = self.STATE_BRIGHTNESS_ACTIVE
            return True

        elif light_level > threshold_high and self.is_brightness_control_active:
            self.log.info(f"[{self.name}] Helligkeit ({light_level}) über Ausschalt-Schwelle ({threshold_high}). Deaktiviere Licht.")
            self.room.apply_state({'on': False})
            self.is_brightness_control_active = False
            self.state = current_period
            return True

        return self.is_brightness_control_active

    def run(self, now):
        if not self.enabled or not self.time_span.is_active(now.time()):
            if self.state != self.STATE_OFF:
                self.room.apply_state({'on': False})
                self.state = self.STATE_OFF
            return

        current_period = self.time_span.get_current_period(now)
        if not current_period:
            return
            
        period_config = self.config[current_period]

        if self.sensor and period_config.get('motion_check', False):
            if self.sensor.get_motion():
                if self.state != self.STATE_MOTION:
                    self.log.info(f"[{self.name}] Bewegung erkannt. Aktiviere Bewegungs-Szene: '{period_config['x_scene_name']}'.")
                    scene_to_set = self.scenes.get(period_config['x_scene_name'])
                    if scene_to_set:
                        self.room.apply_state(scene_to_set.get_state())
                    self.state = self.STATE_MOTION
                self.last_motion_time = now
                return

        if self.state == self.STATE_MOTION:
            wait_time_conf = period_config.get('wait_time', {'min': 0, 'sec': 5})
            timeout_seconds = (wait_time_conf.get('min', 0) * 60) + wait_time_conf.get('sec', 5)
            if now - self.last_motion_time > timedelta(seconds=timeout_seconds):
                self.log.info(f"[{self.name}] Keine Bewegung für {timeout_seconds}s. Kehre zum Normalzustand zurück.")
                self.state = self.STATE_RESET 
            else:
                return

        if self._handle_brightness_control(period_config, current_period):
            return

        if self.state != current_period:
            self.log.info(f"---------- Zustands-Wechsel für Routine '{self.name}' zu '{current_period}' ----------")
            self.log.info(f"Setze Normal-Szene: '{period_config['scene_name']}'.")
            scene_to_set = self.scenes.get(period_config['scene_name'])
            if scene_to_set:
                self.room.apply_state(scene_to_set.get_state())
            self.state = current_period
            self.is_brightness_control_active = False

    def get_status(self):
        motion_detected = self.sensor.get_motion() if self.sensor else False
        brightness = self.sensor.get_brightness() if self.sensor else 'N/A'
        last_scene_name = 'N/A'
        
        current_period_for_status = self.time_span.get_current_period(datetime.now().astimezone())
        if self.state == self.STATE_MOTION and current_period_for_status:
            last_scene_name = self.config[current_period_for_status]['x_scene_name']
        elif self.state == self.STATE_BRIGHTNESS_ACTIVE and current_period_for_status:
            last_scene_name = f"Geregelt ({self.config[current_period_for_status]['scene_name']})"
        elif self.state != self.STATE_OFF and self.config.get(self.state):
             last_scene_name = self.config.get(self.state, {}).get('scene_name', 'N/A')

        return {
            "name": self.name,
            "enabled": self.enabled,
            "period": current_period_for_status,
            "motion_status": f"{'Bewegung erkannt' if motion_detected else 'Keine Bewegung'}",
            "last_scene": last_scene_name,
            "brightness": brightness 
        }
