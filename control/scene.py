class Scene:
    """
    Repräsentiert eine Lichteinstellung (Szene) mit allen relevanten Parametern.
    """
    def __init__(self, status: bool, bri: int, sat: int, ct: int, t_time: int) -> None:
        """
        :param status: Ein- (True) oder Ausgeschaltet (False)
        :param bri: Helligkeit (0-254)
        :param sat: Sättigung (0-254)
        :param ct: Farbtemperatur (153-500)
        :param t_time: Übergangszeit in 1/10 Sekunden
        """
        self.status = status
        self.bri = bri
        self.sat = sat
        self.ct = ct
        self.t_time = t_time

    def get_state(self, t_time_overwrite: int = None) -> dict:
        """
        Gibt den Zustand der Szene als Dictionary für die Hue-API zurück.
        Ermöglicht das Überschreiben der Übergangszeit.
        """
        transition_time = t_time_overwrite if t_time_overwrite is not None else self.t_time
        return {
            "on": self.status,
            "bri": self.bri,
            "sat": self.sat,
            "ct": self.ct,
            "transitiontime": transition_time
        }
