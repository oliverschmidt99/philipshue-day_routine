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
        """
        current_time = time.time()
        if current_time - self.last_command_time < command_throttle_s:
            self.log.debug(f"Room '{self.name}': Command throttled. Skipping.")
            return

        self.log.debug(f"Room '{self.name}': Setting groups {self.group_ids} to state: {state}")
        try:
            self.bridge.set_group(self.group_ids, state)
            self.last_command_time = current_time
        except Exception as e:
            self.log.error(f"Failed to set state for room '{self.name}': {e}")

    def is_any_light_on(self):
        """
        Prüft, ob irgendein Licht in dieser Gruppe aktuell eingeschaltet ist.
        """
        if not self.group_ids:
            return False
        try:
            group_state = self.bridge.get_group(self.group_ids[0])
            if group_state and 'state' in group_state:
                return group_state['state'].get('any_on', False)
        except Exception as e:
            self.log.error(f"Konnte den Status für Gruppe {self.group_ids[0]} nicht abrufen: {e}")
            return None
        return False

    def get_current_state(self):
        """
        Holt den aktuellen, detaillierten Lichtzustand der Gruppe von der Bridge.
        Ist robuster gegen fehlende 'action'-Attribute bei bestimmten Gruppentypen.
        """
        if not self.group_ids:
            return None
        try:
            group_id = self.group_ids[0]
            group_data = self.bridge.get_group(group_id)

            # Wir prüfen, ob der 'action'-Schlüssel existiert, bevor wir ihn verwenden.
            if group_data and 'action' in group_data:
                group_action = group_data['action']
                relevant_keys = ['on', 'bri', 'ct', 'hue', 'sat']
                return {key: group_action.get(key) for key in relevant_keys if key in group_action}
            
            # FALLBACK: Wenn 'action' nicht da ist, bauen wir den Status aus 'state'.
            # Das ist weniger präzise, aber verhindert einen Absturz.
            elif group_data and 'state' in group_data:
                self.log.warning(f"Gruppe {group_id} hat keinen 'action'-Zustand. Verwende 'state' als Fallback.")
                group_state = group_data['state']
                # Wir können hier nur 'on' und 'bri' sicher auslesen.
                return {
                    'on': group_state.get('any_on'),
                    'bri': group_state.get('bri') # Hinweis: Dies ist ein Durchschnittswert.
                }

        except Exception as e:
            self.log.error(f"Konnte den Zustand für Gruppe {self.group_ids[0]} nicht abrufen: {e}")
            return None
        
        self.log.warning(f"Konnte keinen gültigen Zustand für Gruppe {self.group_ids[0]} ermitteln.")
        return None
