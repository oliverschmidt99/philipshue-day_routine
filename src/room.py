import time

class Room:
    """Represents a room or a zone in the Hue system."""

    def __init__(self, bridge, log, name, group_ids, **kwargs):
        """Initializes the Room object."""
        self.bridge = bridge
        self.log = log
        self.name = name
        self.group_ids = [int(gid) for gid in group_ids]
        self.last_command_time = 0

    def apply_state(self, state, command_throttle_s=1):
        """
        Sets the state for all light groups in the room.

        Args:
            state (dict): The state to set (e.g., {'on': True, 'bri': 128}).
            command_throttle_s (int): Minimum time in seconds between commands.
        """
        current_time = time.time()
        if current_time - self.last_command_time < command_throttle_s:
            self.log.debug(f"Room '{self.name}': Command throttled. Skipping.")
            return

        self.log.debug(f"Room '{self.name}': Setting groups {self.group_ids} to state: {state}")
        try:
            # The phue library can take a list of group IDs
            self.bridge.set_group(self.group_ids, state)
            self.last_command_time = current_time
        except Exception as e:
            self.log.error(f"Failed to set state for room '{self.name}': {e}")

