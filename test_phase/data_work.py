import json
import os





def open_json(pfad):
    with open(pfad, "r") as datei:
        daten = json.load(datei)
    return daten


datei_zonen = "zonen.json"
datei_settings = "settings.json"
datei_log = "outside.log"

aktueller_pfad = os.path.dirname(__file__)
pfad_json_zonen = os.path.join(aktueller_pfad, datei_zonen)
pfad_json_settings = os.path.join(aktueller_pfad, datei_settings)
pfad_log = os.path.join(aktueller_pfad, datei_log)


