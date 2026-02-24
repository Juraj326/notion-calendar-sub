import logging
from datetime import date, datetime, timedelta
from typing import Any, cast

from notion_client import APIResponseError, Client
from pydantic.dataclasses import dataclass

from app import extract
from app.config import settings

log = logging.getLogger(__name__)

notion = Client(auth=settings.NOTION_API_KEY)


@dataclass(kw_only=True, slots=True)
class Assignment:
    id: str
    startDate: date | datetime
    endDate: date | datetime
    name: str
    abbreviation: str | None
    course: str
    type: str
    maxPoints: float | None
    url: str


def strToDate(value: str) -> date | datetime:
    if "T" in value:
        return datetime.fromisoformat(value)
    return date.fromisoformat(value)


def parseDateRange(properties: dict) -> None | tuple[date | datetime, date | datetime]:
    start, end = extract.date(properties, "Date")
    if start is None:
        return None

    if end is None:
        end = start

    startDate, endDate = strToDate(start), strToDate(end)
    if isinstance(endDate, date) and not isinstance(endDate, datetime):
        endDate = endDate + timedelta(days=1)

    return startDate, endDate


def assignmentFromPage(page: dict) -> Assignment | None:
    properties = page["properties"]

    dates = parseDateRange(properties)
    if dates is None:
        return None
    startDate, endDate = dates

    return Assignment(
        id=page["id"],
        startDate=startDate,
        endDate=endDate,
        name=extract.title(properties, "Name") or "Untitled",
        abbreviation=extract.rollup(properties, "Abbreviation"),
        course=extract.rollup(properties, "Course") or "Unknown course",
        type=extract.select(properties, "Type") or "Unknown type",
        maxPoints=extract.number(properties, "Max"),
        url=page["url"],
    )


def fetchAssignments() -> list[Assignment]:
    result: list[Assignment] = list()
    hasMore: bool = True
    nextCursor = None

    while hasMore:
        try:
            response = notion.data_sources.query(
                data_source_id=settings.NOTION_DATABASE_ID,
                sorts=[{"property": "Date", "direction": "ascending"}],
                start_cursor=nextCursor,
            )
        except APIResponseError as e:
            log.error(f"Notion API error: {e}")
            return list()

        response = cast(dict[str, Any], response)

        for page in response["results"]:
            assignment = assignmentFromPage(page)
            if assignment is None:
                continue

            result.append(assignment)

        hasMore = response.get("has_more", False)
        nextCursor = response.get("next_cursor")

    return result
