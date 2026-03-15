from datetime import date, datetime

from pydantic.dataclasses import dataclass


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


@dataclass(kw_only=True, slots=True)
class Subscription:
    id: str
    service: str
    billing: str
    cost: float
    billingDate: date
    url: str | None
