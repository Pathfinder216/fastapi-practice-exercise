from typing_extensions import TypedDict


class UploadSummaryResponse(TypedDict):
    total_rows: int
    inserted_rows: int
    invalid_rows: int
    duplicates_skipped: int


class UploadErrorResponse(TypedDict):
    row_number: int
    errors: list[str]


class UploadResponse(TypedDict):
    summary: UploadSummaryResponse
    errors: list[UploadErrorResponse]
