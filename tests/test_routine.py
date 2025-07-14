# tests/test_routine.py

from datetime import datetime, time, timedelta
import pytest
from unittest.mock import MagicMock

# Wir müssen die zu testende Klasse importieren
from src.routine import Routine

@pytest.fixture
def mock_dependencies():
    """Erstellt Schein-Objekte für alle Abhängigkeiten der Routine."""
    mock_room = MagicMock()
    mock_room.turn_groups = MagicMock()
    # Standardmäßig ist kein Licht an
    mock_room.is_any_light_on.return_value = False
    
    mock_sensor = MagicMock()
    mock_sensor.get_motion.return_value = False
    mock_sensor.get_brightness.return_value = 10000

    mock_log = MagicMock()
    
    scenes = {
        'day_normal': MagicMock(),
        'day_motion': MagicMock(),
        'off': MagicMock()
    }

    sun_times = {
        'sunrise': datetime.now().replace(hour=6, minute=0),
        'sunset': datetime.now().replace(hour=21, minute=0)
    }
    
    return {
        "room": mock_room,
        "sensor": mock_sensor,
        "scenes": scenes,
        "sun_times": sun_times,
        "log": mock_log
    }

@pytest.fixture
def routine_config():
    """Stellt eine Standard-Testkonfiguration für eine Routine bereit."""
    return {
        'name': "Test Routine",
        'enabled': True,
        'daily_time': {'H1': 7, 'M1': 0, 'H2': 23, 'M2': 0},
        'day': {
            'scene_name': 'day_normal',
            'x_scene_name': 'day_motion',
            'motion_check': True,
            'wait_time': {'min': 0, 'sec': 5},
            'do_not_disturb': False
        }
    }

def test_routine_period_change(routine_config, mock_dependencies):
    """Testet, ob beim Wechsel des Zeitraums die korrekte Default-Szene gesetzt wird."""
    routine = Routine(
        name="Test Period Change",
        routine_config=routine_config,
        **mock_dependencies
    )
    
    now = datetime.now().replace(hour=14, minute=0)
    routine.run(now)
    
    mock_dependencies['room'].turn_groups.assert_called_once_with(
        mock_dependencies['scenes']['day_normal']
    )
    assert routine.current_period == 'day'

def test_routine_motion_detection_triggers_scene(routine_config, mock_dependencies):
    """Testet, ob bei Bewegung die Bewegungs-Szene aktiviert wird."""
    routine = Routine(
        name="Test Motion",
        routine_config=routine_config,
        **mock_dependencies
    )
    
    now = datetime.now().replace(hour=14, minute=0)
    routine.current_period = 'day' 
    
    mock_dependencies['sensor'].get_motion.return_value = True
    routine.run(now)
    
    mock_dependencies['room'].turn_groups.assert_called_once_with(
        mock_dependencies['scenes']['day_motion']
    )
    assert routine.is_in_motion_state is True

def test_routine_reverts_after_motion_stops(routine_config, mock_dependencies):
    """Testet, ob nach Ablauf der Wartezeit zur normalen Szene zurückgekehrt wird."""
    routine = Routine(
        name="Test Revert",
        routine_config=routine_config,
        **mock_dependencies
    )

    # --- Phase 1: Bewegung löst Szene aus ---
    time_motion_starts = datetime.now().replace(hour=14, minute=0, second=0)
    routine.current_period = 'day'
    mock_dependencies['sensor'].get_motion.return_value = True
    routine.run(time_motion_starts)
    
    mock_dependencies['room'].turn_groups.assert_called_once_with(mock_dependencies['scenes']['day_motion'])
    
    # --- Phase 2: Keine Bewegung mehr, aber Wartezeit noch nicht um ---
    mock_dependencies['sensor'].get_motion.return_value = False
    time_after_motion = time_motion_starts + timedelta(seconds=4)
    routine.run(time_after_motion)
    
    mock_dependencies['room'].turn_groups.assert_called_once()
    
    # --- Phase 3: Wartezeit ist abgelaufen ---
    time_wait_over = time_motion_starts + timedelta(seconds=6)
    routine.run(time_wait_over)
    
    assert mock_dependencies['room'].turn_groups.call_count == 2
    mock_dependencies['room'].turn_groups.assert_called_with(mock_dependencies['scenes']['day_normal'])
    assert routine.is_in_motion_state is False

# =================================================================
# NEUE TESTS ZUR ERHÖHUNG DER TESTABDECKUNG UND KONFIGURATIONS-VALIDIERUNG
# =================================================================

def test_routine_is_disabled(routine_config, mock_dependencies):
    """Testet, dass eine deaktivierte Routine keine Aktionen ausführt."""
    routine_config['enabled'] = False
    routine = Routine(
        name="Disabled Test",
        routine_config=routine_config,
        **mock_dependencies
    )
    now = datetime.now().replace(hour=14, minute=0)
    routine.run(now)

    # Es darf kein Aufruf zum Schalten der Lichter erfolgen
    mock_dependencies['room'].turn_groups.assert_not_called()

def test_do_not_disturb_prevents_trigger(routine_config, mock_dependencies):
    """Testet, ob 'do_not_disturb' das Auslösen bei Bewegung verhindert, wenn Licht bereits an ist."""
    # Aktiviere "Bitte nicht stören" in der Test-Konfiguration
    routine_config['day']['do_not_disturb'] = True
    
    routine = Routine(
        name="Do Not Disturb Test",
        routine_config=routine_config,
        **mock_dependencies
    )
    
    # Simuliere, dass das Licht im Raum bereits an ist
    mock_dependencies['room'].is_any_light_on.return_value = True
    # Simuliere eine Bewegung
    mock_dependencies['sensor'].get_motion.return_value = True
    
    now = datetime.now().replace(hour=14, minute=0)
    routine.current_period = 'day'
    routine.run(now)
    
    # Die Lichter dürfen nicht geschaltet werden, da "Bitte nicht stören" aktiv ist
    mock_dependencies['room'].turn_groups.assert_not_called()

def test_routine_handles_missing_period_config(routine_config, mock_dependencies):
    """Testet, ob die Routine nicht abstürzt, wenn die Konfiguration für einen Zeitabschnitt fehlt."""
    # Entferne die Konfiguration für den 'day'-Abschnitt
    del routine_config['day']
    
    routine = Routine(
        name="Missing Config Test",
        routine_config=routine_config,
        **mock_dependencies
    )
    now = datetime.now().replace(hour=14, minute=0) # Es ist "Tag"
    
    # Die Ausführung sollte einfach nichts tun und keinen Fehler werfen
    try:
        routine.run(now)
    except Exception as e:
        pytest.fail(f"Routine ist mit fehlender Konfiguration abgestürzt: {e}")

    # Es darf kein Aufruf zum Schalten der Lichter erfolgen
    mock_dependencies['room'].turn_groups.assert_not_called()

def test_routine_falls_back_without_sun_times(routine_config, mock_dependencies):
    """Testet, ob die Routine die Fallback-Zeiten verwendet, wenn keine Sonnenzeiten übergeben werden."""
    # Setze sun_times auf None, um den Fallback zu erzwingen
    mock_dependencies['sun_times'] = None
    
    routine = Routine(
        name="Fallback Time Test",
        routine_config=routine_config,
        **mock_dependencies
    )
    
    # Diese Zeit liegt nach dem Fallback-Sonnenaufgang (6:30)
    now = datetime.now().replace(hour=8, minute=0)
    period = routine.get_current_period(now)
    
    # Der Zeitraum sollte trotzdem als "Tag" erkannt werden
    assert period == 'day'

def test_motion_is_ignored_if_motion_check_is_false(routine_config, mock_dependencies):
    """Testet, ob Bewegung ignoriert wird, wenn motion_check deaktiviert ist."""
    # Deaktiviere die Bewegungsprüfung in der Konfiguration
    routine_config['day']['motion_check'] = False
    
    routine = Routine(
        name="No Motion Check Test",
        routine_config=routine_config,
        **mock_dependencies
    )
    
    # Simuliere eine Bewegung
    mock_dependencies['sensor'].get_motion.return_value = True
    
    now = datetime.now().replace(hour=14, minute=0)
    routine.current_period = 'day'
    routine.run(now)
    
    # Es darf kein Aufruf zum Schalten der Lichter erfolgen, weil die Prüfung deaktiviert ist
    mock_dependencies['room'].turn_groups.assert_not_called()
