import sqlite3
import os

CURRENT_DIR = os.path.dirname(__file__)
SCHEMA_PATH = os.path.join(CURRENT_DIR, "schema.sql")

# Ensures the database is created at the project root (two folders above db.py)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "storage", "brawl_data.db")

def get_connection():
    """Establishes and returns the connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    return conn

def initdb():
    """Initializes the database using the schema.sql file."""
    conn = get_connection()
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()