CONTENT_KEYS: set[str] = {"number", "plain_text", "name", "start"}


def parseProperty(prop: dict) -> str | dict | None:
    while isinstance(prop, dict):
        for contentKey in CONTENT_KEYS:
            if contentKey in prop:
                if contentKey == "start":
                    return prop
                return prop[contentKey]
        prop = prop[prop["type"]]

        if prop is None:
            return None
        if isinstance(prop, list):
            prop = prop[0] if prop else None  # type: ignore

    return prop


def title(prop: dict) -> str | None:
    value = parseProperty(prop)
    return value if isinstance(value, str) else None


def date(prop: dict) -> tuple[str, str]:
    dates = parseProperty(prop)

    assert dates is not None and isinstance(dates, dict)

    start = dates["start"]
    end = dates["end"] if dates["end"] else start
    return (start, end)


def select(prop: dict) -> str | None:
    value = parseProperty(prop)
    return value if isinstance(value, str) else None


def rollup(prop: dict) -> str | None:
    value = parseProperty(prop)
    return value if isinstance(value, str) else None


def number(prop: dict) -> int | float | None:
    value = parseProperty(prop)
    return value if isinstance(value, (int, float)) else None
