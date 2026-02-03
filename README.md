# Synthetic Population Data Processor

A FastAPI-based backend service that validates and stores synthetic population data from CSV uploads.

---

## Features
- **FastAPI** backend service
- **Async SQLAlchemy + SQLite** database
- **Pydantic v2 validation** for strong typing and data integrity

---

## API Overview

### `GET /`
Health check endpoint.

### `GET /people`
Returns all stored people.

### `POST /upload`
Processes a multi-part uploaded CSV file, validating each row, inserting valid records, and reporting errors.

---

## Data Model

| Field           | Type            | Validation          | Example                |
| --------------- | --------------- | ------------------- | ---------------------- |
| `person_id`     | string          | Required, unique    | `p001`                 |
| `first_name`    | string          | Alphabetic only     | `John`                 |
| `last_name`     | string          | Alphabetic only     | `Smith`                |
| `email`         | string          | Valid email address | `john.smith@gmail.com` |
| `date_of_birth` | date            | Not in the future   | `2025-02-14`           |
| `income`        | float, optional | ≥ 0 if present      | `3.14159`              |

---

## Running the App

### Installing Dependencies
Install the `poetry` project/dependency manager:
```bash
pip install poetry
```

Install the dependencies:
```bash
poetry install
```

### Running the Backend
```bash
poetry shell fastapi dev
```

### Example Usage
- Visit `http://127.0.0.1:8000/docs` in a web browser
- Upload a file via the command line:
```bash
curl -X POST http://127.0.0.1:8000/upload -F "file=@sample_data/sample.csv"
```
