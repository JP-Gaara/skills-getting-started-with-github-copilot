# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- View current participant emails for each activity, updated after a successful signup
- Sign up for activities
- Unregister participants using the delete icon beside their email; participant lists and available spots refresh automatically

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## Testing

From the repository root, install the dependencies and run the backend tests:

```powershell
python -m pip install -r requirements.txt
python -m pytest tests -v
```

Tests live in `tests/` and use pytest with the Arrange-Act-Assert pattern:

- **Arrange:** prepare inputs, prerequisite state, and expected results.
- **Act:** execute requests and capture their responses.
- **Assert:** check response statuses, payloads, and resulting activity state.

The phases are separated by blank lines. Each test receives
fresh in-memory activity data, restored afterward. FastAPI's TestClient makes
requests in-process; no running server is required, and tests do not alter
registrations on your running website.

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Unregister a participant (404 if the activity or registration does not exist) |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.
