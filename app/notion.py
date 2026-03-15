import logging
from datetime import date, datetime, timedelta
from typing import Any, cast

from notion_client import APIResponseError, Client

from app import extract
from app.config import settings
from app.domain import Assignment, Subscription

log = logging.getLogger(__name__)

notion = Client(auth=settings.NOTION_API_KEY)


def retrieveDatasourceID(databaseID: str) -> str:
    try:
        raw = notion.databases.retrieve(database_id=databaseID)
        result = cast(dict[str, Any], raw)
        datasources = result.get("data_sources", [])
        if not datasources:
            raise ValueError(f"No data sources found for database: {databaseID}")
        return cast(str, datasources[0]["id"])
    except APIResponseError as e:
        raise ValueError(f"Notion API error while retrieving datasource: {e}") from e


def fetchData(calendarName: str) -> list[Assignment | Subscription]:

    if calendarName == settings.ASSIGNMENTS_CALENDAR_NAME:
        return fetchPages(
            retrieveDatasourceID(settings.ASSIGNMENTS_DATABASE_ID),
            {"property": "Date", "date": {"is_not_empty": True}},
            [{"property": "Date", "direction": "ascending"}],
        )
    return fetchPages(retrieveDatasourceID(settings.SUBSCRIPTIONS_DATABASE_ID))


def queryBuilder(
    datasourceID: str, cursor: str | None, filter: dict | None, sorts: list[dict] | None
):
    query: dict[str, Any] = {"data_source_id": datasourceID, "start_cursor": cursor}
    if filter:
        query["filter"] = filter
    if sorts:
        query["sorts"] = sorts
    return query


def fetchPages(
    datasourceID: str, filter: dict | None = None, sorts: list[dict] | None = None
) -> list[Assignment | Subscription]:
    result = list()
    hasMore = True
    cursor = None
    query = queryBuilder(
        datasourceID,
        cursor,
        filter,
        sorts,
    )

    while hasMore:
        try:
            query["start_cursor"] = cursor
            response = notion.data_sources.query(**query)
        except APIResponseError as e:
            log.error(f"Notion API error while querying the datasource: {e}")
            break

        response = cast(dict[str, Any], response)

        for page in response["results"]:
            try:
                data = dataFromPage(page)
                if data is None:
                    continue
                result.append(data)
            except AssertionError:
                log.warning(
                    f"Skipping page {page['id']} due to corrupted date property"
                )

        hasMore = response["has_more"]
        cursor = response["next_cursor"]

    return result


def dataFromPage(page: dict) -> Assignment | Subscription | None:
    databaseID = extract.databaseID(page)
    if databaseID is None:
        return None

    if databaseID == settings.ASSIGNMENTS_DATABASE_ID:
        return assignmentFromPage(page)
    return subscriptionFromPage(page)


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


def subscriptionFromPage(page: dict) -> Subscription | None:
    properties = page["properties"]

    date = extract.dateFormula(properties["Next Renewal"])
    if date is None:
        return None
    date = strToDate(date)

    return Subscription(
        id=page["id"],
        service=extract.title(properties["Service"]) or "Unknown service",
        billing=extract.select(properties["Billing"]) or "Unknown billing cycle",
        cost=extract.number(properties["Cost"]) or 0,
        billingDate=date,
        url=None,  # placeholder
    )


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
