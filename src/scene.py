# src/scene.py
# (Inhaltlich unverändert, nur Kommentare bereinigt)

class Scene:
    """Represents a light setting (scene)."""
    def __init__(self, status: bool, bri: int, sat: int = None, ct: int = None, hue: int = None, t_time: int = 10):
        """Initializes the Scene object."""
        self.status = status
        self.bri = bri
        self.sat = sat
        self.ct = ct
        self.hue = hue
        self.t_time = t_time

    def get_state(self, t_time_overwrite: int = None) -> dict:
        """
        Returns the scene state as a dictionary for the Hue API.

        Ensures that 'ct' and 'hue' are not sent simultaneously.
        """
        transition_time = t_time_overwrite if t_time_overwrite is not None else self.t_time
        
        state = {
            "on": self.status,
            "bri": self.bri,
            "transitiontime": transition_time
        }
        
        if self.hue is not None:
            state['hue'] = self.hue
            if self.sat is not None:
                state['sat'] = self.sat
        elif self.ct is not None:
            state['ct'] = self.ct
            if self.sat is not None:
                state['sat'] = self.sat
        
        return state