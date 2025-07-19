# tests/conftest.py
import sys
import os
import pytest

# --- WICHTIGER TEIL ---
# Fügt das Hauptverzeichnis (in dem sich der 'src'-Ordner befindet) zum
# Python-Pfad hinzu. Das ist die robusteste Methode, damit pytest
# deine Module im 'src'-Layout findet.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# -----------------------------

# Der Rest des Codes für die Web-Tests bleibt unverändert
from web.server import app as flask_app
from selenium import webdriver

@pytest.fixture(scope="session")
def app():
    """Stellt die Flask-App für die Tests bereit."""
    flask_app.config.update({"TESTING": True})
    yield flask_app

@pytest.fixture(scope="function")
def selenium(app):
    """Startet einen Selenium WebDriver für E2E-Tests."""
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    yield driver
    driver.quit()

def pytest_addoption(parser):
    """Fügt die Kommandozeilen-Option --run-hil hinzu."""
    parser.addoption(
        "--run-hil", action="store_true", default=False, help="Führe Hardware-in-the-Loop-Tests aus"
    )
