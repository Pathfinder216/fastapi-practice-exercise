from datetime import date
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    EmailStr,
    NonNegativeFloat,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from utils.validation import empty_string_to_none, ensure_date, is_alpha, is_not_future


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


class PersonBase(BaseModel):
    person_id: str
    first_name: Annotated[str, AfterValidator(is_alpha)]
    last_name: Annotated[str, AfterValidator(is_alpha)]
    email: EmailStr
    date_of_birth: Annotated[
        date, BeforeValidator(ensure_date), AfterValidator(is_not_future)
    ]
    income: Annotated[NonNegativeFloat | None, BeforeValidator(empty_string_to_none)]


class PersonCreate(PersonBase):
    pass


class PersonResponse(PersonBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
