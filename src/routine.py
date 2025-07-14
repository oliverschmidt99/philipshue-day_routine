# src/routine.py

from datetime import datetime, time, timedelta

# Die Import-Anweisung wurde angepasst, um aus demselben Paket zu importieren
from .scene import Scene

class Routine:
    """
    Implements the daily logic for a room.

    This class manages transitions between different time periods of the day
    (morning, day, evening, night) and handles motion-based scene changes.
    """
    def __init__(self, name, room, sensor, routine_config, scenes, sun_times, log):
        """Initializes the Routine object."""
        self.name = name
        self.room = room
        self.sensor = sensor
        self.log = log
        self.scenes = scenes
        self.sun_times = sun_times
        self.enabled = routine_config.get('enabled', True)

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
        self.motion_logged = False

    def get_current_period(self, now: datetime):
        """
        Determines the current time period ('morning', 'day', 'evening', 'night').

        Args:
            now: The current datetime object.

        Returns:
            The name of the current period as a string, or None if inactive.
        """
        current_time = now.time()
        start = self.start_time
        end = self.end_time

        is_active = (start <= end and start <= current_time < end) or \
                    (start > end and (current_time >= start or current_time < end))
        
        if not is_active:
            return None

        # Fallback-Werte, falls keine Sonnenzeiten verfügbar sind
        sunrise = self.sun_times['sunrise'].time() if self.sun_times and 'sunrise' in self.sun_times else time(6, 30)
        sunset = self.sun_times['sunset'].time() if self.sun_times and 'sunset' in self.sun_times else time(20, 0)

        if start <= current_time < sunrise:
            return "morning"
        elif sunrise <= current_time < sunset:
            return "day"
        elif sunset <= current_time < end:
            return "evening"
        else:
            return "night"

    def get_status(self):
        """Returns the current state of the routine for the UI."""
        current_period_for_status = self.get_current_period(datetime.now().astimezone())
        
        motion_status_text = "Nicht relevant"
        is_motion_active_now = False
        if self.sensor:
            is_motion_active_now = self.sensor.get_motion()
            if is_motion_active_now:
                motion_status_text = f"Aktiv seit {self.last_motion_time:%H:%M:%S}" if self.last_motion_time else "Aktiv"
            elif self.is_in_motion_state and self.last_motion_time:
                 motion_status_text = f"Letzte Bewegung um {self.last_motion_time:%H:%M:%S}"
            else:
                motion_status_text = "Keine Bewegung"

        return {
            "name": self.name,
            "enabled": self.enabled,
            "period": current_period_for_status,
            "last_scene": self.last_triggered_scene_name,
            "motion_status": motion_status_text,
            "motion_active": is_motion_active_now
        }

    def run(self, now: datetime):
        """Executes the routine logic for the current time."""
        if not self.enabled:
            if self.current_period is not None:
                self.log.info(f"[{self.name}] Routine deaktiviert, wird übersprungen.")
                self.current_period = None
            return

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
            self.log.info(f"---------- Zustands-Wechsel für Routine '{self.name}' ----------")
            self.log.info(f"Neuer Zustand: {period.upper()}")
            scene_obj = self.scenes.get(normal_scene_name)
            if scene_obj:
                self.log.info(f"Setze Normal-Szene: '{normal_scene_name}'.")
                self.room.turn_groups(scene_obj)
                self.last_triggered_scene_name = normal_scene_name
            self.current_period = period
            self.last_motion_time = None
            self.is_in_motion_state = False

        if not self.sensor or not section_config.get('motion_check', False):
            return

        has_motion = self.sensor.get_motion()
        
        if has_motion and not self.motion_logged:
            self.log.info(f"[{self.name}] Bewegung erkannt.")
            self.motion_logged = True
        elif not has_motion:
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
                wait_delta = timedelta(minutes=wait_time_conf.get('min', 0), seconds=wait_time_conf.get('sec', 0))

                if self.last_motion_time and (now > self.last_motion_time + wait_delta):
                    scene_obj = self.scenes.get(normal_scene_name)
                    if scene_obj:
                        self.log.info(f"[{self.name}] Keine Bewegung für {wait_delta}. Kehre zu '{normal_scene_name}' zurück.")
                        self.room.turn_groups(scene_obj)
                        self.last_triggered_scene_name = normal_scene_name
                    
                    self.is_in_motion_state = False
