# Timetable Management System

A Flask web application for generating and managing college class timetables — built around a JNTUK-style (R20 B.Tech) department structure, with support for faculty, subjects, labs, courses, and per-class scheduling.

## Features

- **Class timetable generation** — auto-builds day/period grids for a given class, with conflict/free-period checks (`generate_class`, `class_reset`).
- **Faculty & department management** — add/edit/delete departments, faculty, designations, and per-faculty login accounts.
- **Course, subject & lab configuration** — manage subjects per semester, lab sessions, and subject types.
- **Multiple report views** — day-wise, period-wise, class-wise, and faculty/lab-wise timetable views, plus free-period listings.
- **Excel export** — generates formatted `.xlsx` timetable and faculty reports using `openpyxl`.
- **Authentication** — session-based login for admin and faculty roles, with email/OTP-based password reset via `Flask-Mail`.

## Tech stack

- **Backend:** Python 3.8, Flask 2.0, Flask-SQLAlchemy, Flask-Mail
- **Database:** SQLite (`jntuk1.db`) — migrated from the original MySQL schema; `insert.py` translates legacy `SHOW TABLES` / `SHOW COLUMNS`-style MySQL calls to SQLite equivalents so the rest of the app is unchanged.
- **Reporting:** openpyxl, pandas
- **Frontend:** Jinja2 templates, static HTML/CSS/JS (jQuery-driven AJAX tables)

## Project structure

```
timetable/
├── appy.py              # Main Flask app: routes, models, timetable logic (~3.4k lines)
├── insert.py             # SQLite connection layer + legacy MySQL SQL translation
├── fac.py, new.py, p.py  # Supporting/utility scripts
├── config.json            # Mail credentials (see Configuration below)
├── requirements.txt
├── appy.wsgi              # WSGI entry point for Apache/mod_wsgi deployment
├── templates/             # Jinja2 templates (dashboard, timetable views, admin forms)
├── static/                 # Static assets
├── reports/                # Generated faculty/timetable Excel reports
└── jntuk1.db               # SQLite database file
```

## Setup

Requires Python 3.8 (pinned dependency versions in `requirements.txt` target this version).

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Configuration

The app reads mail credentials from `config.json`:

```json
{
  "credentials": {
    "user-id": "your-email@gmail.com",
    "pwd": "your-app-password"
  }
}
```

These are used for OTP-based password reset emails via Gmail SMTP (`smtp.gmail.com:465`).

> **Security note:** `config.json` currently contains real credentials committed to source control. Move it out of version control (add to `.gitignore`), rotate the exposed credential, and load it from an environment variable or secrets manager instead.

## Running

```bash
python appy.py
```

The app starts in debug mode on `http://0.0.0.0:5000`.

## Deployment

`appy.wsgi` exposes the app as `application` for deployment behind Apache + mod_wsgi (path is currently hardcoded to `/var/www/appy/timetable` — update to match your server layout).

## Notes

- `.gitignore` excludes `.venv/`, `*.pyc`, `*.xlsx`, and `*.db` — generated reports and the database are expected to be local/regenerated rather than committed.
- Several loose `.xlsx` timetable/faculty reports in the repo root are generated output, not source files.

## Video Demo

- https://drive.google.com/file/d/14cR8jXiR3fPqS6XXBOHbrWvVFS01bwuI/view
