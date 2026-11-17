# Internship Application Tracker

**Python + SQLite | CLI | Automated unit tests**

A small local-first application to keep track of software and IT internship applications. It stores opportunities in a SQLite database and lets you update their status, see totals, and export a spreadsheet-friendly CSV. No account, API key, or paid service is required.

**This is a guided, AI-assisted learning project.** The purpose is to understand SQL queries, input validation, application state, testing, and version control—not to present it as prior professional experience. See [LEARNING.md](LEARNING.md) for a walkthrough and tasks to implement independently.

## Features

- Save a position with a company, role, location, URL, notes, and status
- Filter listings by status (saved, applied, interview, offer, rejected)
- Update status and notes when an application progresses
- Count positions by their current status using SQL GROUP BY
- Export your records to CSV (including basic spreadsheet-formula protection)
- Persist data in a local SQLite database using parameterized SQL
- Run automated unit tests with Python's built-in unittest

## Quick start

Requires **Python 3.9 or later**. No external dependencies.

From the repository root:

```sh
python internship-tracker/tracker.py add --company "Example Tech" --role "Software Intern" --status applied --location "Waterloo"
python internship-tracker/tracker.py add --company "Demo Analytics" --role "Data Intern"
python internship-tracker/tracker.py list
python internship-tracker/tracker.py list --status applied
python internship-tracker/tracker.py update --id 1 --status interview --notes "Recruiter screen"
python internship-tracker/tracker.py stats
python internship-tracker/tracker.py export --output applications.csv
```

The commands create applications.db in your working directory automatically. The database and exported CSV are ignored by Git; **do not commit your real application history or personal notes**. For a custom database file use --db /path/to/my.db **before** the subcommand.

### Run tests

```sh
python -m unittest discover -s internship-tracker -p "test_*.py" -v
```

GitHub Actions also runs the test suite on pull requests and pushes to the main branch.

## Tech choices

- sqlite3: SQL database without a separate server
- argparse: command-line interface
- unittest: automated testing
- csv: importable export file format
- pathlib and datetime: file paths and real calendar dates

## Limitations and next steps

- Command-line only; a web dashboard could be a later iteration
- Status counts show the **current** stage, not a history of every stage reached
- No authentication or cloud sync; records stay on your device
- Next features to build: search by company, edit a saved listing, and a follow-up reminder date

### Example workflow

1. Save interesting opportunities with status saved.
2. Mark them applied after submitting a real application.
3. Update to interview, offer, or rejected as they progress.
4. Review stats weekly and export a CSV when needed.
