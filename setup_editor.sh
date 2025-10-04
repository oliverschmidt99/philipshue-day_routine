#!/bin/bash
echo "Starte Aufräumarbeiten..."

# 1. Entferne alle __pycache__ Verzeichnisse
echo "Entferne __pycache__ Ordner..."
find . -type d -name "__pycache__" -exec rm -r {} +

# 2. Entferne .bak (Backup) Dateien
echo "Entferne .bak Dateien..."
find . -type f -name "*.js.bak" -delete

# 3. Entferne überflüssige Dokumentationsdateien aus blueprint3d
echo "Entferne Doku-Dateien aus blueprint3d..."
rm -f blueprint3d/README.md
rm -f blueprint3d/LICENSE.txt
rm -f blueprint3d/CODING_STYLE.md

# Optional: Entferne das verschachtelte .git Verzeichnis von blueprint3d
# Dies ist sinnvoll, wenn du blueprint3d nicht als Submodul, sondern als
# festen Teil deines Projekts versionieren willst.
if [ -d "blueprint3d/.git" ]; then
    echo "Entferne verschachteltes .git Verzeichnis in blueprint3d..."
    rm -rf blueprint3d/.git
fi

echo "Aufräumen abgeschlossen! ✨"