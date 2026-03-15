from fastapi import FastAPI, HTTPException
from fastapi.responses import Response

from app.calendar import generateICS
from app.config import settings
from app.notion import fetchData

app = FastAPI(
    title="Notion Calendar Subscription",
    description="Generates an ICS feed from a Notion database",
    version="1.1.0",
)


@app.get("/")
def root():
    return {"status": "ok", "message": "App is running"}


@app.get("/{token}/{calendarName}.ics")
def getCalendar(token: str, calendarName: str):
    if token != settings.TOKEN:
        raise HTTPException(status_code=404)

    if calendarName not in (
        settings.ASSIGNMENTS_CALENDAR_NAME,
        settings.SUBSCRIPTIONS_CALENDAR_NAME,
    ):
        raise HTTPException(status_code=404)

    data = fetchData(calendarName)

    ics = generateICS(calendarName, data)
    return Response(content=ics, media_type="text/calendar")
