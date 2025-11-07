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


async def get_existing_ids(ids: Iterable[str]) -> Sequence[str]:
    async with ASYNC_SESSION() as session:
        duplicate_id_statement = select(Person.person_id).where(
            Person.person_id.in_(ids)
        )
        result = await session.scalars(duplicate_id_statement)
        return result.all()


async def insert_people(people: Iterable[Person]):
    """Returns number of duplicates skipped."""
    async with ASYNC_SESSION() as session:
        async with session.begin():
            # TODO: on conflict do nothing
            session.add_all(people)


async def select_people() -> Sequence[Person]:
    async with ASYNC_SESSION() as session:
        result = await session.scalars(select(Person))
        return result.all()
