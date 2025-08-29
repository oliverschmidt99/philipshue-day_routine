# tests/test_server.py
import json
import yaml

# Die Fixtures 'client' und 'setup_test_files' werden automatisch aus conftest.py geladen


def test_index_page(client):
    """Testet, ob die Hauptseite (index.html) erfolgreich geladen wird."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Hue Routine und Scene Editor" in response.data


def test_get_config_api(client, setup_test_files):
    """Testet den GET-Endpunkt für die Konfiguration."""
    response = client.get("/api/config/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["bridge_ip"] == "127.0.0.1"
    assert "Test Routine" in [r["name"] for r in data["routines"]]


def test_post_config_api(client, setup_test_files):
    """Testet den POST-Endpunkt zum Speichern der Konfiguration."""
    config_file, _ = setup_test_files
    new_config_data = {"bridge_ip": "192.168.1.100", "routines": []}

    response = client.post("/api/config/", json=new_config_data)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Konfiguration erfolgreich gespeichert."

    with open(config_file, "r") as f:
        saved_data = yaml.safe_load(f)
    assert saved_data["bridge_ip"] == "192.168.1.100"


def test_get_status_api(client, setup_test_files):
    """Testet den GET-Endpunkt für den Status."""
    _, status_file = setup_test_files
    # Schreibe einen Test-Status in die Datei
    with open(status_file, "w") as f:
        json.dump([{"name": "Test Routine", "period": "day"}], f)

    response = client.get("/api/data/status")
    assert response.status_code == 200
    # Die API gibt jetzt rohen JSON-Text zurück, der manuell geparst werden muss
    data = json.loads(response.data)
    assert data[0]["name"] == "Test Routine"


def test_get_bridge_items_api(client, setup_test_files):
    """Testet den Bridge-Items-Endpunkt mit einer gemockten Bridge."""
    # Der Mock ist bereits durch die app-Fixture in conftest.py aktiv.
    response = client.get("/api/bridge/all_items")
    assert response.status_code == 200
    data = response.get_json()

    assert len(data["groups"]) == 1
    assert data["groups"][0]["name"] == "Test Raum"
    assert len(data["sensors"]) == 1
    assert data["sensors"][0]["name"] == "Test Sensor"
