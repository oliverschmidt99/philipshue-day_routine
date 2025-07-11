from datetime import datetime, time, timedelta

class Routine:
    """
    Diese Klasse implementiert die feste Tageslogik basierend auf dem
    Konzept einer "Normal-Szene", die bei Bewegung von einer
    "Bewegungs-Szene" überschrieben wird.
    """
    def __init__(self, name, room, sensor, routine_config, scenes, sun_times, log):
        self.name = name
        self.room = room
        self.sensor = sensor
        self.log = log
        self.scenes = scenes
        self.sun_times = sun_times

        dt_conf = routine_config.get('daily_time', {})
        self.start_time = time(dt_conf.get('H1', 0), dt_conf.get('M1', 0))
        self.end_time = time(dt_conf.get('H2', 23), dt_conf.get('M2', 59))

        self.morning_conf = routine_config.get('morning')
        self.day_conf = routine_config.get('day')
        self.evening_conf = routine_config.get('evening')
        self.night_conf = routine_config.get('night')

        self.current_period = None
        self.last_triggered_scene_name = None
        self.last_motion_time = None
        self.is_in_motion_state = False

    def get_current_period(self, now: datetime):
        """
        Ermittelt den aktuellen Tageszeitraum ('morning', 'day', 'evening', 'night')
        oder None, wenn die Routine inaktiv ist.
        """
        current_time = now.time()
        is_active = (self.start_time <= current_time < self.end_time) if self.start_time <= self.end_time else (current_time >= self.start_time or current_time < self.end_time)
        if not is_active:
            return None

        sunrise_time = self.sun_times['sunrise'].time() if self.sun_times else time(6, 30)
        sunset_time = self.sun_times['sunset'].time() if self.sun_times else time(20, 0)

        if sunrise_time <= current_time < sunset_time: return "day"
        if self.start_time <= current_time < sunrise_time: return "morning"
        if sunset_time <= current_time < self.end_time: return "evening"
        return "night"

    def get_status(self):
        """Gibt den aktuellen Zustand der Routine als Dictionary für die UI zurück."""
        current_period_for_status = self.get_current_period(datetime.now().astimezone())
        
        motion_status_text = "Nicht relevant"
        is_motion_active_now = False
        if self.sensor:
            is_motion_active_now = self.sensor.get_motion()
            if is_motion_active_now:
                if self.last_motion_time:
                     motion_status_text = f"Aktiv seit {self.last_motion_time.strftime('%H:%M:%S')}"
                else:
                     motion_status_text = "Aktiv"
            elif self.is_in_motion_state and self.last_motion_time:
                 motion_status_text = f"Letzte Bewegung um {self.last_motion_time.strftime('%H:%M:%S')}"
            else:
                motion_status_text = "Keine Bewegung"

        return {
            "name": self.name,
            "period": current_period_for_status,
            "last_scene": self.last_triggered_scene_name,
            "motion_status": motion_status_text,
            "motion_active": is_motion_active_now
        }

    def run(self, now: datetime):
        period = self.get_current_period(now)
        
        if not period:
            if self.current_period is not None:
                self.log.info(f"[{self.name}] Routine jetzt inaktiv.")
            self.current_period = None
            return

        section_config = getattr(self, f"{period}_conf", None)
        if not section_config:
            return

        normal_scene_name = section_config.get('scene_name')
        motion_scene_name = section_config.get('x_scene_name')

        if period != self.current_period:
            scene_obj = self.scenes.get(normal_scene_name)
            if scene_obj:
                self.log.info(f"[{self.name}] Neuer Zeitraum: '{period}'. Setze Normal-Szene: '{normal_scene_name}'.")
                self.room.turn_groups(scene_obj)
                self.last_triggered_scene_name = normal_scene_name
            self.current_period = period
            self.last_motion_time = None
            self.is_in_motion_state = False

        if not self.sensor or not section_config.get('motion_check', False):
            return

        has_motion = self.sensor.get_motion()
        self.log.debug(f"[{self.name}] Sensor-Status: Bewegung={has_motion}")

        if section_config.get('do_not_disturb', False) and self.room.is_any_light_on():
            if has_motion:
                self.last_motion_time = now
            self.log.debug(f"[{self.name}] 'Nicht stören' aktiv und Licht ist an. Ignoriere Trigger.")
            return

        if has_motion:
            if not self.is_in_motion_state:
                self.last_motion_time = now
            
            scene_to_trigger = motion_scene_name
            
            if section_config.get('bri_check', False):
                brightness = self.sensor.get_brightness()
                max_light = section_config.get('max_light_level', 0)
                self.log.debug(f"[{self.name}] Helligkeits-Check: Aktuell={brightness}, Max={max_light}")
                if brightness > max_light:
                    self.log.debug(f"[{self.name}] Zu hell für Bewegungs-Szene. Keine Aktion.")
                    return

            if self.last_triggered_scene_name != scene_to_trigger:
                scene_obj = self.scenes.get(scene_to_trigger)
                if scene_obj:
                    self.log.info(f"[{self.name}] Bewegung erkannt. Aktiviere Bewegungs-Szene: '{scene_to_trigger}'.")
                    self.room.turn_groups(scene_obj)
                    self.last_triggered_scene_name = scene_to_trigger
            self.is_in_motion_state = True
        
        else: # Keine Bewegung
            if self.is_in_motion_state:
                # KORRIGIERT: Robuste Behandlung für verschiedene 'wait_time'-Formate
                wait_time_conf = section_config.get('wait_time', {'min': 5, 'sec': 0})
                wait_time_delta = None

                if isinstance(wait_time_conf, dict):
                    # Neues Format: {min: 5, sec: 0}
                    wait_time_delta = timedelta(minutes=wait_time_conf.get('min', 0), seconds=wait_time_conf.get('sec', 0))
                elif isinstance(wait_time_conf, (int, float)):
                    # Altes Format: 5 (wird als Minuten interpretiert)
                    self.log.warning(f"[{self.name}] Veraltetes 'wait_time'-Format erkannt. Bitte Routine neu speichern, um auf min/sek umzustellen.")
                    wait_time_delta = timedelta(minutes=int(wait_time_conf))
                else:
                    # Fallback
                    wait_time_delta = timedelta(minutes=5)

                if self.last_motion_time and (now > self.last_motion_time + wait_time_delta):
                    scene_obj = self.scenes.get(normal_scene_name)
                    if scene_obj:
                        self.log.info(f"[{self.name}] Keine Bewegung für {wait_time_delta}. Kehre zu Normal-Szene '{normal_scene_name}' zurück.")
                        self.room.turn_groups(scene_obj)
                        self.last_triggered_scene_name = normal_scene_name
                    
                    self.is_in_motion_state = False
