# Bring Back Ivy Command Center

A Flask dashboard for managing media outreach, official correspondence, follow-ups and responses.

## Render settings

- Runtime: Python
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Health check: `/health`

## Add an email through the API

POST JSON to `/api/emails`:

```json
{
  "subject": "Email subject",
  "recipient": "WAVY 10 Investigates",
  "recipient_email": "news@example.com",
  "category": "Media Outreach",
  "status": "Draft",
  "body": "Complete email body",
  "notes": "",
  "follow_up_date": "2026-07-20"
}
```

When `IVY_API_KEY` is set on Render, include the header:

`X-API-Key: your-secret-key`
