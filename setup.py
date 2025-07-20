import requests
import yaml
import os
import time
from phue import Bridge

# Globale Dateipfade
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'config.yaml')

def discover_bridges():
    """Sucht nach Hue Bridges im lokalen Netzwerk über den Discovery-Dienst."""
    print("Suche nach Hue Bridges im Netzwerk...")
    try:
        response = requests.get('https://discovery.meethue.com/')
        response.raise_for_status()
        bridges = response.json()
        return [b['internalipaddress'] for b in bridges]
    except requests.RequestException as e:
        print(f"Fehler bei der Bridge-Suche: {e}")
        return []

def get_geo_coordinates():
    """Fragt den Benutzer nach Breiten- und Längengrad."""
    while True:
        try:
            lat_str = input("Bitte gib den Breitengrad (Latitude) deines Standorts ein (z.B. 53.58): ").strip()
            lon_str = input("Bitte gib den Längengrad (Longitude) deines Standorts ein (z.B. 7.25): ").strip()
            latitude = float(lat_str)
            longitude = float(lon_str)
            return latitude, longitude
        except ValueError:
            print("Ungültige Eingabe. Bitte gib die Koordinaten als Zahlen ein.")
        except (KeyboardInterrupt, EOFError):
            print("\nEinrichtung abgebrochen.")
            return None, None

def setup():
    """Führt den interaktiven Setup-Prozess durch."""
    print("="*50)
    print("Willkommen zur Einrichtung des Philips Hue Controllers!")
    print("="*50)

    # Schritt 1: Bridge-IP finden
    bridge_ip = None
    discovered_ips = discover_bridges()

    if discovered_ips:
        print("Gefundene Bridges:")
        for i, ip in enumerate(discovered_ips):
            print(f"  [{i+1}] {ip}")
        
        while True:
            choice = input(f"Wähle eine Bridge (1-{len(discovered_ips)}) oder gib eine IP manuell ein: ").strip()
            try:
                if 1 <= int(choice) <= len(discovered_ips):
                    bridge_ip = discovered_ips[int(choice) - 1]
                    break
                else:
                    print("Ungültige Auswahl.")
            except ValueError:
                # Annahme: Es ist eine manuelle IP
                bridge_ip = choice
                break
    else:
        print("Keine Bridges automatisch gefunden.")
        bridge_ip = input("Bitte gib die IP-Adresse deiner Hue Bridge manuell ein: ").strip()

    if not bridge_ip:
        print("Keine IP-Adresse angegeben. Einrichtung abgebrochen.")
        return

    print(f"\nVerwende Bridge-IP: {bridge_ip}")

    # Schritt 2: Mit Bridge verbinden und App-Key erhalten
    try:
        bridge = Bridge(bridge_ip)
        print("\n--> WICHTIG: Bitte drücke jetzt den großen runden Link-Button auf deiner Hue Bridge! <--")
        input("Drücke Enter, sobald du den Button gedrückt hast...")
        
        # Schleife für den Verbindungsversuch
        for i in range(5):
            try:
                bridge.connect()
                print("\nErfolgreich mit der Bridge verbunden und autorisiert!")
                app_key = bridge.username
                break
            except Exception as e:
                if i < 4:
                    print(f"Verbindung fehlgeschlagen ({e}). Versuche es in 5 Sekunden erneut...")
                    time.sleep(5)
                else:
                    print("\nVerbindung konnte nach mehreren Versuchen nicht hergestellt werden.")
                    print("Bitte stelle sicher, dass du den Button gedrückt hast und die IP-Adresse korrekt ist.")
                    return
        
    except Exception as e:
        print(f"\nEin kritischer Fehler ist aufgetreten: {e}")
        return

    # Schritt 3: Standort abfragen
    print("\nFür die dynamische Anpassung an Sonnenauf- und -untergang benötigen wir deinen Standort.")
    latitude, longitude = get_geo_coordinates()
    if latitude is None:
        return

    # Schritt 4: config.yaml erstellen
    print("\nErstelle die Konfigurationsdatei 'config.yaml'...")
    
    config_data = {
        'bridge_ip': bridge_ip,
        'app_key': app_key,
        'location': {'latitude': latitude, 'longitude': longitude},
        'global_settings': {
            'datalogger_interval_minutes': 15,
            'hysteresis_percent': 25,
            'log_level': 'INFO',
            'times': {
                'morning': '06:30',
                'day': '',
                'evening': '',
                'night': '23:00'
            }
        },
        'rooms': [],
        'routines': [],
        'scenes': {
            'off': {'status': False, 'bri': 0},
            'on': {'status': True, 'bri': 254}
        }
    }

    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, sort_keys=False)
        print("'config.yaml' wurde erfolgreich erstellt.")
    except Exception as e:
        print(f"Fehler beim Schreiben der Konfigurationsdatei: {e}")
        return

    print("\n="*50)
    print("Einrichtung abgeschlossen! Du kannst die Anwendung jetzt mit 'python main.py' starten.")
    print("="*50)

if __name__ == "__main__":
    if os.path.exists(CONFIG_FILE):
        overwrite = input("Eine 'config.yaml' existiert bereits. Möchtest du sie überschreiben? (ja/nein): ").lower()
        if overwrite not in ['ja', 'j']:
            print("Einrichtung abgebrochen.")
        else:
            setup()
    else:
        setup()
