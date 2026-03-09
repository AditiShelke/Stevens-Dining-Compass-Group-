# Stevens Dining Heatmap API

Flask API that accepts a multi-sheet Excel workbook and returns a ZIP of heatmap PNGs — one per dining venue sheet.

## Deploy to Render.com (free, 5 minutes)

1. Push this folder to a GitHub repo (e.g. `dining-heatmap-api`)
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Render reads `render.yaml` automatically — just click **Deploy**
5. Wait ~3 minutes for build
6. Your API is live at: `https://stevens-dining-heatmap-api.onrender.com`

## API Endpoints

### GET /health
Check the service is running.
```
curl https://your-app.onrender.com/health
# → {"status": "ok", "service": "Stevens Dining Heatmap API"}
```

### POST /generate
Send an Excel file, receive a ZIP of PNG heatmaps.
```
curl -X POST https://your-app.onrender.com/generate \
  -F "file=@Daily_Transactions_January_2026.xlsx" \
  --output heatmaps.zip
```

Returns: `dining_heatmaps.zip` containing one PNG per sheet.

## Connect to n8n

In your n8n HTTP Request node:
- Method: `POST`
- URL: `https://your-app.onrender.com/generate`
- Body Content Type: `Form Data`
- Add field: Name = `file`, Value = `{{ $binary.attachment_0 }}`, Type = `File`
- Response Format: `File`

## Supported Venues
Pierce Dining Hall, Zaro's, CREATE, Cannon, Yella's, TU Taco, Pom & Honey, Piccola Italia, Late Night

Any unrecognized sheet name uses default time range (7AM–9PM).
