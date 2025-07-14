# src/daily_time_span.py

from datetime import time

class DailyTimeSpan:
    """
    Defines a daily time range and checks if a given time is within it.
    """
    def __init__(self, H1, M1, H2, M2):
        """Initializes the time span from H1:M1 to H2:M2."""
        self.time_start = time(H1, M1)
        self.time_end = time(H2, M2)

    def check_time(self, t_now: time):
        """
        Checks if the current time is within the defined span.

        Handles time spans that cross midnight.
        """
        # KORREKTUR: Wir verwenden t_now direkt, da es bereits ein time-Objekt ist.
        current_time = t_now
        
        if self.time_start <= self.time_end:
            # e.g., 08:00 - 22:00
            return self.time_start <= current_time <= self.time_end
        else:
            # e.g., 22:00 - 06:00
            return self.time_start <= current_time or current_time <= self.time_end
