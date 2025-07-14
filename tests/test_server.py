# tests/test_server.py

import pytest
import json
import yaml
from unittest.mock import MagicMock

# Wir müssen die App aus der server.py importieren, um sie testen zu können
from web.server import app as flask_app

@pytest.fixture
def app(tmp_path, monkeypatch):
    """
    Eine Pytest Fixture, die unsere Flask-App für Tests konfiguriert.
    - `tmp_path`: Stellt ein temporäres Verzeichnis für Testdateien bereit.
    - `monkeypatch`: Ändert Variablen/Funktionen zur Laufzeit des Tests.
    """
    # Erstelle eine Schein-Konfigurationsdatei im temporären Verzeichnis
    config_file = tmp_path / "config.yaml"
    test_config = {'bridge_ip': '127.0.0.1', 'scenes': {'test_scene': {'status': True}}}
    with open(config_file, 'w') as f:
        yaml.dump(test_config, f)

    # Erstelle eine Schein-Statusdatei
    status_file = tmp_path / "status.json"
    with open(status_file, 'w') as f:
        json.dump([{'name': 'Test Routine', 'status': 'day'}], f)

    # "Patche" die Pfade in der server.py, damit sie auf unsere Testdateien zeigen
    monkeypatch.setattr('web.server.CONFIG_FILE', str(config_file))
    monkeypatch.setattr('web.server.STATUS_FILE', str(status_file))

    # Verhindere, dass der Test versucht, eine echte Bridge-Verbindung aufzubauen
    monkeypatch.setattr('web.server.get_bridge_connection', MagicMock())

    # Setze die App in den Test-Modus
    flask_app.config.update({"TESTING": True})
    
    yield flask_app

@pytest.fixture
def client(app):
    """Eine Fixture, die einen Test-Client für unsere App bereitstellt."""
    return app.test_client()


def test_index_page(client):
    """Testet, ob die Hauptseite (index.html) erfolgreich geladen wird."""
    response = client.get('/')
    # HTTP-Status 200 OK bedeutet Erfolg
    assert response.status_code == 200
    # Prüfe, ob ein bekannter Teil des HTML-Inhalts vorhanden ist
    assert b"Hue Routine und Scene Editor" in response.data

def test_get_config_api(client):
    """Testet den GET-Endpunkt für die Konfiguration."""
    response = client.get('/api/config')
    assert response.status_code == 200
    data = response.get_json()
    # Prüfe, ob die Daten aus unserer Schein-Konfigurationsdatei geladen wurden
    assert data['bridge_ip'] == '127.0.0.1'
    assert 'test_scene' in data['scenes']

def test_post_config_api(client, tmp_path):
    """Testet den POST-Endpunkt zum Speichern der Konfiguration."""
    new_config_data = {
        'bridge_ip': '192.168.1.100',
        'scenes': {'new_scene': {'status': False}}
    }
    
    response = client.post('/api/config', json=new_config_data)
    assert response.status_code == 200
    assert b"Konfiguration gespeichert" in response.data

    # Überprüfung: Wurde die Schein-Datei korrekt mit den neuen Daten überschrieben?
    config_file = tmp_path / "config.yaml"
    with open(config_file, 'r') as f:
        saved_data = yaml.safe_load(f)
    
    assert saved_data['bridge_ip'] == '192.168.1.100'
    assert 'new_scene' in saved_data['scenes']

def test_get_status_api(client):
    """Testet den GET-Endpunkt für den Status."""
    response = client.get('/api/status')
    assert response.status_code == 200
    data = response.get_json()
    # Prüft, ob die Daten aus der Schein-Statusdatei geladen wurden
    assert len(data) == 1
    assert data[0]['name'] == 'Test Routine'

def test_get_bridge_groups_api(client, monkeypatch):
    """Testet den Bridge-Gruppen-Endpunkt mit einer gemockten Bridge."""
    # Erstelle einen neuen Mock für diesen spezifischen Test
    mock_bridge = MagicMock()
    # Definiere, was der Mock zurückgeben soll, wenn get_group() aufgerufen wird
    mock_bridge.get_group.return_value = {
        '1': {'name': 'Wohnzimmer', 'type': 'Room'},
        '2': {'name': 'Lichtleiste', 'type': 'LightGroup'} # Sollte gefiltert werden
    }
    # Sorge dafür, dass unser get_bridge_connection-Mock diesen neuen Mock zurückgibt
    monkeypatch.setattr('web.server.get_bridge_connection', lambda: mock_bridge)

    response = client.get('/api/bridge/groups')
    assert response.status_code == 200
    data = response.get_json()
    
    # Der Endpunkt sollte nur Gruppen vom Typ 'Room' oder 'Zone' zurückgeben
    assert len(data) == 1
    assert data[0]['name'] == 'Wohnzimmer'
