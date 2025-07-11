class Scene:
    """
    Repräsentiert eine Lichteinstellung (Szene).
    Kann entweder eine Farbtemperatur (ct) oder einen Farbton (hue) speichern.
    """
    def __init__(self, status: bool, bri: int, sat: int = None, ct: int = None, hue: int = None, t_time: int = 10) -> None:
        self.status = status
        self.bri = bri
        self.sat = sat
        self.ct = ct
        self.hue = hue # Neuer Parameter für den Farbton
        self.t_time = t_time

    def get_state(self, t_time_overwrite: int = None) -> dict:
        """
        Gibt den Zustand der Szene als Dictionary für die Hue-API zurück.
        Stellt sicher, dass 'ct' und 'hue' nicht gleichzeitig gesendet werden.
        """
        transition_time = t_time_overwrite if t_time_overwrite is not None else self.t_time
        
        state = {
            "on": self.status,
            "bri": self.bri,
            "transitiontime": transition_time
        }
        
        # Eine Szene ist entweder eine Farbszene (mit hue) oder eine Weißton-Szene (mit ct)
        if self.hue is not None:
            state['hue'] = self.hue
            # Sättigung ist für Farbszenen relevant
            if self.sat is not None:
                state['sat'] = self.sat
        elif self.ct is not None:
            state['ct'] = self.ct
            # Sättigung kann auch für Weißtöne verwendet werden, um sie "pastelliger" zu machen
            if self.sat is not None:
                state['sat'] = self.sat
        
        return state
