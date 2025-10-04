#!/bin/bash
echo "Repariere fehlerhafte Verweise in TypeScript-Dateien..."

# Finde alle .ts Dateien im src-Ordner
# und lösche die Zeilen, die auf 'lib/jQuery.d.ts' verweisen.
find src -type f -name "*.ts" -exec sed -i '/<reference path="..\/..\/lib\/jQuery.d.ts" \/>/d' {} \;
find src -type f -name "*.ts" -exec sed -i '/<reference path="lib\/jQuery.d.ts" \/>/d' {} \;


echo "Reparatur abgeschlossen."