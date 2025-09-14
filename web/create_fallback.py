import subprocess
from datetime import datetime

def run(cmd):
    """Hilfsfunktion: führe einen Befehl aus und gib die Ausgabe zurück."""
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())
    return result.returncode

def create_fallback():
    # Aktuelles Datum und Uhrzeit für den Branchnamen
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d-%H-%M-%S")

    # Frage nach optionalem Zusatz
    suffix = input("Optionaler Zusatz für den Branchnamen (Enter = kein Zusatz): ").strip()
    if suffix:
        branch_name = f"fallback-{timestamp}-{suffix}"
    else:
        branch_name = f"fallback-{timestamp}"

    # Sicherstellen, dass wir auf main sind und alles aktuell ist
    run("git checkout main")
    run("git pull origin main")

    # Neuen Fallback-Branch erstellen
    run(f"git checkout -b {branch_name}")

    # Nach GitHub pushen
    run(f"git push origin {branch_name}")

    # Zurück auf main wechseln
    run("git checkout main")

    print(f"\n✅ Fallback-Branch '{branch_name}' wurde erstellt und nach GitHub gepusht.")

if __name__ == "__main__":
    create_fallback()
