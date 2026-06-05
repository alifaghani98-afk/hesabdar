"""
database.py - SQLite database initialization and connection management
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'hesabdar.db')


def get_connection():
    """Return a new SQLite connection with row_factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they do not exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            description TEXT    DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS counterparties (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name  TEXT    NOT NULL UNIQUE,
            phone TEXT    DEFAULT '',
            note  TEXT    DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id       INTEGER NOT NULL,
            counterparty_id  INTEGER NOT NULL,
            jalali_date      TEXT    NOT NULL,
            description      TEXT    DEFAULT '',
            debit            REAL    NOT NULL DEFAULT 0,
            credit           REAL    NOT NULL DEFAULT 0,
            FOREIGN KEY (project_id)      REFERENCES projects(id)      ON DELETE CASCADE,
            FOREIGN KEY (counterparty_id) REFERENCES counterparties(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()
