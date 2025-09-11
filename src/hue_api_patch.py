import requests
import json
from phue import Bridge, PhueException

# Speichere die originale request-Methode, falls wir sie je wieder brauchen
_original_phue_request = Bridge.request

def patched_request(self, method='GET', url=None, data=None):
    """
    Eine gepatchte Version der request-Methode, die HTTPS verwendet
    und die SSL-Zertifikatsprüfung deaktiviert.
    """
    if url is None:
        url = '/api/' + self.username
    
    # Erstelle die URL mit https
    full_url = f"https://{self.ip}{url}"

    try:
        # Führe den Request mit deaktivierter SSL-Prüfung (verify=False) aus
        if data is not None:
            response = requests.request(method, full_url, data=json.dumps(data), timeout=10, verify=False)
        else:
            response = requests.request(method, full_url, timeout=10, verify=False)
        
        # Deaktiviere Warnungen über unsichere Anfragen in der Konsole
        requests.packages.urllib3.disable_warnings()

        # Gib den Text der Antwort zurück
        return response.text
    except requests.RequestException as e:
        raise PhueException(99, f"Netzwerkfehler bei der HTTPS-Anfrage: {e}") from e


def apply_https_patch():
    """Wendet den Patch auf die phue.Bridge Klasse an."""
    if Bridge.request is not patched_request:
        print("Wende HTTPS-Patch für phue-Bibliothek an...")
        Bridge.request = patched_request