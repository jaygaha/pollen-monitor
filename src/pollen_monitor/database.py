import os
import sqlite3
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "pollen_monitor.db")

def init_db():
    """Initializes the SQLite database and creates the table if it doesn't exist."""
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pollen_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                pollen_type TEXT NOT NULL,
                pollen_level INTEGER NOT NULL,
                pollen_data TEXT,  -- JSON string containing pollen data
                health_recommendations TEXT, -- JSON string containing health recommendations
                index_description TEXT, -- Description of pollen index
                triggered_alert BOOLEAN,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def log_reading(latitude, longitude, pollen_type, pollen_level, pollen_data, health_recommendations, index_description, triggered_alert):
    """Logs a pollen reading into the database."""
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()

        # Serialize pollen_data and health_recommendations as JSON strings for storage
        pollen_data = json.dumps(pollen_data) if pollen_data else None
        health_recommendations = json.dumps(health_recommendations) if health_recommendations else None

        cursor.execute('''
            INSERT INTO pollen_logs (latitude, longitude, pollen_type, pollen_level, pollen_data, health_recommendations, index_description, triggered_alert)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (latitude, longitude, pollen_type, pollen_level, pollen_data, health_recommendations, index_description, triggered_alert))
        conn.commit()