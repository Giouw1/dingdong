import json
import sqlite3
from datetime import datetime
from typing import Any, List, Optional, Union

from app.domain.entities import NotificationPayload, OwnerID
from app.domain.storage_interfaces import AbstractMailboxRepository
from app.infrastructure.sqlite3adapter import Sqlite3Adapter, get_sqlite3adapter


def _extract_owner_id(val: Union[OwnerID, str, int]) -> str:
    if isinstance(val, OwnerID):
        return str(val.owner_id)
    return str(val)


def _parse_timestamp(ts_str: Optional[str]) -> Optional[datetime]:
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str)
    except Exception:
        return None


class SQLite3Mailbox(AbstractMailboxRepository):
    def __init__(self, db_path: str = ":memory:", sqlite3adapter: Optional[Sqlite3Adapter] = None):
        self.sql_adapter = sqlite3adapter if sqlite3adapter is not None else get_sqlite3adapter(db_path=db_path)
        table_creation = """
        CREATE TABLE IF NOT EXISTS Mailbox ( 
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id TEXT NOT NULL,
            notification_content TEXT NOT NULL,
            read INTEGER NOT NULL DEFAULT 0,
            timestamp TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_mailbox_owner ON Mailbox(owner_id);
        """
        self.sql_adapter.executescript(table_creation)

    def save(self, target_id: Union[OwnerID, str, int], payload: Any) -> bool:
        owner_str = _extract_owner_id(target_id)
        
        if isinstance(payload, NotificationPayload):
            ts = payload.timestamp.isoformat() if isinstance(payload.timestamp, datetime) else (str(payload.timestamp) if payload.timestamp else datetime.now().isoformat())
            content = payload.conteudo
            read = 1 if payload.lida else 0
        else:
            ts = datetime.now().isoformat()
            content = json.dumps(payload)
            read = 0

        save_statement = """
        INSERT INTO Mailbox (owner_id, notification_content, read, timestamp)
        VALUES (?, ?, ?, ?);
        """
        self.sql_adapter.execute_transaction(save_statement, (owner_str, content, read, ts))
        return True

    def get_notifications(self, target_id: Union[OwnerID, str, int]) -> Optional[List[Any]]:
        owner_str = _extract_owner_id(target_id)
        get_statement = """
        SELECT notification_content, read, timestamp FROM Mailbox
        WHERE owner_id = ?
        ORDER BY id ASC;
        """
        rows = self.sql_adapter.query(get_statement, (owner_str,))
        if not rows:
            return None

        result: List[Any] = []
        for r in rows:
            raw_content = r["notification_content"]
            try:
                parsed = json.loads(raw_content)
                if isinstance(parsed, (list, dict, str)) and raw_content.startswith(('"', "[", "{")):
                    result.append(parsed)
                    continue
            except Exception:
                pass

            result.append(
                NotificationPayload(
                    conteudo=raw_content,
                    lida=bool(r["read"]),
                    timestamp=_parse_timestamp(r["timestamp"]),
                )
            )
        return result

    def delete_user(self, target_id: Union[OwnerID, str, int]) -> bool:
        owner_str = _extract_owner_id(target_id)
        check_statement = "SELECT 1 FROM Mailbox WHERE owner_id = ? LIMIT 1;"
        rows = self.sql_adapter.query(check_statement, (owner_str,))
        if not rows:
            return False

        delete_statement = "DELETE FROM Mailbox WHERE owner_id = ?;"
        self.sql_adapter.execute_transaction(delete_statement, (owner_str,))
        return True

        






