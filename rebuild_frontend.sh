#!/bin/bash
set -e

# --- Helfer-Funktionen ---
log_info() { echo -e "\e[34m[INFO]\e[0m $1"; }
log_success() { echo -e "\e[32m[ERFOLG]\e[0m $1"; }
log_warning() { echo -e "\e[33m[WARNUNG]\e[0m $1"; }

# --- Haupt-Skript ---
log_info "Starte den Neuaufbau des Frontends..."

# Alte Ordner löschen, falls sie existieren
if [ -d "web" ]; then
    log_warning "Lösche bestehenden 'web' Ordner..."
    rm -rf web
fi
if [ -d "frontend" ]; then
    log_warning "Lösche bestehenden 'frontend' Ordner..."
    rm -rf frontend
fi
log_success "Alte Ordner wurden entfernt."

# Neue Ordnerstruktur erstellen
log_info "Erstelle neue Verzeichnisstruktur..."
mkdir -p web/api
mkdir -p web/static/css
mkdir -p web/static/js
mkdir -p web/static/img
mkdir -p web/templates
log_success "Verzeichnisstruktur erstellt."

# Leere Dateien erstellen
log_info "Erstelle leere Dateien..."
touch web/api/__init__.py
touch web/api/bridge.py
touch web/api/config_api.py
touch web/api/data.py
touch web/api/setup.py
touch web/api/system.py
touch web/static/css/style.css
touch web/static/js/main.js
touch web/templates/base.html
touch web/templates/index.html
touch web/server.py
log_success "Dateien wurden angelegt."

log_info "--------------------------------------------------"
log_success "Frontend-Neuaufbau abgeschlossen!"
log_info "Bitte fülle jetzt die erstellten Dateien mit dem bereitgestellten Inhalt."
log_info "--------------------------------------------------"