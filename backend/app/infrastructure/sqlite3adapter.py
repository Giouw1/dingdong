import sqlite3
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union


def get_sqlite3adapter(db_path: str) -> "Sqlite3Adapter":
    return Sqlite3Adapter(db_path=db_path)


class Sqlite3Adapter: 
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._in_memory_conn: Optional[sqlite3.Connection] = None
        
        if self.db_path == ":memory:":
            self._in_memory_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._in_memory_conn.row_factory = sqlite3.Row
            self._in_memory_conn.execute("PRAGMA foreign_keys = ON;")
        elif not self.db_path.startswith("file:"):
            if self.db_path.startswith(("/databases", "\\databases")):
                self.db_path = self.db_path.lstrip("/\\")
            db_file = Path(self.db_path)
            if db_file.suffix == "":
                if str(db_file).rstrip("/\\").endswith("databases"):
                    self.db_path = str(db_file / "app.db")
                else:
                    self.db_path = str(db_file) + ".db"
                db_file = Path(self.db_path)
            if db_file.parent and str(db_file.parent) != ".":
                db_file.parent.mkdir(parents=True, exist_ok=True)

    def get_sqlite3_connection(self) -> sqlite3.Connection:
        """Abre uma conexão com o SQLite configurada para retornar dicts (Row) e com foreign keys habilitadas."""
        if self._in_memory_conn is not None:
            return self._in_memory_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def query(self, sql: str, params: Union[Tuple, List, dict] = ()) -> List[dict]:
        conn = self.get_sqlite3_connection()
        try:
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            if self._in_memory_conn is None:
                conn.close()

    def execute_transaction(self, sql: str, params: Union[Tuple, List, dict] = ()) -> sqlite3.Cursor:
        conn = self.get_sqlite3_connection()
        try:
            cursor = conn.execute(sql, params)
            conn.commit()
            return cursor
        except Exception:
            conn.rollback()
            raise
        finally:
            if self._in_memory_conn is None:
                conn.close()

    def executescript(self, script: str) -> None:
        conn = self.get_sqlite3_connection()
        try:
            conn.executescript(script)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            if self._in_memory_conn is None:
                conn.close()

    def close(self) -> None:
        if self._in_memory_conn is not None:
            self._in_memory_conn.close()
            self._in_memory_conn = None



