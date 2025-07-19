# tests/test_e2e.py
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

# Die 'live_server' und 'app' Fixtures werden automatisch bereitgestellt.

@pytest.fixture(scope="function")
def setup_e2e_files(tmp_path, monkeypatch):
    """Erstellt für jeden Test eine saubere Konfigurations- und Statusdatei."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
bridge_ip: '127.0.0.1'
location: {latitude: 52.0, longitude: 8.0}
global_settings: {hysteresis_percent: 25, datalogger_interval_minutes: 15, log_level: 'INFO'}
scenes:
  off: {status: false, bri: 0}
  on_test: {status: true, bri: 200, ct: 300}
rooms: []
routines: []
""")
    status_file = tmp_path / "status.json"
    status_file.write_text("[]")

    monkeypatch.setattr('web.server.CONFIG_FILE', str(config_file))
    monkeypatch.setattr('web.server.STATUS_FILE', str(status_file))

def test_full_navigation_and_all_buttons(selenium, live_server, setup_e2e_files):
    """Testet die Navigation durch alle Tabs und die Funktionalität aller wichtigen Knöpfe."""
    selenium.get(live_server.url())
    wait = WebDriverWait(selenium, 10)

    # --- 1. Tab-Navigation testen ---
    tabs = ['tab-routines', 'tab-scenes', 'tab-status', 'tab-analyse', 'tab-einstellungen', 'tab-hilfe']
    for tab_id in tabs:
        print(f"Teste Navigation zu Tab: {tab_id}")
        tab_button = wait.until(EC.element_to_be_clickable((By.ID, tab_id)))
        tab_button.click()
        # Warten, bis der zugehörige Content-Bereich sichtbar ist
        content_id = tab_id.replace('tab-', 'content-')
        wait.until(EC.visibility_of_element_located((By.ID, content_id)))
        # Überprüfen, ob der Tab als aktiv markiert ist
        assert "tab-active" in tab_button.get_attribute("class")

    # --- 2. Test der Einstellungs-Knöpfe ---
    # Zum Einstellungs-Tab zurückkehren
    wait.until(EC.element_to_be_clickable((By.ID, 'tab-einstellungen'))).click()
    
    # Teste den 'Speichern' Knopf
    ip_input = wait.until(EC.visibility_of_element_located((By.ID, 'setting-bridge-ip')))
    ip_input.clear()
    ip_input.send_keys("1.2.3.4")
    wait.until(EC.element_to_be_clickable((By.ID, 'btn-save-settings'))).click()
    # Toast-Nachricht prüfen
    toast = wait.until(EC.visibility_of_element_located((By.ID, 'toast')))
    assert "Einstellungen gespeichert" in toast.text
    
    # Teste System-Aktionen (Beispiel: Backup)
    # HINWEIS: Neustart und andere Aktionen sind im E2E-Test schwierig zu validieren.
    # Wir testen hier nur, ob der Klick eine Reaktion auslöst (z.B. eine Toast-Nachricht).
    # Hier müsste man die API mocken oder komplexere Logik einbauen.
    
    # --- 3. Test der Analyse-Seite ---
    wait.until(EC.element_to_be_clickable((By.ID, 'tab-analyse'))).click()
    # Warten bis Sensor-Optionen geladen sind
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#analyse-sensor option")))
    # Klick auf "Daten laden"
    wait.until(EC.element_to_be_clickable((By.ID, 'btn-fetch-data'))).click()
    # Prüfen, ob das Chart-Canvas da ist
    wait.until(EC.visibility_of_element_located((By.ID, 'sensor-chart')))
    print("Analyse-Seite erfolgreich geladen.")

    # --- 4. Test Routine an/aus schalten ---
    wait.until(EC.element_to_be_clickable((By.ID, 'tab-routines'))).click()
    # Zuerst eine Routine erstellen (Code von deinem 'test_create_new_routine_workflow' Test)
    wait.until(EC.element_to_be_clickable((By.ID, "btn-new-routine"))).click()
    modal = wait.until(EC.visibility_of_element_located((By.ID, "modal-routine")))
    modal.find_element(By.ID, "new-routine-name").send_keys("Schaltbare Routine")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#new-routine-group option:not([value=''])")))
    Select(modal.find_element(By.ID, "new-routine-group")).select_by_visible_text("Test Raum")
    modal.find_element(By.CSS_SELECTOR, "button[data-action='create-routine']").click()
    wait.until(EC.invisibility_of_element_located((By.ID, "modal-routine")))

    # Nun den Schalter testen
    toggle_switch = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[data-action='toggle-routine']")))
    # Sicherstellen, dass er anfangs an ist ('checked')
    assert toggle_switch.is_selected()
    # Ausschalten
    toggle_switch.find_element(By.XPATH, "./..").click() # Klick auf das Label, um den Schalter umzulegen
    time.sleep(0.5) # Kurze Pause, damit der State sich ändern kann
    assert not toggle_switch.is_selected()
    print("Routine an/aus Schalter funktioniert.")