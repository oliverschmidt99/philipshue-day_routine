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

        self.last_triggered_period = None
        self.last_triggered_scene_name = None
        self.last_motion_time = None

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
        """Gibt den aktuellen Zustand der Routine als Dictionary zurück."""
        return {
            "name": self.name,
            "period": self.last_triggered_period,
            "last_scene": self.last_triggered_scene_name
        }

    def run(self, now: datetime):
        period = self.get_current_period(now)
        if not period:
            if self.last_triggered_period is not None:
                self.log.info(f"[{self.name}] Routine jetzt inaktiv.")
                self.last_triggered_period = None
            return

        section_config = getattr(self, f"{period}_conf", None)
        if not section_config:
            return

        normal_scene_name = section_config.get('scene_name')
        motion_scene_name = section_config.get('x_scene_name')

        if period != self.last_triggered_period:
            scene_obj = self.scenes.get(normal_scene_name)
            if scene_obj:
                self.log.info(f"[{self.name}] Neuer Zeitraum: '{period}'. Setze Normal-Szene: '{normal_scene_name}'.")
                self.room.turn_groups(scene_obj)
                self.last_triggered_scene_name = normal_scene_name
            self.last_triggered_period = period
            self.last_motion_time = None

        if not self.sensor or not section_config.get('motion_check', False):
            return

        if section_config.get('do_not_disturb', False) and self.room.is_any_light_on():
            if self.sensor.get_motion():
                self.last_motion_time = now
            self.log.debug(f"[{self.name}] 'Nicht stören' aktiv und Licht ist an. Ignoriere Trigger.")
            return

        if self.sensor.get_motion():
            self.last_motion_time = now
            
            scene_to_trigger = motion_scene_name
            
            if section_config.get('bri_check', False):
                if self.sensor.get_brightness() > section_config.get('max_light_level', 0):
                    self.log.debug(f"[{self.name}] Zu hell für Bewegungs-Szene. Keine Aktion.")
                    return

            if self.last_triggered_scene_name != scene_to_trigger:
                scene_obj = self.scenes.get(scene_to_trigger)
                if scene_obj:
                    self.log.info(f"[{self.name}] Bewegung erkannt. Aktiviere Bewegungs-Szene: '{scene_to_trigger}'.")
                    self.room.turn_groups(scene_obj)
                    self.last_triggered_scene_name = scene_to_trigger
        
        else:
            wait_time_minutes = section_config.get('wait_time', 5)
            if self.last_motion_time and (now > self.last_motion_time + timedelta(minutes=wait_time_minutes)):
                
                if self.last_triggered_scene_name != normal_scene_name:
                    scene_obj = self.scenes.get(normal_scene_name)
                    if scene_obj:
                        self.log.info(f"[{self.name}] Keine Bewegung für {wait_time_minutes} min. Kehre zu Normal-Szene '{normal_scene_name}' zurück.")
                        self.room.turn_groups(scene_obj)
                        self.last_triggered_scene_name = normal_scene_name
                
                self.last_motion_time = None
