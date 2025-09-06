#!/bin/bash
set -e # Bricht das Skript bei Fehlern sofort ab

# Helfer-Funktionen
log_info() { echo -e "\n\e[34m[INFO]\e[0m $1"; }
log_success() { echo -e "\e[32m[ERFOLG]\e[0m $1"; }
log_error() { echo -e "\e[31m[FEHLER]\e[0m $1"; }

# Haupt-Skript
log_info "Starte die Einrichtung des Philips Hue Controllers..."

log_info "Überprüfe und installiere Systemabhängigkeiten..."
if command -v pacman &> /dev/null; then
    sudo pacman -S --needed --noconfirm python python-pip git python-venv
elif command -v apt-get &> /dev/null; then
    sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv git
else
    log_error "Kein unterstützter Paketmanager (pacman oder apt-get) gefunden." && exit 1
fi
log_success "Systemabhängigkeiten sind installiert."

VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    log_info "Erstelle Python Virtual Environment..."
    python3 -m venv "$VENV_DIR"
else
    log_info "Virtual Environment existiert bereits."
fi
log_success "Virtual Environment ist eingerichtet."

log_info "Installiere Python-Pakete..."
source "$VENV_DIR/bin/activate"
pip install -r requirements.txt
deactivate
log_success "Alle Python-Pakete sind installiert."

log_info "Erstelle das 'data' Verzeichnis für Konfiguration und Logs..."
mkdir -p data
# Erstelle eine leere Konfigurationsdatei, falls sie nicht existiert
touch data/config.yaml
log_success "'data' Verzeichnis sichergestellt."

SERVICE_NAME="hue_controller.service"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"
WORKING_DIRECTORY=$(pwd)
VENV_PYTHON_PATH="$WORKING_DIRECTORY/$VENV_DIR/bin/python"
# KORRIGIERT: Verweist jetzt auf die neue app.py
SCRIPT_PATH="$WORKING_DIRECTORY/app.py"

log_info "Erstelle systemd Service-Datei..."
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Philips Hue Advanced Routine Controller
After=network.target

[Service]
ExecStart=$VENV_PYTHON_PATH $SCRIPT_PATH
WorkingDirectory=$WORKING_DIRECTORY
StandardOutput=journal
StandardError=journal
Restart=always
User=$(whoami)
Environment="PYTHONPATH=$WORKING_DIRECTORY"

[Install]
WantedBy=multi-user.target
EOF
log_success "systemd Service-Datei unter $SERVICE_FILE erstellt."

log_info "Lade systemd neu und starte den Service..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
    log_success "Service '$SERVICE_NAME' wurde erfolgreich gestartet und aktiviert."
    log_info "Status: systemctl status $SERVICE_NAME"
    log_info "Logs: journalctl -u $SERVICE_NAME -f"
else
    log_error "Service '$SERVICE_NAME' konnte nicht gestartet werden. Prüfe die Logs für Details."
    exit 1
fi

log_success "Einrichtung abgeschlossen! Die Web-UI ist in Kürze erreichbar."