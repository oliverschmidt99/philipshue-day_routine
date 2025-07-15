# tests/test_hardware.py
# WICHTIG: Diese Tests interagieren mit der echten Hue Bridge und Lampen.
# Sie benötigen eine korrekt konfigurierte `config.yaml`.

import pytest
import time
import yaml
from phue import Bridge

# Wir überspringen diese Tests standardmäßig, da sie manuelle Interaktion erfordern.
# Um sie auszuführen, muss pytest mit der Option --run-hil aufgerufen werden.
pytestmark = pytest.mark.skipif("not config.getoption('--run-hil')")

# --- Hilfsfunktionen für den Test ---

def get_config():
    """Lädt die reale Konfigurationsdatei."""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        pytest.fail("Die Datei 'config.yaml' wurde nicht gefunden. "
                    "Bitte stelle sicher, dass sie im Hauptverzeichnis existiert.")

def connect_to_real_bridge():
    """Stellt eine Verbindung zur echten Hue Bridge her."""
    config = get_config()
    bridge_ip = config.get('bridge_ip')
    if not bridge_ip:
        pytest.fail("In der 'config.yaml' ist keine 'bridge_ip' angegeben.")
    
    print(f"\nVerbinde mit der echten Bridge unter {bridge_ip}...")
    try:
        b = Bridge(bridge_ip)
        b.connect()
        print("Verbindung erfolgreich!")
        return b
    except Exception as e:
        pytest.fail(f"Konnte keine Verbindung zur Bridge herstellen: {e}")

def user_prompt(message):
    """Zeigt eine Anweisung an und wartet auf die Bestätigung des Benutzers."""
    input(f"\n>>> AKTION: {message} (Enter drücken, um fortzufahren)...")

def get_group_state(bridge, group_id):
    """Liest den aktuellen Zustand einer Gruppe von der Bridge."""
    try:
        return bridge.get_group(group_id)
    except Exception as e:
        pytest.fail(f"Fehler beim Abrufen des Gruppenstatus für ID {group_id}: {e}")

# --- Der eigentliche Hardware-in-the-Loop Test ---

def test_motion_routine_on_real_hardware():
    """
    Ein interaktiver Test, der eine Bewegungs-Routine auf der echten Hardware prüft.
    Folge den Anweisungen in der Konsole.
    """
    config = get_config()
    bridge = connect_to_real_bridge()

    # Finde die erste Routine in der Konfiguration, die Bewegungssteuerung nutzt.
    test_routine = None
    for r in config.get('routines', []):
        # Wir suchen eine Routine, die im "day"-Abschnitt eine Bewegungs-Szene hat.
        if r.get('day', {}).get('motion_check') and r.get('day', {}).get('x_scene_name'):
            test_routine = r
            break
    
    if not test_routine:
        pytest.skip("Keine passende Test-Routine mit 'motion_check: true' im 'day'-Abschnitt in der config.yaml gefunden.")

    # Finde die zugehörigen Konfigurationsdetails
    room_name = test_routine['room_name']
    room_config = next((room for room in config['rooms'] if room['name'] == room_name), None)
    if not room_config or not room_config.get('group_ids'):
        pytest.fail(f"Keine Konfiguration oder 'group_ids' für Raum '{room_name}' gefunden.")
    
    group_id = room_config['group_ids'][0]
    motion_scene_name = test_routine['day']['x_scene_name']
    normal_scene_name = test_routine['day']['scene_name']
    wait_seconds = test_routine['day']['wait_time'].get('sec', 0) + test_routine['day']['wait_time'].get('min', 0) * 60

    print("\n--- Starte Hardware-in-the-Loop Test ---")
    print(f"Routine: '{test_routine['name']}'")
    print(f"Raum: '{room_name}' (Gruppe ID: {group_id})")
    print(f"Bewegungs-Szene: '{motion_scene_name}'")
    print(f"Normal-Szene: '{normal_scene_name}'")
    print("-------------------------------------------")

    # Schritt 1: Bewegung auslösen
    user_prompt(f"Bitte löse jetzt den Bewegungsmelder für den Raum '{room_name}' aus.")
    
    print("Warte 5 Sekunden, damit die Szene aktiviert werden kann...")
    time.sleep(5)

    # Schritt 2: Ergebnis überprüfen
    print("Überprüfe den Zustand der Lampe(n)...")
    current_state = get_group_state(bridge, group_id)
    
    assert current_state['state']['any_on'] is True, \
        f"FEHLER: Die Lampen in Gruppe {group_id} wurden nicht eingeschaltet."
    print("ERFOLG: Lampe(n) wurden eingeschaltet.")

    # Schritt 3: Auf das Zurücksetzen warten
    user_prompt(f"Bewegungstest erfolgreich. Bitte sorge dafür, dass KEINE weitere Bewegung ausgelöst wird. "
                f"Der Test wartet jetzt {wait_seconds + 5} Sekunden auf das Zurücksetzen.")
    
    time.sleep(wait_seconds + 5)

    # Schritt 4: Endgültiges Ergebnis überprüfen
    print("Überprüfe den Zustand der Lampe(n) nach der Wartezeit...")
    final_state = get_group_state(bridge, group_id)
    
    # Wir prüfen, ob die Lampe an ist (falls die Normal-Szene 'an' ist) oder aus.
    normal_scene_is_on = config['scenes'][normal_scene_name]['status']
    
    assert final_state['state']['any_on'] == normal_scene_is_on, \
        f"FEHLER: Die Lampen sind nicht in den erwarteten Zustand '{normal_scene_name}' zurückgekehrt."
    
    print(f"ERFOLG: Lampe(n) sind korrekt in den Zustand '{normal_scene_name}' zurückgekehrt.")
    print("\n--- Hardware-in-the-Loop Test abgeschlossen ---")

