# Limmat Temperature Fetcher

Daily fetch of water temperatures at the Letten bathing spots in Zurich, via the [Stadt Zürich open data API](https://www.stadt-zuerich.ch/stzh/bathdatadownload).

## What it does

A GitHub Actions workflow runs every day at 10:00 CEST and commits the current water temperatures as `limmat_temp.json` to this repository. The JSON is then read by a Power Automate flow that displays the data in the gebana intranet.

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

## Manual trigger

The workflow can also be triggered manually via GitHub Actions → "Fetch Limmat Temperature" → "Run workflow".
