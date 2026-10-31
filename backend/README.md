# NagrikAI Backend

## Overview

NagrikAI is a citizen-assistance platform that helps citizens understand government documents, discover government schemes, check indicative eligibility and manage important reminders.

This backend is developed using Python, FastAPI and MongoDB Atlas.

## Technology Stack

- Python 3.12
- FastAPI
- MongoDB Atlas
- PyMongo
- JWT Authentication
- Pydantic

## Project Structure

```text
backend/
├── app/
│   ├── routes/
│   │   ├── auth.py
│   │   ├── schemes.py
│   │   └── reminders.py
│   ├── schemas/
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── main.py
│   ├── models.py
│   ├── security.py
│   └── seed_schemes.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation

1. Install Python 3.12 or a compatible version.
2. Open a terminal in the backend folder.
3. Create and activate a virtual environment.
4. Install dependencies:

```powershell
pip install -r requirements.txt
```

5. Create a `.env` file using `.env.example` as a template.
6. Add your MongoDB Atlas URI and application secrets to `.env`.

## Run the Backend

```powershell
uvicorn app.main:app --reload
```

Development server:

`http://127.0.0.1:8000`

Swagger API documentation:

`http://127.0.0.1:8000/docs`

## API Endpoints

### Authentication

- POST `/api/auth/signup`
- POST `/api/auth/login`
- GET `/api/auth/me`

### Government Schemes

- GET `/api/schemes`
- GET `/api/schemes?q=student`
- GET `/api/schemes?state=Karnataka`
- POST `/api/schemes/eligibility`

### Reminders

- POST `/api/reminders`
- GET `/api/reminders`
- DELETE `/api/reminders/{reminder_id}`

## Authentication

Protected endpoints require:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Obtain the access token through the login endpoint.

## Database

Database: `nagrikai`

MongoDB Atlas is used for shared application data.

The `.env` file must never be committed to GitHub.

## Integration

The frontend communicates with this backend using HTTP requests and JSON responses.

The document-analysis module should reuse the shared authentication and database interfaces.

## Important Notes

- Scheme eligibility results are indicative and are not official government approvals.
- Demo scheme data must be replaced with verified government information before production use.
- Official scheme links and verification dates should be maintained.
- Notifications and scheduled reminder checks require an additional background worker or scheduler.