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
fastapi dev
```

### Example Usage
```bash
curl -X POST "http://127.0.0.1:8000/upload?filename=sample_data%2Fsample.csv"
```
