from datetime import datetime, time, timedelta

class Routine:
    """
    Verwaltet die Logik für eine einzelne Routine, die jetzt auch dynamische
    Zeiten basierend auf Sonnenauf- und -untergang verarbeiten kann.
    """
    def __init__(self, name, room, sensor, sections_config, scenes, sun_times, log):
        self.name = name
        self.room = room
        self.sensor = sensor
        self.sections_config = sections_config
        self.scenes = scenes
        self.sun_times = sun_times
        self.log = log
        
        self.last_triggered_scene_name = None
        # Berechne die konkreten Startzeiten für heute einmal beim Start
        self._resolved_times = self._resolve_section_times()

    def _resolve_time_object(self, time_config):
        """Wandelt ein Zeit-Konfigurationsobjekt in ein konkretes datetime.time Objekt um."""
        if not isinstance(time_config, dict):
            # Fallback für altes Format (feste Zeit als String)
            try:
                return datetime.strptime(time_config, '%H:%M').time()
            except (ValueError, TypeError):
                 self.log.warning(f"Ungültiges altes Zeitformat '{time_config}'. Fallback auf 00:00.")
                 return time(0, 0)

        time_type = time_config.get('type')
        
        if time_type == 'fixed':
            return datetime.strptime(time_config.get('value', '00:00'), '%H:%M').time()
        
        # Verarbeite Sonnenauf- und -untergang
        if self.sun_times and time_type in self.sun_times:
            base_time = self.sun_times[time_type] # Dies ist ein datetime-Objekt mit Zeitzone
            offset = timedelta(minutes=time_config.get('offset', 0))
            # Wende den Offset an und gib nur die Zeit zurück
            return (base_time + offset).time()
        
        # Fallback, wenn Sonnenzeiten nicht verfügbar sind oder der Typ unbekannt ist
        self.log.warning(f"Kann Zeit für Typ '{time_type}' nicht auflösen. Fallback auf Mitternacht.")
        return time(0, 0)

    def _resolve_section_times(self):
        """Berechnet einmal alle Startzeiten für die Abschnitte und speichert sie."""
        resolved = {}
        for name, config in self.sections_config.items():
            resolved_time = self._resolve_time_object(config.get('time'))
            resolved[name] = resolved_time
            self.log.info(f"Routine '{self.name}', Abschnitt '{name}': Startzeit für heute ist {resolved_time.strftime('%H:%M:%S')}")
        return resolved

    def _get_current_section(self, now_time: time):
        """Ermittelt den aktuell gültigen Tagesabschnitt basierend auf den aufgelösten Zeiten."""
        # Sortiere die Abschnitte nach ihrer berechneten Startzeit
        sorted_sections = sorted(self._resolved_times.items(), key=lambda item: item[1])
        
        current_section_name = None
        # Finde den letzten Abschnitt, dessen Startzeit vor der aktuellen Zeit liegt
        for name, start_time in sorted_sections:
            if now_time >= start_time:
                current_section_name = name
            else:
                break
        
        # Wenn kein Abschnitt passt (z.B. vor dem ersten), nimm den letzten des Tages (der über Mitternacht geht)
        if current_section_name is None:
            current_section_name = sorted_sections[-1][0]
            
        return current_section_name, self.sections_config[current_section_name]

    def run(self, now: datetime):
        """
        Führt die Routine aus. Prüft Zeit, Bewegung und Helligkeit
        und schaltet das Licht entsprechend.
        'now' muss ein zeitzonen-bewusstes datetime-Objekt sein.
        """
        if not self.sensor.get_motion():
            self.last_triggered_scene_name = None
            return

        # Vergleiche die Zeitkomponente von 'now'
        section_name, config = self._get_current_section(now.time())
        
        scene_to_trigger_name = config.get('scene_name')

        if config.get('bri_check', False):
            current_brightness = self.sensor.get_brightness()
            max_light_level = config.get('max_light_level', 0)
            if current_brightness > max_light_level:
                scene_to_trigger_name = config.get('x_scene_name')

        if scene_to_trigger_name != self.last_triggered_scene_name:
            scene_obj = self.scenes.get(scene_to_trigger_name)
            if scene_obj:
                self.log.info(f"[{self.name}] Bewegung erkannt. Abschnitt: '{section_name}'. Trigger Szene: '{scene_to_trigger_name}'.")
                self.room.turn_groups(scene_obj)
                self.last_triggered_scene_name = scene_to_trigger_name
            else:
                self.log.error(f"[{self.name}] Szene '{scene_to_trigger_name}' nicht in Konfiguration gefunden.")
