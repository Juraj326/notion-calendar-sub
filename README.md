# Notion Calendar Subscription

A small python application that generates a subscription calendar for a specific Notion database.

## Setup

### 1. Create a Notion Integration

1. Go to [notion.so/my-integrations](https://notion.so/my-integrations)
2. Create a new integration
3. Copy the API key

### 2. Share Your Database

1. Open your Notion database
2. Click "..." → "Connections" → Add your integration

#### Get Your Database ID

The database ID is in the URL when viewing your database:

```
https://notion.so/your-workspace/DATABASE_ID?v=...
```

### 3. Configure Environment

Copy `.env.example` to `.env` and fill in your values

| Variable | Description |
|----------|-------------|
| `NOTION_API_KEY` | Your Notion integration token |
| `ASSIGNMENTS_DATABASE_ID` | The ID of your Notion assignments database |
| `SUBSCRIPTIONS_DATABASE_ID` | The ID of your Notion subscriptions database |
| `ASSIGNMENTS_CALENDAR_NAME` | Name shown in calendar apps (default: "Assignments") |
| `SUBSCRIPTIONS_CALENDAR_NAME` | Name shown in calendar apps (default: "Subscriptions") |
| `TOKEN` | Secret token for the calendar URL |

### 4. Start the app

```bash
uv sync
uv run uvicorn app.main:app --reload
```

Add `http://localhost:8000/{YOUR_TOKEN}/{CALENDAR_NAME}.ics` (e.g. assignments calendar) in your calendar app

## Project Structure

```
├── app/
│   ├── __init__.py   # Package marker
│   ├── main.py       # FastAPI routes
│   ├── notion.py     # Notion API integration
│   ├── domain.py     # Data models
│   ├── extract.py    # Notion property extraction helpers
│   ├── calendar.py   # ICS generation
│   └── config.py     # Environment configuration
├── Dockerfile
├── fly.toml
└── pyproject.toml
```