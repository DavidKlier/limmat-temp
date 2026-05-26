import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import os

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
    print(f"❌ Fehler beim Abrufen: {e}")
    raise

# OneDrive-Upload via Microsoft Graph API
tenant_id = os.environ.get("AZURE_TENANT_ID")
client_id = os.environ.get("AZURE_CLIENT_ID")
client_secret = os.environ.get("AZURE_CLIENT_SECRET")
onedrive_user = os.environ.get("ONEDRIVE_USER")  # d.klier@gebana.com

if all([tenant_id, client_id, client_secret, onedrive_user]):
    try:
        token_response = requests.post(
            f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": "https://graph.microsoft.com/.default",
            },
        )
        token_response.raise_for_status()
        access_token = token_response.json()["access_token"]

        with open(output_path, "rb") as f:
            upload_response = requests.put(
                f"https://graph.microsoft.com/v1.0/users/{onedrive_user}/drive/root:/Coding/limmat_temp.json:/content",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                data=f,
            )
        upload_response.raise_for_status()
        print("✅ OneDrive-Upload erfolgreich.")

    except Exception as e:
        print(f"❌ Fehler beim OneDrive-Upload: {e}")
        raise
else:
    print("ℹ️  Keine Azure-Credentials gefunden, OneDrive-Upload übersprungen.")
