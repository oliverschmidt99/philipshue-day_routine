# Dieses Skript ist komplett eigenständig und holt weitere Kern-Informationen von der Bridge.
import json
from python_hue_v2.hue import Hue

# --- Deine Zugangsdaten ---
BRIDGE_IP = "192.168.178.147"
APP_KEY = "Moerx3s4SFDkEdFQTPGlQfiaRjd6TxIDqbLhgB83"
# ---------------------------

# Die Ressourcen-Typen, die wir jetzt abfragen wollen
RESOURCES_TO_GET = [
    "lights",
    "scenes",
    "devices",
    "bridge"
]

def main():
    """
    Stellt eine Verbindung zur Hue Bridge her und fragt weitere wichtige
    Ressourcen ab.
    """
    print(f"Versuche, eine Verbindung zur Bridge unter {BRIDGE_IP} herzustellen...")

    try:
        hue = Hue(BRIDGE_IP, APP_KEY)
        hue.bridge.get_bridge()
        print("\nVerbindung erfolgreich hergestellt!")
        print("-" * 40)

    except Exception as e:
        print(f"\nVerbindung fehlgeschlagen: {e}")
        return

    # Frage jeden Ressourcen-Typ einzeln ab
    for resource_type in RESOURCES_TO_GET:
        print(f"\n--- Abfrage für: '{resource_type}' ---")
        try:
            # Wir verwenden die in der Bibliothek vorhandenen, direkten Methoden
            if resource_type == "lights":
                response_data = hue.bridge.get_lights()
            elif resource_type == "scenes":
                response_data = hue.bridge.get_scenes()
            elif resource_type == "devices":
                response_data = hue.bridge.get_devices()
            elif resource_type == "bridge":
                response_data = hue.bridge.get_bridge()
            
            if response_data:
                print(f"Erfolgreich {len(response_data)} Einträge für '{resource_type}' gefunden.")
                # Wir geben nur die ersten beiden Einträge aus, um die Konsole übersichtlich zu halten
                pretty_data = json.dumps(response_data[:2], indent=2)
                print(pretty_data)
            else:
                print(f"Keine Daten für '{resource_type}' gefunden.")

        except Exception as e:
            print(f"Ein unerwarteter Fehler bei '{resource_type}' ist aufgetreten: {e}")


if __name__ == "__main__":
    main()