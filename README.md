# Notes API

A Flask backend where users sign up, log in, and manage their own notes.
It uses session-based login, and users can only see and change their own notes.

## Installation

```bash
pipenv install
pipenv shell
cd server
export FLASK_APP=app.py
flask db upgrade
python seed.py
```

## Run

```bash
flask run -p 5555
```

Test logins: `alice` / `password123` and `bob` / `password123`.

## Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/signup` | Create an account and log in |
| POST | `/login` | Log in |
| DELETE | `/logout` | Log out |
| GET | `/check_session` | Get the logged-in user |
| GET | `/notes?page=1&per_page=5` | List your notes (paginated) |
| POST | `/notes` | Create a note |
| PATCH | `/notes/<id>` | Update your note |
| DELETE | `/notes/<id>` | Delete your note |

All `/notes` routes need you to be logged in, otherwise they return 401.