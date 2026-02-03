from typing import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
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


async def insert_people(people: Iterable[Person]) -> None:
    rows = [
        {
            col.name: getattr(p, col.name)
            for col in Person.__table__.c
            if col.name != "id"
        }
        for p in people
    ]
    if not rows:
        return
    async with ASYNC_SESSION.begin() as session:
        stmt = sqlite_insert(Person).on_conflict_do_nothing(
            index_elements=[Person.person_id]
        )
        await session.execute(stmt, rows)


async def select_people() -> Sequence[Person]:
    async with ASYNC_SESSION() as session:
        result = await session.scalars(select(Person))
        return result.all()


async def delete_all_data() -> None:
    async with ASYNC_SESSION.begin() as session:
        for table in reversed(DBBase.metadata.sorted_tables):
            await session.execute(table.delete())
