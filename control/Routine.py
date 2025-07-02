from datetime import datetime

class Routine:
    """
    Verwaltet die Logik für eine einzelne Routine, die einen Raum,
    einen Sensor und einen Zeitplan miteinander verbindet.
    """
    def __init__(self, name, room, sensor, daily_time_span, sections_config, scenes, log):
        self.name = name
        self.room = room
        self.sensor = sensor
        self.daily_time_span = daily_time_span
        self.sections_config = sections_config
        self.scenes = scenes
        self.log = log
        
        # Sortierte Liste der Tagesabschnitte nach Zeit
        self.sorted_sections = sorted(
            sections_config.items(), 
            key=lambda item: datetime.strptime(item[1]['time'], '%H:%M').time()
        )
        self.last_triggered_scene_name = None

    def _get_current_section(self, now_time):
        """Ermittelt den aktuell gültigen Tagesabschnitt."""
        current_section = None
        # Finde den letzten Abschnitt, dessen Startzeit vor der aktuellen Zeit liegt
        for name, config in self.sorted_sections:
            section_time = datetime.strptime(config['time'], '%H:%M').time()
            if now_time >= section_time:
                current_section = (name, config)
            else:
                break
        # Wenn kein Abschnitt passt (z.B. vor dem ersten Abschnitt), nimm den letzten des Tages
        return current_section if current_section else self.sorted_sections[-1]

    def run(self, now: datetime):
        """
        Führt die Routine aus. Prüft Zeit, Bewegung und Helligkeit
        und schaltet das Licht entsprechend.
        """
        if not self.daily_time_span.check_time(now):
            return # Routine ist außerhalb des aktiven Zeitraums

        if not self.sensor.get_motion():
            self.last_triggered_scene_name = None # Reset bei keiner Bewegung
            return # Keine Bewegung, nichts zu tun

        section_name, config = self._get_current_section(now.time())
        
        scene_to_trigger_name = config.get('scene_name')

        if config.get('bri_check', False):
            current_brightness = self.sensor.get_brightness()
            max_light_level = config.get('max_light_level', 0)
            if current_brightness > max_light_level:
                self.log.info(f"[{self.name}] Helligkeit ({current_brightness}) > Max ({max_light_level}). Wechsle zu alternativer Szene.")
                scene_to_trigger_name = config.get('x_scene_name')

        # Nur schalten, wenn sich die Zielszenen geändert hat, um Flackern zu vermeiden
        if scene_to_trigger_name != self.last_triggered_scene_name:
            scene_obj = self.scenes.get(scene_to_trigger_name)
            if scene_obj:
                self.log.info(f"[{self.name}] Bewegung erkannt. Abschnitt: '{section_name}'. Trigger Szene: '{scene_to_trigger_name}'.")
                self.room.turn_groups(scene_obj)
                self.last_triggered_scene_name = scene_to_trigger_name
            else:
                self.log.error(f"[{self.name}] Szene '{scene_to_trigger_name}' nicht in Konfiguration gefunden.")
