# Limmat Temperature Fetcher

Fetches water temperatures at the Letten bathing spots in Zurich 3x daily and uploads the result to OneDrive, where a Power Automate flow reads it and displays it in the gebana intranet.

## Architecture

```
cron-job.org (07:00 / 11:00 / 15:00 CEST)
  → POST to GitHub API (workflow_dispatch)
    → GitHub Actions: fetch Stadt Zürich XML API → upload JSON to OneDrive
      → Power Automate (07:30 / 11:30 / 15:30 CEST): read JSON → update SharePoint list
        → gebana Intranet
```

## Output format

```json
{
  "abgerufen_am": "2026-05-26T10:00:00.000000",
  "daten": [
    {
      "name": "Flussbad Oberer Letten",
      "temperature": "18.5 °C",
      "timestamp": "2026-05-26T09:30:00"
    },
    {
      "name": "Flussbad Unterer Letten",
      "temperature": "18.3 °C",
      "timestamp": "2026-05-26T09:30:00"
    }
  ]
}
```

**Note:** The Letten bathing spots only appear in the API feed during the outdoor swimming season (~May–September). Outside the season, `daten` will be an empty array — this is expected.

## Monitored locations

| POI ID | Name |
|--------|------|
| `flb6939` | Flussbad Oberer Letten |
| `flb8803` | Flussbad Unterer Letten |

Source: [Stadt Zürich open data API](https://www.stadt-zuerich.ch/stzh/bathdatadownload)

## OneDrive path

`Coding/limmat_temp.json`

## Trigger: cron-job.org

The workflow trigger is `workflow_dispatch` only — no GitHub-internal schedule (GitHub drops cron schedules for repos with low activity).

cron-job.org sends a `POST` to the GitHub API at 07:00, 11:00, 15:00 CEST (= 05:00, 09:00, 13:00 UTC):

- **URL:** `https://api.github.com/repos/DavidKlier/limmat-temp/actions/workflows/fetch-limmat.yml/dispatches`
- **Method:** POST
- **Headers:** `Authorization: Bearer <PAT>` · `Accept: application/vnd.github+json` · `X-GitHub-Api-Version: 2022-11-28` · `Content-Type: application/json`
- **Body:** `{"ref": "main"}`
- **Success:** HTTP `204 No Content`

**PAT:** Fine-grained token scoped to this repo only, permission `Actions: read and write`. Name: `cron-job.org limmat-fetcher`. Account: `d.klier@gebana.com`.

## GitHub Secrets

| Secret | Description |
|--------|-------------|
| `AZURE_TENANT_ID` | gebana Azure AD Tenant ID |
| `AZURE_CLIENT_ID` | App-ID of the `gebLimmatTemp` Azure AD app |
| `AZURE_REFRESH_TOKEN` | Delegated refresh token (generated via `setup_token.py`) |
| `ONEDRIVE_USER` | `d.klier@gebana.com` |

## Azure AD app (`gebLimmatTemp`)

- App-ID: `8ac161df-e7d9-41e5-a580-429dc5748e8d`
- Permission: `Files.ReadWrite` (Delegated)
- Allow public client flows: enabled
- Conditional Access exception: granted

The workflow uses a delegated refresh token (not a client secret) to authenticate as the user. The token refreshes itself on every run — as long as the workflow runs regularly, it stays valid indefinitely.

## Renewing the refresh token

If the token ever expires (e.g. after a long pause):

```bash
python3 ~/Claude/limmat-temp/setup_token.py
```

Open the printed URL, enter the device code, log in → copy the new refresh token into the GitHub Secret `AZURE_REFRESH_TOKEN`.

## Power Automate

Scheduled recurrence: every day at 07:30, 11:30, 15:30 CEST (= 05:30, 09:30, 13:30 UTC).

Uses a OneDrive file read (not a file-change trigger — that trigger has a known bug with `Invalid fileId` errors in Power Automate).

## Manual trigger

GitHub → Actions → "Fetch Limmat Temperature" → Run workflow
