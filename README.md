# Stevens Dining Heatmap API

Flask API that accepts a multi-sheet Excel workbook and returns a ZIP of heatmap PNGs — one per dining venue sheet.

## Deployed to Render.com 

1. Pushed the folder to a GitHub repo 
2. [render.com](https://render.com) → New → Web Service
3. Connected my GitHub repo
4. Render reads `render.yaml` automatically — just click **Deploy**

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
