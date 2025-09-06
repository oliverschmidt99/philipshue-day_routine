"""
API-Endpunkt für die Hilfe-Seite.
"""

import os
from flask import Blueprint, current_app, jsonify

help_api = Blueprint("help_api", __name__)


@help_api.route("/")
def get_help_content_api():
    """Liest den HTML-Inhalt der Hilfeseite und gibt ihn zurück."""
    try:
        template_folder = current_app.template_folder
        help_file_path = os.path.join(template_folder, "hilfe.html")

        with open(help_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return jsonify({"content": content})
    except FileNotFoundError:
        current_app.logger_instance.error("Hilfedatei 'hilfe.html' nicht gefunden.")
        return jsonify({"error": "Hilfedatei nicht gefunden."}), 404
    except IOError as e:
        current_app.logger_instance.error(f"E/A-Fehler beim Laden der Hilfe: {e}")
        return jsonify({"error": f"Hilfe konnte nicht geladen werden: {e}"}), 500
