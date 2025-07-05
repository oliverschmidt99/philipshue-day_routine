import time
import yaml
from datetime import datetime, date
from phue import Bridge
from astral.sun import sun
# Wir gehen zurück zu LocationInfo, da dies mit mehr Versionen kompatibel ist
from astral import LocationInfo

from control.scene import Scene
from control.Room import Room
from control.Sensor import Sensor
from control.Routine import Routine
from control.logger import Logger

CONFIG_FILE = 'config.yaml'

def load_config():
    """Lädt die Konfiguration aus der YAML-Datei."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Fehler: Die Konfigurationsdatei '{CONFIG_FILE}' wurde nicht gefunden.")
        exit()
    except Exception as e:
        print(f"Fehler beim Laden der Konfiguration: {e}")
        exit()

def connect_bridge(ip, log):
    """Stellt die Verbindung zur Hue Bridge her."""
    log.info(f"Versuche, eine Verbindung zur Bridge unter {ip} herzustellen...")
    try:
        b = Bridge(ip)
        b.connect()
        log.info("Verbindung zur Hue Bridge erfolgreich hergestellt.")
        return b
    except Exception as e:
        log.error(f"Konnte keine Verbindung zur Bridge herstellen: {e}", exc_info=True)
        exit()

def get_sun_times(location_config, log):
    """Berechnet die Sonnenauf- und -untergangszeiten für den aktuellen Tag."""
    if not location_config:
        log.warning("Keine Standort-Informationen in config.yaml gefunden. Sonnenzeiten können nicht berechnet werden.")
        return None
    try:
        # KORRIGIERT: Wir verwenden jetzt die kompatiblere LocationInfo-Klasse.
        # Name und Region sind Platzhalter, aber die API erwartet sie.
        # Die Zeitzone ist wichtig für die korrekte Berechnung.
        # Wir übergeben 'elevation' nicht mehr, da es den ursprünglichen Fehler verursacht hat.
        loc = LocationInfo(
            "Home",
            "Germany",
            "Europe/Berlin",
            location_config['latitude'],
            location_config['longitude']
        )
        
        # Berechne die Sonnenzeiten für das heutige Datum.
        s = sun(loc.observer, date=date.today(), tzinfo=loc.timezone)
        
        log.info(f"Sonnenzeiten für heute berechnet: Aufgang={s['sunrise'].strftime('%H:%M')}, Untergang={s['sunset'].strftime('%H:%M')}")
        return {
            "sunrise": s['sunrise'],
            "sunset": s['sunset']
        }
    except Exception as e:
        log.error(f"Fehler bei der Berechnung der Sonnenzeiten: {e}", exc_info=True)
        return None

def main():
    """Initialisiert und startet die Lichtsteuerung."""
    log = Logger("info.log")
    log.info("Starte Philips Hue Routine...")

    config = load_config()
    if not config:
        return

    try:
        bridge = connect_bridge(config['bridge_ip'], log)
        sun_times = get_sun_times(config.get('location'), log)
        
        scenes = {name: Scene(**params) for name, params in config.get('scenes', {}).items()}
        
        rooms = {room_conf['name']: Room(bridge, log, **room_conf) for room_conf in config.get('rooms', [])}
        
        sensors = {room_conf['name']: Sensor(bridge, room_conf['sensor_id'], log) for room_conf in config.get('rooms', [])}

        routines = []
        for routine_conf in config.get('routines', []):
            room = rooms.get(routine_conf['room_name'])
            sensor = sensors.get(routine_conf['room_name'])
            
            if not room or not sensor:
                log.error(f"Raum oder Sensor für Routine '{routine_conf['name']}' nicht gefunden. Überspringe.")
                continue

            routine = Routine(
                name=routine_conf['name'],
                room=room,
                sensor=sensor,
                sections_config=routine_conf.get('sections', {}),
                scenes=scenes,
                sun_times=sun_times, # Übergebe die Sonnenzeiten
                log=log
            )
            routines.append(routine)
            log.info(f"Routine '{routine.name}' für Raum '{room.name}' erfolgreich geladen.")

        if not routines:
            log.warning("Keine Routinen zum Ausführen gefunden. Beende.")
            return

        log.info("Initialisierung abgeschlossen. Starte Hauptschleife.")
        while True:
            # Hole die aktuelle Zeit mit Zeitzoneninformationen des Systems
            now = datetime.now().astimezone() 
            for routine in routines:
                routine.run(now)
            time.sleep(1)

    except (KeyboardInterrupt, SystemExit):
        log.info("Programm wird beendet.")
    except Exception as e:
        log.error(f"Ein kritischer Fehler ist aufgetreten: {e}", exc_info=True)

if __name__ == "__main__":
    main()
