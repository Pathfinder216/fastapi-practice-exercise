from datetime import date, datetime
from typing import Annotated, Any

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    EmailStr,
    NonNegativeFloat,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class DBBase(DeclarativeBase):
    pass


class Person(DBBase):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[str] = mapped_column(unique=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str]
    date_of_birth: Mapped[date]
    income: Mapped[float | None]


def is_alpha(value: str) -> str:
    if not value.isalpha():
        raise ValueError(f"'{value}' is not alphabetic")
    return value


def ensure_date(value: Any) -> date:
    if isinstance(value, date):
        return value

    if not isinstance(value, str):
        raise TypeError(f"'{value}' must be a date or a string")

    return datetime.strptime(value, "%Y-%m-%d").date()


def is_not_future(value: date) -> date:
    if value > date.today():
        raise ValueError(f"'{value} is a future date")
    return value


class PersonBase(BaseModel):
    person_id: str
    first_name: Annotated[str, AfterValidator(is_alpha)]
    last_name: Annotated[str, AfterValidator(is_alpha)]
    email: EmailStr
    date_of_birth: Annotated[
        date, BeforeValidator(ensure_date), AfterValidator(is_not_future)
    ]
    income: Annotated[
        NonNegativeFloat | None, BeforeValidator(lambda v: None if v == "" else v)
    ]


class PersonCreate(PersonBase):
    pass


class PersonResponse(PersonBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
