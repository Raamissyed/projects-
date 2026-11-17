"""Unit tests for the internship tracker; run with unittest discovery."""

import csv
from pathlib import Path
import tempfile
import unittest

from tracker import (
    add_application, export_csv, get_applications, get_stats, open_database,
    update_application, validate_date,
)


class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.connection = open_database(":memory:")

    def tearDown(self):
        self.connection.close()

    def test_new_database_starts_empty(self):
        self.assertEqual(get_applications(self.connection), [])
        self.assertEqual(sum(get_stats(self.connection).values()), 0)

    def test_add_and_filter(self):
        add_application(self.connection, "Example Corp", "Developer Intern", status="applied", application_date="2026-11-17")
        add_application(self.connection, "Another Corp", "QA Intern")
        applied = get_applications(self.connection, "applied")
        self.assertEqual(len(applied), 1)
        self.assertEqual(applied[0]["company"], "Example Corp")
        self.assertEqual(applied[0]["application_date"], "2026-11-17")
        self.assertEqual(len(get_applications(self.connection)), 2)

    def test_invalid_company_and_date(self):
        with self.assertRaises(ValueError):
            add_application(self.connection, "  ", "Developer")
        with self.assertRaises(ValueError):
            add_application(self.connection, "Example", "Developer", application_date="2026-02-30")
        with self.assertRaises(ValueError):
            validate_date("yesterday")

    def test_parameterized_sql_keeps_quotes_and_sql_text_safe(self):
        company = "Example's startup; DROP TABLE applications; --"
        add_application(self.connection, company, "Intern")
        self.assertEqual(get_applications(self.connection)[0]["company"], company)
        self.assertEqual(sum(get_stats(self.connection).values()), 1)

    def test_update_status_and_notes(self):
        app_id = add_application(self.connection, "Example", "Analyst")
        update_application(self.connection, app_id, "interview", notes="Phone screen scheduled")
        app = get_applications(self.connection)[0]
        self.assertEqual(app["status"], "interview")
        self.assertEqual(app["notes"], "Phone screen scheduled")
        self.assertIsNotNone(app["application_date"])

    def test_updating_missing_application_is_error(self):
        with self.assertRaises(ValueError):
            update_application(self.connection, 999, "offer")

    def test_stats_group_by_status(self):
        add_application(self.connection, "A", "Intern")
        add_application(self.connection, "B", "Intern", status="applied")
        add_application(self.connection, "C", "Intern", status="applied")
        self.assertEqual(get_stats(self.connection)["saved"], 1)
        self.assertEqual(get_stats(self.connection)["applied"], 2)
        self.assertEqual(get_stats(self.connection)["interview"], 0)

    def test_csv_export_and_formula_protection(self):
        add_application(self.connection, "=SUM(1,1)", "Developer", notes="@dangerous")
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "applications.csv"
            self.assertEqual(export_csv(self.connection, target), 1)
            with target.open(newline="", encoding="utf-8") as handle:
                exported = list(csv.DictReader(handle))
            self.assertEqual(exported[0]["company"], "'=SUM(1,1)")
            self.assertEqual(exported[0]["notes"], "'@dangerous")

    def test_database_persists_to_disk(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "applications.db"
            with open_database(target) as connection:
                add_application(connection, "Persistent", "Developer")
            with open_database(target) as connection:
                self.assertEqual(get_applications(connection)[0]["company"], "Persistent")


if __name__ == "__main__":
    unittest.main()
