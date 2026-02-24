from fastapi import FastAPI, HTTPException
from fastapi.responses import Response

from app.calendar import generateICS
from app.config import settings
from app.notion import fetchAssignments

app = FastAPI(
    title="Notion Calendar Subscription",
    description="Generates an ICS feed from a Notion database",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"status": "ok", "message": "App is running"}


@app.get("/calendar/{token}.ics")
def getCalendar(token: str):
    if token != settings.TOKEN:
        raise HTTPException(status_code=404)

    assignments = fetchAssignments()

    ics = generateICS(assignments)
    return Response(content=ics, media_type="text/calendar")
