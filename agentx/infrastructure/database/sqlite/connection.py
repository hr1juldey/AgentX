"""SQLite connection management.

Handles database initialization and connection lifecycle.
"""

from pathlib import Path
import sqlite3


class SQLiteConnectionManager:
    """Manages SQLite database connection and schema."""

    def __init__(self, db_path: Path | str) -> None:
        """Initialize connection manager.

        Args:
            db_path: Path to SQLite database file.
        """
        self._db_path = Path(db_path) if isinstance(db_path, str) else db_path
        self._conn: sqlite3.Connection | None = None
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        # Ensure data directory exists
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = self.get_connection()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                state TEXT NOT NULL,
                created_at TEXT NOT NULL,
                modified_at TEXT NOT NULL,
                last_activity_at TEXT NOT NULL,
                current_reasoning_step INTEGER DEFAULT 0,
                total_tool_calls INTEGER DEFAULT 0
            )
        """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON sessions(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_state ON sessions(state)")
        conn.commit()

    def get_connection(self) -> sqlite3.Connection:
        """Get or create SQLite connection.

        Returns:
            sqlite3.Connection: The SQLite connection.
        """
        if self._conn is None:
            self._conn = sqlite3.connect(str(self._db_path))
            self._conn.row_factory = sqlite3.Row
        return self._conn
