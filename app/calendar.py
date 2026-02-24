from icalendar import Calendar, Event

from app.config import settings
from app.notion import Assignment


def createCalendar() -> Calendar:
    calendar = Calendar()
    calendar.add("prodid", "-//Notion Calendar Sub//notion-calendar-sub//")
    calendar.add("version", "2.0")
    calendar.add("calscale", "GREGORIAN")
    calendar.add("method", "PUBLISH")
    calendar.add("x-wr-calname", settings.CALENDAR_NAME)

    return calendar


def createEvent(assignment: Assignment) -> Event:
    event = Event()

    description = f"{assignment.course}\n{assignment.type}"
    if assignment.maxPoints is not None:
        description += f"\n{assignment.maxPoints}"

    event.add("uid", f"{assignment.id}@notion-calendar-sub")
    prefix = "" if assignment.abbreviation is None else f"{assignment.abbreviation}: "
    event.add("summary", prefix + assignment.name)
    event.add("dtstart", assignment.startDate)
    event.add("dtend", assignment.endDate)
    event.add("description", description)
    event.add("url", assignment.url)

    return event


def generateICS(assignments: list[Assignment]) -> bytes:
    calendar = createCalendar()

    for assignment in assignments:
        calendar.add_component(createEvent(assignment))

    return calendar.to_ical()
