from datetime import time, datetime, timedelta

class DailyTimeSpan:
    """
    Verwaltet die Zeitberechnungen für eine tägliche Routine, einschließlich der
    dynamischen Bestimmung von Morgen, Tag, Abend und Nacht basierend auf
    Sonnenauf- und -untergang.
    """

    def __init__(self, start_time, end_time, sun_times, time_spans_config, log):
        """
        Initialisiert das DailyTimeSpan-Objekt.

        Args:
            start_time (datetime.time): Die allgemeine Startzeit der Routine.
            end_time (datetime.time): Die allgemeine Endzeit der Routine.
            sun_times (dict): Ein Dictionary mit 'sunrise' und 'sunset' Objekten.
            time_spans_config (dict): Konfiguration für die einzelnen Zeiträume.
            log: Das Logger-Objekt.
        """
        self.overall_start = start_time
        self.overall_end = end_time
        self.sun_times = sun_times
        self.time_spans_config = time_spans_config
        self.log = log
        self.periods = self._calculate_periods()

    def _resolve_time(self, time_str):
        """Wandelt einen String ('sunrise', 'sunset', 'HH:MM') in ein time-Objekt um."""
        if isinstance(time_str, time):
            return time_str
        if self.sun_times:
            if time_str == 'sunrise':
                return self.sun_times['sunrise'].time()
            if time_str == 'sunset':
                return self.sun_times['sunset'].time()
        # Fallback, falls Sonnenzeiten nicht verfügbar sind
        elif time_str in ['sunrise', 'sunset']:
             self.log.warning(f"'{time_str}' kann nicht aufgelöst werden, da keine Sonnenzeiten verfügbar sind. Verwende 06:00/18:00.")
             return time(6, 0) if time_str == 'sunrise' else time(18, 0)
        
        return datetime.strptime(time_str, '%H:%M').time()

    def _calculate_periods(self):
        """Berechnet die Start- und Endzeiten für jeden Zeitraum."""
        periods = {}
        if not self.time_spans_config:
            self.log.error("Keine 'time_spans_config' zum Berechnen der Perioden vorhanden.")
            return periods
            
        for name, (start_str, end_str) in self.time_spans_config.items():
            try:
                start_time = self._resolve_time(start_str)
                end_time = self._resolve_time(end_str)
                periods[name] = (start_time, end_time)
            except Exception as e:
                self.log.error(f"Fehler beim Berechnen der Periode '{name}': {e}")
        return periods

    def is_active(self, current_time):
        """Prüft, ob die Routine zur aktuellen Zeit insgesamt aktiv ist."""
        # Behandelt den Fall, dass die Routine über Mitternacht läuft (z.B. 22:00 - 06:00)
        if self.overall_start > self.overall_end:
            return current_time >= self.overall_start or current_time < self.overall_end
        return self.overall_start <= current_time < self.overall_end

    def get_current_period(self, now):
        """Gibt den Namen des aktuellen Zeitraums (z.B. 'day') zurück."""
        current_time = now.time()
        if not self.is_active(current_time):
            return None

        for name, (start, end) in self.periods.items():
            # Behandelt den Fall, dass ein Zeitraum über Mitternacht läuft
            if start > end:
                if current_time >= start or current_time < end:
                    return name
            # Normaler Fall
            elif start <= current_time < end:
                return name
        
        self.log.debug(f"Für die Zeit {current_time} wurde keine passende Periode gefunden.")
        return None
