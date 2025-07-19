# tests/test_hardware.py
import pytest
import time
import yaml
from phue import Bridge
from datetime import datetime, time as dt_time

# Importiere die Klassen, die wir für den Test brauchen
from src.room import Room
from src.scene import Scene
from src.sensor import Sensor
from src.routine import Routine
from src.logger import logger

# Stellt sicher, dass diese Tests nur mit --run-hil ausgeführt werden
pytestmark = pytest.mark.skipif("not config.getoption('--run-hil')")

# --- Test-Setup ---

@pytest.fixture(scope="module")
def hardware_bridge():
    """Stellt einmalig die Bridge-Verbindung für alle HIL-Tests bereit."""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        bridge = Bridge(config['bridge_ip'])
        bridge.connect()
        print(f"\nVerbindung zur echten Bridge unter {config['bridge_ip']} erfolgreich!")
        return bridge
    except Exception as e:
        pytest.fail(f"Konnte keine Verbindung zur Bridge herstellen: {e}")

def user_prompt(message):
    """Zeigt eine Anweisung an und wartet auf Bestätigung."""
    input(f"\n>>> AKTION ERFORDERLICH: {message}\n    (Enter drücken, um den Test fortzusetzen)...")

# --- Die neue, vereinfachte Test-Suite ---

class TestGuidedHardwareScenarios:

    ROUTINE_NAME = "TEST"

    def setup_test_environment(self, hardware_bridge):
        """Lädt die Konfig und erstellt die notwendigen Objekte für einen Test."""
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        routine_conf = next((r for r in config.get('routines', []) if r['name'] == self.ROUTINE_NAME), None)
        if not routine_conf:
            pytest.fail(f"Routine '{self.ROUTINE_NAME}' nicht in config.yaml gefunden.")

        scenes = {name: Scene(**params) for name, params in config.get('scenes', {}).items()}
        room_conf = next((r for r in config.get('rooms', []) if r['name'] == routine_conf['room_name']), None)
        if not room_conf:
            pytest.fail(f"Raum '{routine_conf['room_name']}' für Routine '{self.ROUTINE_NAME}' nicht in config.yaml gefunden.")
            
        sensor_conf = next((s for s in config.get('sensors', []) if s['id'] == room_conf.get('sensor_id')), None)

        room = Room(hardware_bridge, logger, **room_conf)
        sensor = Sensor(hardware_bridge, sensor_conf['id'], logger) if sensor_conf else None
        
        routine = Routine(
            name=routine_conf['name'], room=room, sensor=sensor,
            routine_config=routine_conf, scenes=scenes, sun_times=None, log=logger, global_settings=config.get('global_settings', {})
        )
        return routine, room

    @pytest.mark.parametrize("period, mock_hour, scene_name, color_name", [
        ("Morning", 8, "blau", "BLAU"),
        ("Day", 14, "red", "ROT"),
        ("Evening", 20, "grün", "GRÜN"),
        ("Night", 2, "gelb", "GELB"),
    ])
    def test_scenario_1_time_based_scene_change(self, hardware_bridge, period, mock_hour, scene_name, color_name):
        """
        Testet Szenario 1: Wird die korrekte, farbige Normal-Szene zur richtigen Zeit aktiviert?
        """
        if period == "Morning":
            user_prompt(
                "--- SETUP FÜR SZENARIO 1 ---\n"
                f"Bitte konfiguriere die Routine '{self.ROUTINE_NAME}' in der UI wie folgt:\n"
                "  - Für ALLE Zeiträume:\n"
                "    - Auf Bewegung reagieren: NEIN\n"
                "    - Normal-Szene: 'blau' (Morning), 'red' (Day), 'grün' (Evening), 'gelb' (Night)\n"
                "  - Speichere die Routine ab."
            )
        
        routine, room = self.setup_test_environment(hardware_bridge)
        fake_time = datetime.now().replace(hour=mock_hour, minute=0, second=0)
        print(f"\n--- Starte Test 1 ({period}) mit simulierter Zeit: {fake_time.strftime('%H:%M')} ---")

        routine.run(fake_time)
        
        user_prompt(f"Die Lichter sollten jetzt auf {color_name} geschaltet sein. Bitte visuell prüfen.")
        
        group_state = hardware_bridge.get_group(room.group_ids[0])
        assert group_state['state']['any_on'], f"FEHLER ({period}): Licht ist nicht an."
        print(f"ERFOLG ({period}): Die korrekte Szene wurde aktiviert.")

    def test_scenario_2_motion_reaction(self, hardware_bridge):
        """Testet Szenario 2: Korrekte Reaktion auf Bewegung."""
        user_prompt(
            "--- SETUP FÜR SZENARIO 2 ---\n"
            f"Bitte konfiguriere die Routine '{self.ROUTINE_NAME}' in der UI wie folgt:\n"
            "  - Für den Zeitraum 'Day':\n"
            "    - Auf Bewegung reagieren: JA (Wartezeit z.B. 10s)\n"
            "    - Normal-Szene: 'off'\n"
            "    - Szene bei Bewegung: 'cold_max'\n"
            "  - Speichere die Routine ab."
        )

        routine, room = self.setup_test_environment(hardware_bridge)
        hardware_bridge.set_group(room.group_ids[0], 'on', False)
        time.sleep(1)

        print("\n--- Starte Test 2 (Bewegungserkennung) ---")
        user_prompt("Löse jetzt den Bewegungsmelder aus.")
        
        routine.run(datetime.now().replace(hour=14))
        time.sleep(2) # Gib der Bridge Zeit zu reagieren

        group_state = hardware_bridge.get_group(room.group_ids[0])
        assert group_state['state']['any_on'], "FEHLER: Licht wurde bei Bewegung nicht eingeschaltet."
        print("ERFOLG: Licht wurde bei Bewegung korrekt eingeschaltet.")

        user_prompt("Sorge nun dafür, dass KEINE Bewegung mehr erkannt wird. Der Test wartet 15s auf das Zurücksetzen.")
        time.sleep(15)
        
        # Simuliere eine spätere Zeit für den Reset-Check
        routine.run(datetime.now().replace(hour=14, minute=1))
        time.sleep(2)

        group_state = hardware_bridge.get_group(room.group_ids[0])
        assert not group_state['state']['any_on'], "FEHLER: Licht wurde nach Wartezeit nicht ausgeschaltet."
        print("ERFOLG: Licht wurde korrekt zurückgesetzt.")

    def test_scenario_3_brightness_check(self, hardware_bridge):
        """Testet Szenario 3: Die Helligkeitsprüfung."""
        user_prompt(
            "--- SETUP FÜR SZENARIO 3 ---\n"
            f"Bitte konfiguriere die Routine '{self.ROUTINE_NAME}' in der UI wie folgt:\n"
            "  - Für den Zeitraum 'Day':\n"
            "    - Auf Bewegung reagieren: JA\n"
            "    - Helligkeits-Check: JA\n"
            "    - Normal-Szene: 'off'\n"
            "    - Szene bei Bewegung: 'cold_max'\n"
            "  - Speichere die Routine ab."
        )

        routine, room = self.setup_test_environment(hardware_bridge)
        hardware_bridge.set_group(room.group_ids[0], 'on', False)
        time.sleep(1)

        print("\n--- Starte Test 3.1 (Umgebung ist hell) ---")
        user_prompt("Sorge dafür, dass der Lichtsensor HELLIGKEIT misst (z.B. anleuchten) und löse dann die Bewegung aus.")
        routine.run(datetime.now().replace(hour=14))
        time.sleep(2)
        
        group_state_bright = hardware_bridge.get_group(room.group_ids[0])
        assert not group_state_bright['state']['any_on'], "FEHLER (Hell): Licht ging an, obwohl es hell war."
        print("ERFOLG (Hell): Licht ist wie erwartet aus geblieben.")

        print("\n--- Starte Test 3.2 (Umgebung ist dunkel) ---")
        user_prompt("Sorge nun dafür, dass der Lichtsensor DUNKELHEIT misst (z.B. abdecken) und löse dann die Bewegung aus.")
        routine.run(datetime.now().replace(hour=14))
        time.sleep(2)

        group_state_dark = hardware_bridge.get_group(room.group_ids[0])
        assert group_state_dark['state']['any_on'], "FEHLER (Dunkel): Licht ging nicht an, obwohl es dunkel war."
        print("ERFOLG (Dunkel): Licht wurde korrekt eingeschaltet.")

    def test_scenario_4_do_not_disturb(self, hardware_bridge):
        """Testet Szenario 4: Die 'Bitte nicht stören'-Funktion."""
        user_prompt(
            "--- SETUP FÜR SZENARIO 4 ---\n"
            f"Bitte konfiguriere die Routine '{self.ROUTINE_NAME}' in der UI wie folgt:\n"
            "  - Für den Zeitraum 'Day':\n"
            "    - Auf Bewegung reagieren: JA\n"
            "    - Normal-Szene: 'warm_mid' (eine Szene, die AN ist)\n"
            "  - Speichere die Routine ab."
        )

        routine, room = self.setup_test_environment(hardware_bridge)
        
        print("\n--- Starte Test 4 ('Bitte nicht stören') ---")
        user_prompt("Schalte das Licht im Raum manuell AUS (z.B. per App).")
        time.sleep(2) # Warte kurz, damit der Zustand auf der Bridge aktuell ist

        # Simuliere einen Durchlauf, bei dem die Routine den Konflikt erkennen sollte
        routine.run(datetime.now().replace(hour=14))
        assert routine.do_not_disturb, "FEHLER: 'do_not_disturb' wurde nach manueller Änderung nicht aktiviert."
        print("ERFOLG: 'do_not_disturb' wurde nach manueller Änderung korrekt aktiviert.")

        user_prompt("Löse jetzt den Bewegungsmelder aus. Das Licht sollte aus bleiben.")
        routine.run(datetime.now().replace(hour=14))
        time.sleep(2)

        group_state = hardware_bridge.get_group(room.group_ids[0])
        assert not group_state['state']['any_on'], "FEHLER: Licht wurde trotz 'do_not_disturb' eingeschaltet."
        print("ERFOLG: Licht ist aus geblieben, 'do_not_disturb' funktioniert!")

