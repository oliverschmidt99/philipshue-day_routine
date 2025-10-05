"""
Definiert eine Datenklasse für eine Lichteinstellung (Szene),
die direkt in einen Hue-API-Aufruf umgewandelt werden kann.
"""
from .logger import AppLogger

class Scene:
    """Repräsentiert eine Lichteinstellung (Szene)."""

    def __init__(
        self,
        status: bool,
        bri: int,
        sat: int = None,
        ct: int = None,
        hue: int = None,
        transitiontime: int = 10,
    ):
        """Initialisiert das Scene-Objekt."""
        self.status = status
        self.bri = bri
        self.sat = sat
        self.ct = ct
        self.hue = hue
        self.transitiontime = transitiontime

    def get_state(self, t_time_overwrite: int = None) -> dict:
        """
        Gibt den Szenen-Zustand als Dictionary für die Hue-API zurück.
        Stellt sicher, dass 'ct' und 'hue' nicht gleichzeitig gesendet werden.
        """
        state = {
            "on": self.status,
            "bri": int(self.bri),
            "transitiontime": (
                t_time_overwrite
                if t_time_overwrite is not None
                else self.transitiontime
            ),
        }

        if not self.status:
            return {"on": False, "transitiontime": state["transitiontime"]}

        if self.hue is not None:
            state["hue"] = int(self.hue)
            if self.sat is not None:
                state["sat"] = int(self.sat)
        elif self.ct is not None:
            state["ct"] = int(self.ct)

        return state