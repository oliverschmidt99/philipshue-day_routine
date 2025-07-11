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

        self.current_period = self.get_current_period(datetime.now().astimezone())
        self.last_triggered_scene_name = None
        self.last_motion_time = None
        self.is_in_motion_state = False
        self.motion_logged = False # Neuer Flag für das Logging

    def get_current_period(self, now: datetime):
        """
        Ermittelt den aktuellen Tageszeitraum ('morning', 'day', 'evening', 'night')
        basierend auf der festen Logik.
        """
        current_time = now.time()
        
        start = self.start_time
        end = self.end_time
        sunrise = self.sun_times['sunrise'].time() if self.sun_times else time(6, 30)
        sunset = self.sun_times['sunset'].time() if self.sun_times else time(20, 0)
        
        # Prüft die Zeiträume in einer logischen Reihenfolge
        if start <= current_time < sunrise:
            return "morning"
        if sunrise <= current_time < sunset:
            return "day"
        if sunset <= current_time < end:
            return "evening"
        
        # Alle anderen Zeiten werden als "Nacht" behandelt.
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
        
        if has_motion:
            if not self.motion_logged:
                self.log.info(f"[{self.name}] Bewegung erkannt.")
                self.motion_logged = True
        else:
            self.motion_logged = False


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
                    self.log.info(f"[{self.name}] Aktiviere Bewegungs-Szene: '{scene_to_trigger}'.")
                    self.room.turn_groups(scene_obj)
                    self.last_triggered_scene_name = scene_to_trigger
            self.is_in_motion_state = True
        
        else: # Keine Bewegung
            if self.is_in_motion_state:
                wait_time_conf = section_config.get('wait_time', {'min': 5, 'sec': 0})
                wait_time_delta = timedelta(minutes=wait_time_conf.get('min', 0), seconds=wait_time_conf.get('sec', 0))

                if self.last_motion_time and (now > self.last_motion_time + wait_time_delta):
                    scene_obj = self.scenes.get(normal_scene_name)
                    if scene_obj:
                        self.log.info(f"[{self.name}] Keine Bewegung für {wait_time_delta}. Kehre zu Normal-Szene '{normal_scene_name}' zurück.")
                        self.room.turn_groups(scene_obj)
                        self.last_triggered_scene_name = normal_scene_name
                    
                    self.is_in_motion_state = False
