def title(properties: dict, key: str) -> str | None:
    prop = properties.get(key, {}).get("title", [])
    return prop[0]["plain_text"] if prop else None


def date(properties: dict, key: str) -> tuple[str | None, str | None]:
    prop = properties.get(key, {}).get("date")
    start = prop["start"] if prop else None
    end = prop["end"] if prop else None
    return (start, end)


def select(properties: dict, key: str) -> str | None:
    prop = properties.get(key, {}).get("select")
    return prop["name"] if prop else None


def rollup(properties: dict, key: str) -> str | None:
    array = properties.get(key, {}).get("rollup", {}).get("array", [])
    if not array:
        return None

    content = array[0].get(array[0].get("type"), [])
    return content[0]["plain_text"] if content else None


def number(properties: dict, key: str) -> float | None:
    value = properties.get(key, {}).get("number")
    return float(value) if value else None
