# tests/test_server.py

import pytest
import json
import yaml

# Die 'client' und 'app' Fixtures werden automatisch von pytest-flask bereitgestellt.
# Die 'app' Fixture aus conftest.py sorgt dafür, dass die Bridge-Verbindung
# bereits für die gesamte Sitzung gemockt ist.

@pytest.fixture(scope="function")
def setup_api_files(tmp_path, monkeypatch):
    """Setzt temporäre Dateien für jeden API-Test auf."""
    config_file = tmp_path / "config.yaml"
    test_config = {'bridge_ip': '127.0.0.1', 'scenes': {'test_scene': {'status': True}}}
    with open(config_file, 'w') as f:
        yaml.dump(test_config, f)

    status_file = tmp_path / "status.json"
    with open(status_file, 'w') as f:
        json.dump([{'name': 'Test Routine', 'status': 'day'}], f)

    # Die Tests sollen auf diese temporären Dateien zugreifen.
    monkeypatch.setattr('web.server.CONFIG_FILE', str(config_file))
    monkeypatch.setattr('web.server.STATUS_FILE', str(status_file))


def test_index_page(client, setup_api_files):
    """Testet, ob die Hauptseite (index.html) erfolgreich geladen wird."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Hue Routine und Scene Editor" in response.data

def test_get_config_api(client, setup_api_files):
    """Testet den GET-Endpunkt für die Konfiguration."""
    response = client.get('/api/config')
    assert response.status_code == 200
    data = response.get_json()
    assert data['bridge_ip'] == '127.0.0.1'

def test_post_config_api(client, tmp_path, setup_api_files):
    """Testet den POST-Endpunkt zum Speichern der Konfiguration."""
    new_config_data = {'bridge_ip': '192.168.1.100'}
    
    response = client.post('/api/config', json=new_config_data)
    assert response.status_code == 200

    config_file = tmp_path / "config.yaml"
    with open(config_file, 'r') as f:
        saved_data = yaml.safe_load(f)
    assert saved_data['bridge_ip'] == '192.168.1.100'

def test_get_status_api(client, setup_api_files):
    """Testet den GET-Endpunkt für den Status."""
    response = client.get('/api/status')
    assert response.status_code == 200
    data = response.get_json()
    assert data[0]['name'] == 'Test Routine'

def test_get_bridge_groups_api(client, setup_api_files):
    """Testet den Bridge-Gruppen-Endpunkt mit einer gemockten Bridge."""
    # Der Mock ist bereits durch die app-Fixture in conftest.py aktiv.
    response = client.get('/api/bridge/groups')
    assert response.status_code == 200
    data = response.get_json()
    
    assert len(data) == 1
    # KORREKTUR: Der Test erwartet jetzt den Namen aus dem Mock in conftest.py.
    assert data[0]['name'] == 'Test Raum'
