# src/daily_time_span.py
from datetime import time


class DailyTimeSpan:
    """
    Bestimmt die aktuelle Tagesperiode (Morgen, Tag, Abend, Nacht)
    basierend auf festen Zeiten und Sonnenauf- bzw. -untergang.
    """

    def __init__(self, start_time, end_time, sun_times, log):
        self.morning_start = start_time
        self.evening_end = end_time
        self.sun_times = sun_times
        self.log = log

    def get_current_period(self, now):
        """Gibt den Namen des aktuellen Zeitraums zurück."""
        current_time = now.time()

        sunrise_t = time(6, 30)
        sunset_t = time(21, 0)
        if (
            self.sun_times
            and self.sun_times.get("sunrise")
            and self.sun_times.get("sunset")
        ):
            sunrise_t = self.sun_times["sunrise"].time()
            sunset_t = self.sun_times["sunset"].time()

        if self.morning_start <= current_time < sunrise_t:
            return "morning"
        if sunrise_t <= current_time < sunset_t:
            return "day"
        if sunset_t <= current_time < self.evening_end:
            return "evening"

        return "night"
