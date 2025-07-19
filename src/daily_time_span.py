from datetime import time, datetime

class DailyTimeSpan:
    """
    Verwaltet die Zeitberechnungen für eine tägliche Routine.
    Die Logik zur Bestimmung der Periode (Morgen, Tag, Abend, Nacht)
    folgt einer strikten if/elif/else Kette, um die korrekte Priorität
    sicherzustellen.
    """

    def __init__(self, start_time, end_time, sun_times, log):
        """
        Initialisiert das DailyTimeSpan-Objekt.

        Args:
            start_time (datetime.time): Die Startzeit für die "Morgen"-Periode.
            end_time (datetime.time): Die Endzeit für die "Abend"-Periode.
            sun_times (dict): Ein Dictionary mit 'sunrise' und 'sunset' datetime-Objekten.
            log: Das Logger-Objekt.
        """
        self.morning_start = start_time
        self.evening_end = end_time
        self.sun_times = sun_times
        self.log = log

    def get_current_period(self, now):
        """
        Gibt den Namen des aktuellen Zeitraums zurück, basierend auf der
        bewährten, priorisierten if/elif/else Logik.
        """
        current_time = now.time()
        
        # Holen der Sonnenzeiten mit einem Fallback
        sunrise_t = time(6, 30)
        sunset_t = time(21, 0)
        if self.sun_times and self.sun_times.get('sunrise') and self.sun_times.get('sunset'):
            sunrise_t = self.sun_times['sunrise'].time()
            sunset_t = self.sun_times['sunset'].time()
        else:
            self.log.warning("Keine Sonnenzeiten verfügbar. Verwende Fallback-Zeiten für Perioden-Berechnung.")

        # Hier wird die Logik aus deinem alten Skript exakt nachgebildet:
        
        # 1. Priorität: Ist es "Tag"? (zwischen Sonnenaufgang und -untergang)
        if sunrise_t <= current_time < sunset_t:
            return 'day'
        else:
            # 2. Priorität: Wenn nicht Tag, ist es "Morgen"? (zwischen Routine-Start und Sonnenaufgang)
            if self.morning_start <= current_time < sunrise_t:
                return 'morning'
            # 3. Priorität: Wenn nicht Tag oder Morgen, ist es "Abend"? (zwischen Sonnenuntergang und Routine-Ende)
            elif sunset_t <= current_time < self.evening_end:
                return 'evening'
            # 4. Priorität: Wenn nichts von alledem zutrifft, muss es "Nacht" sein.
            else:
                return 'night'