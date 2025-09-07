"""
API-Endpunkt für die Hilfe-Seite.
"""

from flask import Blueprint, jsonify, render_template

help_api = Blueprint("help_api", __name__)

@help_api.route("/")
def get_help_content():
    """Rendert den Inhalt der Hilfe-Seite und gibt ihn als JSON zurück."""
    try:
        # Wir rendern das Template, um z.B. Jinja-Variablen zu verarbeiten
        content = render_template("hilfe.html")
        return jsonify({"content": content})
    except Exception as e:
        return jsonify({"error": f"Hilfe konnte nicht geladen werden: {e}"}), 500