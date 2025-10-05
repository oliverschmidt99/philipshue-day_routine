# src/daily_time_span.py
from datetime import time, datetime


class DailyTimeSpan:
    """
    Bestimmt die aktuelle Tagesperiode (Morgen, Tag, Abend, Nacht)
    basierend auf festen Zeiten und Sonnenauf- bzw. -untergang.
    """

    def __init__(self, start_time: time, end_time: time, sun_times: dict | None, log):
        self.morning_start = start_time
        self.evening_end = end_time
        self.log = log

        # Fallback-Zeiten, falls keine Sonnenzeiten verfügbar sind
        self.sunrise_t = time(6, 30)
        self.sunset_t = time(21, 0)

        if sun_times and sun_times.get("sunrise") and sun_times.get("sunset"):
            self.sunrise_t = sun_times["sunrise"].time()
            self.sunset_t = sun_times["sunset"].time()

    def is_active(self, now: datetime) -> bool:
        """Prüft, ob die aktuelle Uhrzeit im aktiven Gesamtzeitraum liegt."""
        current_time = now.time()
        # Normaler Fall: Startzeit < Endzeit (z.B. 07:00 - 23:00)
        if self.morning_start <= self.evening_end:
            return self.morning_start <= current_time < self.evening_end
        # Fall über Mitternacht: Startzeit > Endzeit (z.B. 22:00 - 06:00)
        else:
            return current_time >= self.morning_start or current_time < self.evening_end

    def get_current_period(self, now: datetime) -> str:
        """Gibt den Namen des aktuellen Zeitraums zurück."""
        if not self.is_active(now):
            return "night"

        current_time = now.time()

        if self.morning_start <= current_time < self.sunrise_t:
            return "morning"
        if self.sunrise_t <= current_time < self.sunset_t:
            return "day"
        if self.sunset_t <= current_time < self.evening_end:
            return "evening"

        # Fallback, falls die Logik oben nicht greift (z.B. bei Zeiten über Mitternacht)
        return "night"