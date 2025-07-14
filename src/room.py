# src/room.py

# Die Import-Anweisung wurde angepasst, um aus demselben Paket zu importieren
from .scene import Scene

class Room:
    """
    Represents a room and controls its associated light groups.

    Uses the phue Bridge object to send commands.
    """
    def __init__(self, bridge, log, name, group_ids, **kwargs):
        """Initializes the Room object."""
        self.bridge = bridge
        self.log = log
        self.name = name
        self.group_ids = group_ids

    def turn_groups(self, scene: Scene, t_time_overwrite: int = None):
        """
        Sets all light groups in this room to a specific scene.

        Args:
            scene: The Scene object to apply.
            t_time_overwrite: Optional transition time in 1/10 seconds.
        """
        if not isinstance(scene, Scene):
            self.log.error(f"Invalid scene type for room '{self.name}'.")
            return

        state = scene.get_state(t_time_overwrite)
        self.log.info(f"Room '{self.name}': Setting groups {self.group_ids} to state: {state}")

        for group_id in self.group_ids:
            try:
                self.bridge.set_group(int(group_id), state)
            except Exception as e:
                self.log.error(f"Error setting group {group_id} in room '{self.name}': {e}")

    def is_any_light_on(self) -> bool:
        """
        Checks if at least one light is on in any of this room's groups.

        Returns:
            True if any light is on, False otherwise.
        """
        for group_id in self.group_ids:
            try:
                group_state = self.bridge.get_group(int(group_id))
                if group_state and group_state.get('state', {}).get('any_on', False):
                    self.log.debug(f"Room '{self.name}', group {group_id}: Light is on.")
                    return True
            except Exception as e:
                self.log.error(f"Error getting group status for {group_id}: {e}")
                continue
        return False
