# tests/conftest.py
# Diese Datei wird von pytest automatisch für die Konfiguration verwendet.

import pytest
from web.server import app as flask_app

@pytest.fixture(scope='session')
def app():
    """
    Stellt die Flask-App für pytest-flask zur Verfügung.
    'scope="session"' bedeutet, dass dies nur einmal pro Testlauf geschieht.
    """
    # Setzt die App in den Test-Modus
    flask_app.config.update({
        "TESTING": True,
    })
    
    yield flask_app
