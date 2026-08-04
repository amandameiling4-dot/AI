import sqlite3
from pathlib import Path
from typing import List, Dict, Optional


class AppStore:
    """Simple SQLite-backed persistence for thoughts, connected apps, and generated apps."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or "data/app_store.sqlite3")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS thoughts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS connected_apps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_name TEXT NOT NULL,
                    app_id TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS generated_apps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    app_type TEXT NOT NULL,
                    generated_files TEXT NOT NULL,
                    security_checks TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def add_thought(self, content: str, source: str) -> Dict[str, object]:
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO thoughts (content, source) VALUES (?, ?)",
                (content, source),
            )
            conn.commit()
            return {"id": cursor.lastrowid, "content": content, "source": source}

    def list_thoughts(self) -> List[Dict[str, object]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT id, content, source, created_at FROM thoughts ORDER BY id").fetchall()
            return [dict(row) for row in rows]

    def add_connected_app(self, app_name: str, app_id: str) -> Dict[str, object]:
        with self._connect() as conn:
            existing = conn.execute(
                "SELECT id, app_name, app_id FROM connected_apps WHERE app_id = ?",
                (app_id,),
            ).fetchone()
            if existing is not None:
                conn.execute(
                    "UPDATE connected_apps SET app_name = ? WHERE app_id = ?",
                    (app_name, app_id),
                )
                conn.commit()
                return {"id": existing["id"], "app_name": app_name, "app_id": app_id}
            cursor = conn.execute(
                "INSERT INTO connected_apps (app_name, app_id) VALUES (?, ?)",
                (app_name, app_id),
            )
            conn.commit()
            return {"id": cursor.lastrowid, "app_name": app_name, "app_id": app_id}

    def list_connected_apps(self) -> List[Dict[str, object]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT id, app_name, app_id, created_at FROM connected_apps ORDER BY id").fetchall()
            return [dict(row) for row in rows]

    def add_generated_app(
        self,
        project_name: str,
        description: str,
        app_type: str,
        generated_files: List[str],
        security_checks: List[str],
    ) -> Dict[str, object]:
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO generated_apps (project_name, description, app_type, generated_files, security_checks) VALUES (?, ?, ?, ?, ?)",
                (
                    project_name,
                    description,
                    app_type,
                    "|".join(generated_files),
                    "|".join(security_checks),
                ),
            )
            conn.commit()
            return {
                "id": cursor.lastrowid,
                "project_name": project_name,
                "description": description,
                "app_type": app_type,
                "generated_files": generated_files,
                "security_checks": security_checks,
            }

    def list_generated_apps(self) -> List[Dict[str, object]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, project_name, description, app_type, generated_files, security_checks, created_at FROM generated_apps ORDER BY id"
            ).fetchall()
            return [dict(row) for row in rows]
