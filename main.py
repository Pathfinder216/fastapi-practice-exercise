import csv
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Sequence

from fastapi import FastAPI
from pydantic import ValidationError

from database import create_db, insert_people, select_people
from models import Person, PersonCreate, PersonResponse
from schemas import UploadResponse, UploadErrorResponse, UploadSummaryResponse


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, None]:
    await create_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root() -> dict[str, Any]:
    return {"status": 200, "description": "hello world"}


@app.get("/people", response_model=Sequence[PersonResponse])
async def get_people() -> Sequence[Person]:
    return await select_people()


@app.post("/upload")
async def upload_csv(filename: str) -> UploadResponse:
    with open(filename) as f:
        people_to_add: dict[str, Person] = {}
        errors: list[UploadErrorResponse] = []
        file_duplicates = 0

        for row_num, row in enumerate(csv.DictReader(f), start=1):
            try:
                person = PersonCreate.model_validate(row)
            except ValidationError as err:
                errors.append(
                    UploadErrorResponse(
                        row_number=row_num,
                        errors=[f"{e['loc'][0]}: {e['msg']}" for e in err.errors()],
                    )
                )
            else:
                if person.person_id in people_to_add:
                    file_duplicates += 1
                else:
                    people_to_add[person.person_id] = Person(**person.model_dump())

        db_duplicates = await insert_people(
            people_to_add.values(), person_ids=set(people_to_add)
        )

        summary = UploadSummaryResponse(
            total_rows=len(people_to_add) + len(errors) + file_duplicates,
            valid_rows=len(people_to_add) - db_duplicates,
            invalid_rows=len(errors),
            duplicates_skipped=file_duplicates + db_duplicates,
        )

    return UploadResponse(summary=summary, errors=errors)
