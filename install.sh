#!/bin/bash

# ================================================================= #
#                      HELFER-FUNKTIONEN
# ================================================================= #
log_info() { echo -e "\n\e[34m[INFO]\e[0m $1"; }
log_success() { echo -e "\e[32m[ERFOLG]\e[0m $1"; }
log_error() { echo -e "\e[31m[FEHLER]\e[0m $1"; }
log_warning() { echo -e "\e[33m[AKTION ERFORDERLICH]\e[0m $1"; }

# ================================================================= #
#            SSH-SCHLÜSSEL EINRICHTEN
# ================================================================= #
setup_ssh_for_github() {
    log_info "Richte SSH-Schlüssel für passwortfreies 'git pull' von GitHub ein..."
    SSH_DIR="$HOME/.ssh"; KEY_PATH="$SSH_DIR/id_ed25519"
    mkdir -p "$SSH_DIR"; chmod 700 "$SSH_DIR"
    if [ ! -f "$KEY_PATH" ]; then
        log_info "Kein SSH-Schlüssel gefunden. Erstelle einen neuen..."
        ssh-keygen -t ed25519 -f "$KEY_PATH" -N "" -C "$(whoami)@$(hostname)-huecontroller"
        log_success "Neuer SSH-Schlüssel wurde unter $KEY_PATH erstellt."
    else
        log_success "Vorhandener SSH-Schlüssel unter $KEY_PATH wird verwendet."
    fi
    log_warning "Bitte füge den folgenden öffentlichen SSH-Schlüssel zu deinem GitHub-Account hinzu:"
    echo "--------------------------------------------------------------------------------"
    echo "1. Markiere und kopiere den gesamten Text zwischen den Linien:"
    echo ""; cat "$KEY_PATH.pub"; echo ""
    echo "2. Gehe zu GitHub in deinem Browser: https://github.com/settings/keys"
    echo "3. Klicke auf 'New SSH key', gib einen Titel ein (z.B. 'Hue Controller') und füge den Schlüssel ein."
    echo "--------------------------------------------------------------------------------"
    read -p "Drücke ENTER, sobald du den Schlüssel zu GitHub hinzugefügt hast..."
    
    log_info "Ändere die Git-URL auf das korrekte SSH-Format..."
    # ===== HIER IST DIE FINALE KORREKTUR DER URL =====
    if git remote set-url origin git@github.com:oliverschmidt99/philipshue-day_routine.git; then
        log_success "Git-Repository wurde erfolgreich auf SSH umgestellt."
    else
        log_error "Konnte das Git-Repository nicht auf SSH umstellen. Bitte manuell prüfen."
    fi
}

# ================================================================= #
#        PASSWORTFREIES SUDO EINRICHTEN
# ================================================================= #
setup_passwordless_sudo() {
    log_info "Richte passwortfreies sudo für System-Updates ein..."
    SUDOERS_FILE="/etc/sudoers.d/010-hue-controller-updates"
    USERNAME=$(whoami)
    
    if command -v pacman &> /dev/null; then
        COMMAND_PATH="/usr/bin/pacman -Syu --noconfirm"
    elif command -v apt-get &> /dev/null; then
        COMMAND_PATH="/usr/bin/apt-get update, /usr/bin/apt-get upgrade -y"
    else
        log_error "Kein unterstützter Paketmanager für passwortfreies sudo gefunden."
        return 1
    fi

    echo "$USERNAME ALL=(ALL) NOPASSWD: $COMMAND_PATH" | sudo tee "$SUDOERS_FILE" > /dev/null
    sudo chmod 440 "$SUDOERS_FILE"
    log_success "Passwortfreies sudo für Update-Befehle wurde eingerichtet."
}

# ================================================================= #
#                   HAUPTSKRIPT-ABLAUF
# ================================================================= #
log_info "Starte die Einrichtung des Philips Hue Controllers..."
log_info "Überprüfe und installiere Systemabhängigkeiten (benötigt eventuell sudo-Passwort)..."
if command -v pacman &> /dev/null; then
    PACKAGES="python python-pip gcc git"
    if ! sudo pacman -S --needed --noconfirm $PACKAGES; then log_error "Installation der Systemabhängigkeiten fehlgeschlagen." && exit 1; fi
elif command -v apt-get &> /dev/null; then
    PACKAGES="python3 python3-pip python3-venv gcc git"
    if ! sudo apt-get update || ! sudo apt-get install -y $PACKAGES; then log_error "Installation der Systemabhängigkeiten fehlgeschlagen." && exit 1; fi
else
    log_error "Kein unterstützter Paketmanager (pacman oder apt-get) gefunden." && exit 1
fi
log_success "Systemabhängigkeiten sind installiert."

VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    log_info "Erstelle Python Virtual Environment in '$VENV_DIR'..."
    python3 -m venv $VENV_DIR
    if [ $? -ne 0 ]; then log_error "Erstellung des Virtual Environments fehlgeschlagen." && exit 1; fi
else
    log_info "Virtual Environment existiert bereits."
fi
log_success "Virtual Environment ist eingerichtet."

log_info "Aktiviere Virtual Environment und installiere Pakete aus requirements.txt..."
source $VENV_DIR/bin/activate
pip install -r requirements.txt
if [ $? -ne 0 ]; then log_error "Installation der Python-Pakete fehlgeschlagen." && deactivate && exit 1; fi
deactivate
log_success "Alle Python-Pakete sind installiert."

setup_ssh_for_github
setup_passwordless_sudo

SERVICE_NAME="hue_controller.service"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"
WORKING_DIRECTORY=$(pwd)
VENV_PYTHON_PATH="$WORKING_DIRECTORY/$VENV_DIR/bin/python"
SCRIPT_PATH="$WORKING_DIRECTORY/main.py"
log_info "Erstelle systemd Service-Datei..."
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
User=$(whoami)

[Install]
WantedBy=multi-user.target
EOF
log_success "systemd Service-Datei unter $SERVICE_FILE erstellt."

log_info "Lade systemd neu und starte den Service..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    log_success "Service '$SERVICE_NAME' wurde erfolgreich gestartet und aktiviert."
    log_info "Der Status kann mit 'systemctl status $SERVICE_NAME' überprüft werden."
else
    log_error "Service '$SERVICE_NAME' konnte nicht gestartet werden."
    log_info "Überprüfe die Logs mit 'journalctl -u $SERVICE_NAME' für Details." && exit 1
fi
log_success "Einrichtung abgeschlossen! Die Web-UI sollte in Kürze erreichbar sein."