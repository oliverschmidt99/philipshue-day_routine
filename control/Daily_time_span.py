from datetime import time

class Daily_time_span:
    """
    Definiert einen täglichen Zeitbereich und prüft, ob eine
    gegebene Zeit innerhalb dieses Bereichs liegt.
    """
    def __init__(self, H1, M1, H2, M2):
        self.time_start = time(H1, M1)
        self.time_end = time(H2, M2)

    def check_time(self, t_now):
        """
        Prüft, ob die aktuelle Zeit `t_now` (ein datetime-Objekt)
        innerhalb des definierten Zeitraums liegt.
        """
        current_time = t_now.time()
        
        # Fall 1: Zeitspanne geht nicht über Mitternacht (z.B. 08:00 - 22:00)
        if self.time_start <= self.time_end:
            return self.time_start <= current_time <= self.time_end
        # Fall 2: Zeitspanne geht über Mitternacht (z.B. 22:00 - 06:00)
        else:
            return self.time_start <= current_time or current_time <= self.time_end
