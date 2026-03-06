import sqlite3
import json
import pytest
from unittest.mock import patch
from pollen_monitor.database import init_db, log_reading


@pytest.fixture
def tmp_db(tmp_path):
    db_path = str(tmp_path / "test_pollen.db")
    with patch("pollen_monitor.database.DATABASE_URL", db_path):
        init_db()
        yield db_path


class TestInitDb:

    def test_creates_table(self, tmp_db):
        conn = sqlite3.connect(tmp_db)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pollen_logs'")
        assert cursor.fetchone() is not None
        conn.close()

    def test_idempotent(self, tmp_db):
        """Calling init_db twice should not raise."""
        with patch("pollen_monitor.database.DATABASE_URL", tmp_db):
            init_db()


class TestLogReading:

    def test_inserts_reading(self, tmp_db):
        pollen_data = {"tree": {"value": 3, "category": "Moderate"}}
        health_recs = {"tip": "Wear a mask."}

        with patch("pollen_monitor.database.DATABASE_URL", tmp_db):
            log_reading(35.6, 139.7, "all", 3, pollen_data, health_recs, "Moderate", True)

        conn = sqlite3.connect(tmp_db)
        row = conn.execute("SELECT * FROM pollen_logs").fetchone()
        conn.close()

        assert row is not None
        assert row[1] == 35.6  # latitude
        assert row[2] == 139.7  # longitude
        assert row[3] == "all"  # pollen_type
        assert row[4] == 3  # pollen_level (int)
        assert json.loads(row[5]) == pollen_data
        assert json.loads(row[6]) == health_recs
        assert row[7] == "Moderate"  # index_description
        assert row[8] == 1  # triggered_alert (True -> 1 in SQLite)

    def test_null_optional_fields(self, tmp_db):
        with patch("pollen_monitor.database.DATABASE_URL", tmp_db):
            log_reading(35.6, 139.7, "all", 0, None, None, None, False)

        conn = sqlite3.connect(tmp_db)
        row = conn.execute("SELECT * FROM pollen_logs").fetchone()
        conn.close()

        assert row[5] is None  # pollen_data
        assert row[6] is None  # health_recommendations

    def test_multiple_readings(self, tmp_db):
        with patch("pollen_monitor.database.DATABASE_URL", tmp_db):
            for i in range(5):
                log_reading(35.6, 139.7, "all", i, None, None, None, False)

        conn = sqlite3.connect(tmp_db)
        count = conn.execute("SELECT COUNT(*) FROM pollen_logs").fetchone()[0]
        conn.close()
        assert count == 5
