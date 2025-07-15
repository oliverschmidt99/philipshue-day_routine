# tests/test_e2e.py
# Verwendet jetzt die zentrale Mock-Konfiguration aus conftest.py

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# Die 'live_server' und 'app' Fixtures werden automatisch bereitgestellt.

@pytest.fixture(scope="function")
def setup_e2e_files(tmp_path, monkeypatch):
    """
    Erstellt für jeden Test temporäre, leere Konfigurationsdateien,
    damit die Tests sich nicht gegenseitig beeinflussen.
    """
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
bridge_ip: '127.0.0.1'
scenes:
  off: {status: false, bri: 0}
routines: []
rooms: []
""")
    status_file = tmp_path / "status.json"
    status_file.write_text("[]")

    monkeypatch.setattr('web.server.CONFIG_FILE', str(config_file))
    monkeypatch.setattr('web.server.STATUS_FILE', str(status_file))


def test_page_title(selenium, live_server, setup_e2e_files):
    """Testet, ob der Titel der Webseite korrekt ist."""
    selenium.get(live_server.url())
    assert "Hue Routine und Scene Editor" in selenium.title

def test_create_new_scene_workflow(selenium, live_server, setup_e2e_files):
    """
    Testet den kompletten Arbeitsablauf zum Erstellen einer neuen Szene.
    """
    selenium.get(live_server.url())
    wait = WebDriverWait(selenium, 10)
    
    scenes_tab = wait.until(EC.element_to_be_clickable((By.ID, "tab-scenes")))
    scenes_tab.click()

    new_scene_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-new-scene")))
    new_scene_button.click()

    modal_scene_name_input = wait.until(EC.visibility_of_element_located((By.ID, "scene-name")))
    scene_name = "E2E Test Szene"
    modal_scene_name_input.send_keys(scene_name)

    save_button_modal = selenium.find_element(By.CSS_SELECTOR, "button[data-action='save-scene']")
    save_button_modal.click()

    wait.until(EC.invisibility_of_element_located((By.ID, "modal-scene")))

    scenes_container = wait.until(EC.visibility_of_element_located((By.ID, "scenes-container")))
    scene_cards = scenes_container.find_elements(By.CSS_SELECTOR, "div.bg-white")
    
    found_scene = any(scene_name.lower() in card.text.lower() for card in scene_cards)
    assert found_scene, f"Die Szene '{scene_name}' wurde nach dem Erstellen nicht auf der Seite gefunden."

def test_create_new_routine_workflow(selenium, live_server, setup_e2e_files):
    """
    Testet den kompletten Arbeitsablauf zum Erstellen einer neuen Routine.
    """
    selenium.get(live_server.url())
    wait = WebDriverWait(selenium, 10)

    new_routine_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-new-routine")))
    new_routine_button.click()

    modal_container = wait.until(EC.visibility_of_element_located((By.ID, "modal-routine")))

    modal_routine_name_input = modal_container.find_element(By.ID, "new-routine-name")
    routine_name = "E2E Test Routine"
    modal_routine_name_input.send_keys(routine_name)

    # Warten, bis die Optionen im Dropdown geladen sind.
    group_dropdown = modal_container.find_element(By.ID, "new-routine-group")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#new-routine-group option:not([value=''])")))
    
    # Jetzt können die Optionen sicher ausgewählt werden.
    Select(group_dropdown).select_by_visible_text("Test Raum")
    Select(modal_container.find_element(By.ID, "new-routine-sensor")).select_by_visible_text("Test Sensor (ID: 2)")

    create_button_modal = modal_container.find_element(By.CSS_SELECTOR, "button[data-action='create-routine']")
    create_button_modal.click()

    wait.until(EC.invisibility_of_element_located((By.ID, "modal-routine")))

    routines_container = wait.until(EC.visibility_of_element_located((By.ID, "routines-container")))
    assert routine_name in routines_container.text
    assert "Raum: Test Raum" in routines_container.text
