import requests
import json

class HueBridge:
    """
    Verwaltet die Kommunikation mit der Philips Hue Bridge.
    """
    def __init__(self, ip, log):
        self.ip = ip
        self.log = log
        self.username = "HT5fC1p2k2OFg9bJ5L-DFo1aNFRMv-VnSAxGk5Y8" # Dein Hue-API-Benutzername
        self.base_url = f"http://{self.ip}/api/{self.username}"
        self.session = requests.Session()
        self.log.info(f"HueBridge für IP {self.ip} initialisiert.")

    def _request(self, method, endpoint, data=None):
        """Führt eine Anfrage an die Hue Bridge aus und behandelt Fehler."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.request(method, url, data=json.dumps(data) if data else None, timeout=5)
            response.raise_for_status()  # Wirft eine Ausnahme bei HTTP-Fehlern (z.B. 404, 500)
            
            # Die Hue API gibt manchmal eine Liste mit einem Fehler-Objekt zurück
            response_data = response.json()
            if isinstance(response_data, list) and response_data:
                first_item = response_data[0]
                if 'error' in first_item:
                    self.log.error(f"Hue API Fehler bei '{method} {url}': {first_item['error']}")
                    return None
            return response_data
        
        except requests.exceptions.RequestException as e:
            self.log.error(f"Netzwerkfehler bei der Kommunikation mit der Hue Bridge: {e}")
            return None
        except json.JSONDecodeError:
            self.log.error(f"Fehler beim Parsen der JSON-Antwort von der Hue Bridge.")
            return None

    def get_sensor(self, sensor_id):
        """Ruft die Daten eines bestimmten Sensors ab."""
        return self._request('GET', f'sensors/{sensor_id}')

    def get_group(self, group_id):
        """Ruft die Daten einer bestimmten Gruppe ab."""
        return self._request('GET', f'groups/{group_id}')

    def set_group(self, group_id, state):
        """Setzt den Zustand einer Gruppe."""
        return self._request('PUT', f'groups/{group_id}/action', data=state)
