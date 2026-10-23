"""SQLite database layer — persistent project configs, mappings, and scenarios."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "database" / "decisionlab.db"


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    _init_schema(conn)
    return conn


def _init_schema(conn: sqlite3.Connection):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            file_name TEXT
        );

        CREATE TABLE IF NOT EXISTS column_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            column_name TEXT NOT NULL,
            role TEXT NOT NULL,
            confirmed INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        );

        CREATE TABLE IF NOT EXISTS scenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            name TEXT NOT NULL,
            params_json TEXT,
            result_json TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS preferences (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        """
    )
    conn.commit()


def save_project(name: str, file_name: str = "", conn: sqlite3.Connection | None = None) -> int:
    conn = conn or get_connection()
    cur = conn.execute("INSERT INTO projects (name, file_name) VALUES (?, ?)", (name, file_name))
    conn.commit()
    return cur.lastrowid


def list_projects(conn: sqlite3.Connection | None = None) -> list[dict]:
    conn = conn or get_connection()
    rows = conn.execute("SELECT * FROM projects ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


def save_mappings(project_id: int, mappings: dict[str, str], conn: sqlite3.Connection | None = None):
    conn = conn or get_connection()
    conn.execute("DELETE FROM column_mappings WHERE project_id = ?", (project_id,))
    for col, role in mappings.items():
        conn.execute(
            "INSERT INTO column_mappings (project_id, column_name, role, confirmed) VALUES (?, ?, ?, 1)",
            (project_id, col, role),
        )
    conn.commit()


def save_scenario(name: str, params: dict, result: dict, project_id: int | None = None,
                   conn: sqlite3.Connection | None = None) -> int:
    conn = conn or get_connection()
    cur = conn.execute(
        "INSERT INTO scenarios (project_id, name, params_json, result_json) VALUES (?, ?, ?, ?)",
        (project_id, name, json.dumps(params), json.dumps(result)),
    )
    conn.commit()
    return cur.lastrowid


def list_scenarios(conn: sqlite3.Connection | None = None) -> list[dict]:
    conn = conn or get_connection()
    rows = conn.execute("SELECT * FROM scenarios ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]