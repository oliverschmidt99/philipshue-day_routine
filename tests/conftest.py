# tests/conftest.py
import sys
import os
import pytest
import yaml
from unittest.mock import MagicMock, patch

# Fügt das Hauptverzeichnis zum Python-Pfad hinzu
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Mocke die Bridge, bevor die App importiert wird
mock_bridge = MagicMock()
mock_bridge.get_api.return_value = {
    "lights": {"1": {"name": "Test Lampe"}},
    "groups": {"1": {"name": "Test Raum", "lights": ["1"]}},
    "sensors": {"1": {"name": "Test Sensor", "type": "ZLLPresence"}},
}

# Wichtig: Patch muss VOR dem Import von 'web.server' passieren
with patch("phue.Bridge", return_value=mock_bridge):
    from web.server import app as flask_app


@pytest.fixture(scope="session")
def app():
    """Stellt die Flask-App für die Tests bereit."""
    flask_app.config.update({"TESTING": True})

    # Mocke die globalen Manager der App, um auf Test-Dateien zuzugreifen
    with flask_app.app_context():
        yield flask_app


@pytest.fixture
def client(app):
    """Ein Test-Client für die Flask-App."""
    return app.test_client()


@pytest.fixture(scope="function")
def setup_test_files(tmp_path, monkeypatch):
    """Erstellt für jeden Test eine saubere Konfigurations- und Statusdatei."""
    config_file = tmp_path / "config.yaml"
    test_config = {
        "bridge_ip": "127.0.0.1",
        "app_key": "testkey",
        "scenes": {"off": {"status": False, "bri": 0}},
        "rooms": [{"name": "Test Raum", "group_id": 1, "sensor_id": 1}],
        "routines": [
            {
                "name": "Test Routine",
                "room_name": "Test Raum",
                "enabled": True,
                "daily_time": {"H1": 7, "M1": 0, "H2": 23, "M2": 0},
                "day": {"scene_name": "off", "motion_check": False},
            }
        ],
    }
    with open(config_file, "w") as f:
        yaml.dump(test_config, f)

    status_file = tmp_path / "status.json"
    status_file.write_text('{"routines": [], "sun_times": null}')

    # Überschreibe die Pfade in der server.py Instanz
    monkeypatch.setattr("web.server.CONFIG_FILE", str(config_file))
    monkeypatch.setattr("web.server.STATUS_FILE", str(status_file))

    # Wichtig: Auch den ConfigManager in der App neu initialisieren
    from src.config_manager import ConfigManager
    from web.server import log

    monkeypatch.setattr(
        "web.server.config_manager", ConfigManager(str(config_file), log)
    )

    return config_file, status_file
