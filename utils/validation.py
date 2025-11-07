from datetime import date, datetime
from typing import Any


def empty_string_to_none(value: Any) -> Any:
    return None if value == "" else value


def ensure_date(value: Any) -> date:
    if isinstance(value, date):
        return value

    if not isinstance(value, str):
        raise TypeError(f"'{value}' must be a date or a string")

    return datetime.strptime(value, "%Y-%m-%d").date()


def is_alpha(value: str) -> str:
    if not value.isalpha():
        raise ValueError(f"'{value}' is not alphabetic")
    return value


def is_not_future(value: date) -> date:
    if value > date.today():
        raise ValueError(f"'{value} is a future date")
    return value
