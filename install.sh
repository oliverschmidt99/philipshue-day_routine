#!/bin/bash

# Funktion für farbige Ausgaben
log_info() {
    echo -e "\e[34m[INFO]\e[0m $1"
}

log_success() {
    echo -e "\e[32m[ERFOLG]\e[0m $1"
}

log_error() {
    echo -e "\e[31m[FEHLER]\e[0m $1"
}

# --- Skriptstart ---
log_info "Starte die Einrichtung des Philips Hue Controllers..."

# 1. Systemabhängigkeiten basierend auf dem verfügbaren Paketmanager installieren
log_info "Überprüfe und installiere Systemabhängigkeiten (benötigt eventuell sudo-Passwort)..."

# Prüfe auf pacman (Arch Linux, EndeavourOS, etc.)
if command -v pacman &> /dev/null; then
    log_info "Paketmanager 'pacman' gefunden (Arch-basiertes System)."
    PACKAGES="python python-pip gcc"
    if ! sudo pacman -S --needed --noconfirm $PACKAGES; then
        log_error "Installation der Systemabhängigkeiten mit pacman fehlgeschlagen."
        exit 1
    fi
# Prüfe auf apt-get (Debian, Ubuntu, Raspberry Pi OS, etc.)
elif command -v apt-get &> /dev/null; then
    log_info "Paketmanager 'apt-get' gefunden (Debian-basiertes System)."
    PACKAGES="python3 python3-pip python3-venv gcc"
    if ! sudo apt-get update || ! sudo apt-get install -y $PACKAGES; then
        log_error "Installation der Systemabhängigkeiten mit apt-get fehlgeschlagen."
        exit 1
    fi
else
    log_error "Kein unterstützter Paketmanager (pacman oder apt-get) gefunden."
    exit 1
fi
log_success "Systemabhängigkeiten sind installiert."


# 2. Python Virtual Environment erstellen
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    log_info "Erstelle Python Virtual Environment in '$VENV_DIR'..."
    python3 -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        log_error "Erstellung des Virtual Environments fehlgeschlagen."
        exit 1
    fi
else
    log_info "Virtual Environment existiert bereits."
fi
log_success "Virtual Environment ist eingerichtet."

# 3. Python-Pakete installieren
log_info "Aktiviere Virtual Environment und installiere Pakete aus requirements.txt..."
source $VENV_DIR/bin/activate
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    log_error "Installation der Python-Pakete fehlgeschlagen."
    deactivate
    exit 1
fi
deactivate
log_success "Alle Python-Pakete sind installiert."

# 4. systemd Service einrichten
SERVICE_NAME="hue_controller.service"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"
# Wichtig: Absolute Pfade verwenden, damit systemd sie findet.
WORKING_DIRECTORY=$(pwd)
VENV_PYTHON_PATH="$WORKING_DIRECTORY/$VENV_DIR/bin/python"
SCRIPT_PATH="$WORKING_DIRECTORY/main.py"

log_info "Erstelle systemd Service-Datei mit korrekten Pfaden..."

# Service-Datei-Inhalt mit heredoc erstellen
# Die Variablen werden hier direkt mit ihren absoluten Pfaden eingesetzt.
sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Philips Hue Advanced Routine Controller
After=network.target

[Service]
ExecStart=$VENV_PYTHON_PATH $SCRIPT_PATH
WorkingDirectory=$WORKING_DIRECTORY
StandardOutput=journal
StandardError=journal
Restart=always
User=$USER

[Install]
WantedBy=multi-user.target
EOF

log_info "systemd Service-Datei unter $SERVICE_FILE erstellt."

# 5. systemd neu laden und Service starten/aktivieren
log_info "Lade systemd neu und starte den Service neu..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

if sudo systemctl is-active --quiet $SERVICE_NAME; then
    log_success "Service '$SERVICE_NAME' wurde erfolgreich neu gestartet und aktiviert."
    log_info "Der Status kann mit 'systemctl status $SERVICE_NAME' überprüft werden."
else
    log_error "Service '$SERVICE_NAME' konnte nicht gestartet werden."
    log_info "Überprüfe die Logs mit 'journalctl -u $SERVICE_NAME' für Details."
    exit 1
fi

log_success "Einrichtung abgeschlossen! Die Web-UI sollte in Kürze erreichbar sein."