from typing import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from models import DBBase, Person

DATABASE_PATH = "sqlite+aiosqlite:///pop.db"

ENGINE = create_async_engine(DATABASE_PATH, echo=True)
ASYNC_SESSION = async_sessionmaker(ENGINE, expire_on_commit=False)


async def create_db() -> None:
    async with ENGINE.begin() as conn:
        await conn.run_sync(DBBase.metadata.create_all)


async def insert_people(
    people: Iterable[Person], *, person_ids: set[str] | None = None
) -> int:
    """Returns number of duplicates skipped."""
    if person_ids is None:
        person_ids = {person.person_id for person in people}

    async with ASYNC_SESSION() as session:
        async with session.begin():
            duplicate_id_statement = select(Person.person_id).where(
                Person.person_id.in_(person_ids)
            )
            result = await session.scalars(duplicate_id_statement)
            duplicate_person_ids = set(result.all())
            people_to_add = [
                person
                for person in people
                if person.person_id not in duplicate_person_ids
            ]

            session.add_all(people_to_add)

    return len(duplicate_person_ids)


async def select_people() -> Sequence[Person]:
    async with ASYNC_SESSION() as session:
        result = await session.scalars(select(Person))
        return result.all()
