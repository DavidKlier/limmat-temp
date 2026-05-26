"""
Einmalig ausführen um den Refresh Token zu generieren.
Den ausgegebenen Token als GitHub Secret 'AZURE_REFRESH_TOKEN' speichern.
"""
import requests
import time

tenant_id = input("Tenant ID: ").strip()
client_id = input("Client ID: ").strip()

response = requests.post(
    f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/devicecode",
    data={
        "client_id": client_id,
        "scope": "https://graph.microsoft.com/Files.ReadWrite offline_access",
    },
)
response.raise_for_status()
data = response.json()

print(f"\n1. Diese URL öffnen: {data['verification_uri']}")
print(f"2. Diesen Code eingeben: {data['user_code']}\n")

while True:
    time.sleep(data["interval"])
    token_response = requests.post(
        f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "client_id": client_id,
            "device_code": data["device_code"],
        },
    )
    token_data = token_response.json()

    if "refresh_token" in token_data:
        print("✅ Anmeldung erfolgreich!\n")
        print("Refresh Token (als GitHub Secret 'AZURE_REFRESH_TOKEN' speichern):")
        print("-" * 60)
        print(token_data["refresh_token"])
        print("-" * 60)
        break
    elif token_data.get("error") == "authorization_pending":
        print("Warte auf Anmeldung im Browser...")
    else:
        print(f"❌ Fehler: {token_data.get('error_description', token_data)}")
        break
