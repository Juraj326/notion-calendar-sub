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
    maxPoints: int | float | None
    url: str


def strToDate(value: str) -> date | datetime:
    if "T" in value:
        return datetime.fromisoformat(value)
    return date.fromisoformat(value)


def getDatesFromProperty(prop: dict) -> tuple[date | datetime, date | datetime]:
    start, end = extract.date(prop)

    startDate, endDate = strToDate(start), strToDate(end)
    if isinstance(endDate, date) and not isinstance(endDate, datetime):
        endDate = endDate + timedelta(days=1)
    return startDate, endDate


def assignmentFromPage(page: dict) -> Assignment:
    properties = page["properties"]

    startDate, endDate = getDatesFromProperty(properties["Date"])

    return Assignment(
        id=page["id"],
        startDate=startDate,
        endDate=endDate,
        name=extract.title(properties["Name"]) or "Untitled",
        abbreviation=extract.rollup(properties["Abbreviation"]),
        course=extract.rollup(properties["Course"]) or "Unknown course",
        type=extract.select(properties["Type"]) or "Unknown type",
        maxPoints=extract.number(properties["Max"]),
        url=page["url"],
    )


def fetchAssignments() -> list[Assignment]:
    result = list()
    hasMore = True
    cursor = None

    while hasMore:
        try:
            response = notion.data_sources.query(
                data_source_id=settings.NOTION_DATABASE_ID,
                filter={"property": "Date", "date": {"is_not_empty": True}},
                sorts=[{"property": "Date", "direction": "ascending"}],
                start_cursor=cursor,
            )
        except APIResponseError as e:
            log.error(f"Notion API error: {e}")
            break

        response = cast(dict[str, Any], response)

        for page in response["results"]:
            try:
                result.append(assignmentFromPage(page))
            except AssertionError:
                log.warning(
                    f"Skipping page {page['id']} due to corrupted date property"
                )

        hasMore = response["has_more"]
        cursor = response["next_cursor"]

    return result
