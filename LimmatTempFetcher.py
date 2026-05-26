import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import json

xml_url = "https://www.stadt-zuerich.ch/stzh/bathdatadownload"
output_path = "limmat_temp.json"
relevante_poiids = ["flb6939", "flb8803"]

try:
    response = requests.get(xml_url)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    ergebnisse = []

    for bad in root.findall(".//bath"):
        poiid = bad.findtext("poiid", "").strip()
        if poiid in relevante_poiids:
            name = bad.findtext("title", "").strip()
            temperature = bad.findtext("temperatureWater", "").strip()
            timestamp = bad.findtext("dateModified", "").strip()
            temperature_formatted = f"{temperature} °C" if temperature else "n/a"
            ergebnisse.append({
                "name": name,
                "temperature": temperature_formatted,
                "timestamp": timestamp
            })

    output = {
        "abgerufen_am": datetime.now().isoformat(),
        "daten": ergebnisse
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("✅ Temperaturdaten gespeichert.")

except Exception as e:
    print(f"❌ Fehler beim Verarbeiten: {e}")
    raise
