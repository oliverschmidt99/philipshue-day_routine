#!/bin/bash
#
# Installations- und Einrichtungsskript für den Philips Hue Advanced Routine Controller
#

# Beendet das Skript sofort, wenn ein Befehl fehlschlägt
set -e

# --- Globale Variablen ---
SERVICE_NAME="hue_controller.service"
VENV_DIR=".venv"
PROJECT_DIR=$(pwd)
PYTHON_EXEC="$PROJECT_DIR/$VENV_DIR/bin/python"
MAIN_SCRIPT="$PROJECT_DIR/main.py"
CURRENT_USER=$(whoami)

# --- Funktionen ---

# Funktion zur Anzeige von Info-Meldungen
info() {
    echo -e "\e[34m[INFO]\e[0m $1"
}

# Funktion zur Anzeige von Erfolgs-Meldungen
success() {
    echo -e "\e[32m[ERFOLG]\e[0m $1"
}

# Funktion zur Anzeige von Warnungen
warn() {
    echo -e "\e[33m[WARNUNG]\e[0m $1"
}

# Funktion zur Anzeige von Fehlern und zum Beenden
fail() {
    echo -e "\e[31m[FEHLER]\e[0m $1" >&2
    exit 1
}

# --- Skript-Ausführung ---

info "Starte die Einrichtung des Philips Hue Controllers..."

# 1. Systemabhängigkeiten für Arch Linux installieren
info "Überprüfe und installiere Systemabhängigkeiten (benötigt eventuell sudo-Passwort)..."
if ! command -v pacman &> /dev/null; then
    fail "Dieser Installer ist für Arch-basierte Linux-Distributionen (pacman) ausgelegt."
fi

sudo pacman -Syu --noconfirm --needed python python-pip python-venv gcc || fail "Installation der Systemabhängigkeiten fehlgeschlagen."
success "Systemabhängigkeiten sind auf dem neuesten Stand."

# 2. Virtuelle Umgebung (venv) einrichten
if [ -d "$VENV_DIR" ]; then
    warn "Das Verzeichnis '$VENV_DIR' existiert bereits. Überspringe die Erstellung."
else
    info "Erstelle eine neue virtuelle Python-Umgebung in '$VENV_DIR'..."
    python -m venv $VENV_DIR || fail "Erstellung der venv fehlgeschlagen."
    success "Virtuelle Umgebung wurde erstellt."
fi

# 3. Python-Abhängigkeiten aus requirements.txt installieren
info "Installiere Python-Abhängigkeiten in der venv..."
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt || fail "Installation der Python-Abhängigkeiten fehlgeschlagen."
deactivate
success "Alle Python-Abhängigkeiten wurden erfolgreich installiert."

# 4. systemd-Service für den Autostart einrichten
info "Richte den systemd-Service für den Autostart ein..."
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"

# Erstelle den Inhalt für die .service-Datei
read -r -d '' SERVICE_CONTENT <<EOF
[Unit]
Description=Philips Hue Advanced Routine Controller
After=network.target

[Service]
User=$CURRENT_USER
Group=$(id -gn "$CURRENT_USER")
WorkingDirectory=$PROJECT_DIR
ExecStart=$PYTHON_EXEC $MAIN_SCRIPT
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Schreibe die Datei mit sudo-Rechten
echo "$SERVICE_CONTENT" | sudo tee "$SERVICE_FILE" > /dev/null || fail "Konnte die systemd-Service-Datei nicht erstellen."
success "systemd-Service-Datei wurde unter '$SERVICE_FILE' erstellt."

# systemd neuladen und den Service aktivieren/starten
info "Aktiviere und starte den systemd-Service..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"
success "Der Service '$SERVICE_NAME' wurde aktiviert und gestartet."

# --- Abschluss ---
echo
success "Die Installation und Einrichtung ist abgeschlossen!"
info "Die Anwendung läuft jetzt als Hintergrund-Service."
info "Du kannst den Status mit 'systemctl status $SERVICE_NAME' überprüfen."
info "Die Weboberfläche ist unter http://<deine-ip>:5000 erreichbar."