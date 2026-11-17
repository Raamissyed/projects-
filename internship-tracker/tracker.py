"""A command-line internship application tracker using Python and SQLite."""

import argparse
import csv
from datetime import date
from pathlib import Path
import sqlite3

STATUSES = ("saved", "applied", "interview", "offer", "rejected")
CSV_COLUMNS = ("id", "company", "role", "location", "url", "status", "application_date", "notes")

SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL CHECK(length(trim(company)) > 0),
    role TEXT NOT NULL CHECK(length(trim(role)) > 0),
    location TEXT NOT NULL DEFAULT '',
    url TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL CHECK(status IN ('saved', 'applied', 'interview', 'offer', 'rejected')),
    application_date TEXT,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""


def open_database(path):
    """Open a database and create the table on first use."""
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute(SCHEMA)
    return connection


def validate_date(value):
    """Validate that an optional application date is a real ISO date."""
    if value is None:
        return None
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise ValueError("Date must be valid and use YYYY-MM-DD format") from exc


def add_application(connection, company, role, *, location="", url="", status="saved", application_date=None, notes=""):
    if not company.strip() or not role.strip():
        raise ValueError("Company and role must not be empty")
    if status not in STATUSES:
        raise ValueError(f"Status must be one of: {', '.join(STATUSES)}")
    application_date = validate_date(application_date)
    if status != "saved" and application_date is None:
        application_date = date.today().isoformat()

    with connection:
        cursor = connection.execute(
            """INSERT INTO applications (company, role, location, url, status, application_date, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (company.strip(), role.strip(), location.strip(), url.strip(), status, application_date, notes.strip()),
        )
    return cursor.lastrowid


def get_applications(connection, status=None):
    if status is not None and status not in STATUSES:
        raise ValueError("Invalid status filter")
    if status is None:
        query = "SELECT * FROM applications ORDER BY id DESC"
        return connection.execute(query).fetchall()
    return connection.execute("SELECT * FROM applications WHERE status = ? ORDER BY id DESC", (status,)).fetchall()


def update_application(connection, app_id, status, *, notes=None):
    if status not in STATUSES:
        raise ValueError("Invalid status")
    existing = connection.execute("SELECT application_date, notes FROM applications WHERE id = ?", (app_id,)).fetchone()
    if existing is None:
        raise ValueError(f"Application #{app_id} does not exist")

    application_date = existing["application_date"]
    if status != "saved" and application_date is None:
        application_date = date.today().isoformat()
    new_notes = existing["notes"] if notes is None else notes.strip()
    with connection:
        connection.execute(
            "UPDATE applications SET status = ?, application_date = ?, notes = ? WHERE id = ?",
            (status, application_date, new_notes, app_id),
        )


def get_stats(connection):
    counts = {status: 0 for status in STATUSES}
    for row in connection.execute("SELECT status, COUNT(*) AS total FROM applications GROUP BY status"):
        counts[row["status"]] = row["total"]
    return counts


def safe_csv_value(value):
    """Prevent exported user text from being interpreted as a spreadsheet formula."""
    text = "" if value is None else str(value)
    if text.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def export_csv(connection, path):
    rows = get_applications(connection)
    with open(path, "w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output)
        writer.writerow(CSV_COLUMNS)
        for row in rows:
            writer.writerow([safe_csv_value(row[column]) for column in CSV_COLUMNS])
    return len(rows)


def make_parser():
    parser = argparse.ArgumentParser(description="Track internship applications locally with SQLite")
    parser.add_argument("--db", default="applications.db", help="SQLite database file (default: applications.db)")
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="Save a new internship opportunity or application")
    add.add_argument("--company", required=True)
    add.add_argument("--role", required=True)
    add.add_argument("--location", default="")
    add.add_argument("--url", default="")
    add.add_argument("--status", choices=STATUSES, default="saved")
    add.add_argument("--date", dest="application_date", help="Application date in YYYY-MM-DD format")
    add.add_argument("--notes", default="")

    show = commands.add_parser("list", help="List saved opportunities and applications")
    show.add_argument("--status", choices=STATUSES)

    update = commands.add_parser("update", help="Change an application's status")
    update.add_argument("--id", type=int, required=True)
    update.add_argument("--status", choices=STATUSES, required=True)
    update.add_argument("--notes")

    commands.add_parser("stats", help="Count applications by current status")
    export = commands.add_parser("export", help="Export application data to CSV")
    export.add_argument("--output", type=Path, required=True)
    return parser


def main(argv=None):
    parser = make_parser()
    arguments = parser.parse_args(argv)
    try:
        with open_database(arguments.db) as connection:
            if arguments.command == "add":
                app_id = add_application(
                    connection, arguments.company, arguments.role,
                    location=arguments.location, url=arguments.url,
                    status=arguments.status, application_date=arguments.application_date,
                    notes=arguments.notes,
                )
                print(f"Saved application #{app_id}.")
            elif arguments.command == "list":
                applications = get_applications(connection, arguments.status)
                if not applications:
                    print("No applications found.")
                for app in applications:
                    print(f"#{app['id']} | {app['company']} | {app['role']} | {app['status']} | {app['application_date'] or 'not applied'}")
            elif arguments.command == "update":
                update_application(connection, arguments.id, arguments.status, notes=arguments.notes)
                print(f"Updated application #{arguments.id} to {arguments.status}.")
            elif arguments.command == "stats":
                for status, count in get_stats(connection).items():
                    print(f"{status:10} {count}")
            elif arguments.command == "export":
                count = export_csv(connection, arguments.output)
                print(f"Exported {count} applications to {arguments.output}.")
    except (ValueError, sqlite3.Error, OSError) as exc:
        parser.exit(1, f"Error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
