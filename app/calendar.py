from icalendar import Calendar, Event

from app.domain import Assignment, Subscription


def createCalendar(name: str) -> Calendar:
    calendar = Calendar()
    calendar.add("prodid", "-//Notion Calendar Sub//notion-calendar-sub//")
    calendar.add("version", "2.0")
    calendar.add("calscale", "GREGORIAN")
    calendar.add("method", "PUBLISH")
    calendar.add("x-wr-calname", name)

    return calendar


def createEvent(data: Assignment | Subscription) -> Event:
    if isinstance(data, Assignment):
        return createAssignmentEvent(data)
    return createSubscriptionEvent(data)


def createAssignmentEvent(assignment: Assignment) -> Event:
    event = Event()

    description = f"{assignment.course}\n{assignment.type}"
    if assignment.maxPoints is not None:
        description += f"\n{assignment.maxPoints}"

    event.add("uid", f"{assignment.id}@notion-assignments-sub")
    prefix = "" if assignment.abbreviation is None else f"{assignment.abbreviation}: "
    event.add("summary", prefix + assignment.name)
    event.add("dtstart", assignment.startDate)
    event.add("dtend", assignment.endDate)
    event.add("description", description)
    event.add("url", assignment.url)

    return event


def createSubscriptionEvent(subscription: Subscription) -> Event:
    event = Event()

    description = f"{subscription.billing}\n{subscription.cost}"

    event.add("uid", f"{subscription.id}@notion-subscriptions-sub")
    event.add("summary", subscription.service)
    event.add("dtstart", subscription.billingDate)
    event.add("description", description)
    if subscription.url is not None:
        event.add("url", subscription.url)

    return event


def generateICS(calendarName: str, data: list[Assignment | Subscription]) -> bytes:
    calendar = createCalendar(calendarName)

    for dataComponent in data:
        calendar.add_component(createEvent(dataComponent))

    return calendar.to_ical()
