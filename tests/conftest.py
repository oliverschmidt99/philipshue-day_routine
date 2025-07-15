# tests/conftest.py
# Diese Datei wird von pytest automatisch für die Konfiguration verwendet.

import pytest
import phue
from unittest.mock import MagicMock
from web.server import app as flask_app

# KORREKTUR: Die app-Fixture ist jetzt 'session'-scoped, genau wie der 'live_server'.
# Die monkeypatch-Fixture wird explizit mit dem korrekten Scope angefordert,
# um den ScopeMismatch-Fehler zu beheben.
@pytest.fixture(scope='session')
def app(request):
    """
    Stellt die Flask-App für pytest-flask zur Verfügung und
    mockt die Bridge-Verbindung für die gesamte Test-Sitzung.
    """
    # Eine session-weite monkeypatch-Instanz anfordern.
    mp = request.getfixturevalue("monkeypatch")

    # Der zentrale Mock für die Bridge-Verbindung
    mock_bridge_instance = MagicMock()
    mock_bridge_instance.get_group.return_value = {'1': {'name': 'Test Raum', 'type': 'Room'}}
    
    mock_sensor = MagicMock()
    mock_sensor.name = 'Test Sensor'
    mock_sensor.type = 'ZLLPresence'
    mock_bridge_instance.get_sensor_objects.return_value = {'2': mock_sensor}
    
    # Jedes Mal, wenn im Code phue.Bridge() aufgerufen wird, wird unser Schein-Objekt zurückgegeben.
    mp.setattr(phue, 'Bridge', lambda ip: mock_bridge_instance)

    # Setzt die App in den Test-Modus
    flask_app.config.update({
        "TESTING": True,
    })
    
    yield flask_app

# NEU: Diese Funktion bringt pytest die neue Kommandozeilen-Option bei.
def pytest_addoption(parser):
    """Fügt die Kommandozeilen-Option --run-hil hinzu."""
    parser.addoption(
        "--run-hil", action="store_true", default=False, help="Führe Hardware-in-the-Loop Tests aus"
    )
