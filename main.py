import csv
from contextlib import asynccontextmanager
from io import StringIO
from typing import Any, AsyncGenerator, Sequence

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import ValidationError

from database import (
    create_db,
    delete_all_data,
    get_existing_ids,
    insert_people,
    select_people,
)
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
async def upload_csv(file: UploadFile = File(...)) -> UploadResponse:
    if not (file.filename and file.filename.endswith(".csv")):
        raise HTTPException(status_code=415, detail="Only CSV files are supported")

    # TODO: don't block main thread when reading file
    contents = StringIO(file.file.read().decode())

    people_from_file: dict[str, Person] = {}
    errors: list[UploadErrorResponse] = []
    num_file_duplicates = 0

    for row_num, row in enumerate(csv.DictReader(contents), start=1):
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
            if person.person_id in people_from_file:
                num_file_duplicates += 1
            else:
                people_from_file[person.person_id] = Person(**person.model_dump())

    db_duplicates = set(await get_existing_ids(people_from_file))
    people_to_insert = [
        person
        for person_id, person in people_from_file.items()
        if person_id not in db_duplicates
    ]

    await insert_people(people_to_insert)

    summary = UploadSummaryResponse(
        total_rows=len(people_from_file) + len(errors) + num_file_duplicates,
        valid_rows=len(people_to_insert),
        invalid_rows=len(errors),
        duplicates_skipped=num_file_duplicates + len(db_duplicates),
    )

    return UploadResponse(summary=summary, errors=errors)


@app.post("/clear")
async def clear() -> dict[str, Any]:
    await delete_all_data()
    return {"status": 200, "description": "successfully cleared data"}
