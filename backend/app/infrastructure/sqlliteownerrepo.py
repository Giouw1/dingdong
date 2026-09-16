
import sqlite3
from typing import Optional, Union

from app.domain.entities import Nickname, OwnerID, UserData
from app.domain.storage_interfaces import AbstractIDGenerator, AbstractOwnerRepository
from app.infrastructure.sqlite3adapter import Sqlite3Adapter, get_sqlite3adapter


def _extract_owner_id(val: Union[OwnerID, str, int]) -> str:
    if isinstance(val, OwnerID):
        return str(val.owner_id)
    return str(val)


def _extract_nickname(val: Union[Nickname, str]) -> str:
    if isinstance(val, Nickname):
        return str(val.nickname)
    return str(val)


class SQLite3OwnerRepo(AbstractOwnerRepository):
    def __init__(self, db_path: str = ":memory:", sqlite3adapter: Optional[Sqlite3Adapter] = None):
        self.sql_adapter = sqlite3adapter if sqlite3adapter is not None else get_sqlite3adapter(db_path=db_path)
        table_creation = """
        CREATE TABLE IF NOT EXISTS Owner_Credentials ( 
            username TEXT UNIQUE PRIMARY KEY,
            password TEXT NOT NULL,
            owner_id TEXT UNIQUE NOT NULL
        );
        CREATE TABLE IF NOT EXISTS Owner_Nickname (
            nickname TEXT PRIMARY KEY,
            owner_id TEXT UNIQUE NOT NULL,
            FOREIGN KEY(owner_id) REFERENCES Owner_Credentials(owner_id) ON DELETE CASCADE
        );
        """
        self.sql_adapter.executescript(table_creation)

    def register_user(self, owner_id: Union[OwnerID, str, int], user_data: UserData) -> bool:
        oid = _extract_owner_id(owner_id)
        user_registration = """
        INSERT INTO Owner_Credentials (username, password, owner_id)
        VALUES (?, ?, ?);
        """
        try:
            self.sql_adapter.execute_transaction(user_registration, (user_data.username, user_data.password, oid))
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user_id(self, user_data: UserData) -> Optional[OwnerID]:
        user_id_retrieval = """
        SELECT owner_id FROM Owner_Credentials
        WHERE username = ? AND password = ?;
        """
        rows = self.sql_adapter.query(user_id_retrieval, (user_data.username, user_data.password))
        if rows:
            return OwnerID(owner_id=str(rows[0]["owner_id"]))
        return None

    def delete_user(self, user_data: UserData) -> bool:
        user_lookup = """
        SELECT owner_id FROM Owner_Credentials
        WHERE username = ? AND password = ?;
        """
        rows = self.sql_adapter.query(user_lookup, (user_data.username, user_data.password))
        if not rows:
            return False
        
        oid = str(rows[0]["owner_id"])
        self.sql_adapter.execute_transaction("DELETE FROM Owner_Nickname WHERE owner_id = ?;", (oid,))
        self.sql_adapter.execute_transaction(
            "DELETE FROM Owner_Credentials WHERE username = ? AND password = ?;",
            (user_data.username, user_data.password)
        )
        return True

    def register_nickname(self, owner_id: Union[OwnerID, str, int], nickname: Union[Nickname, str]) -> Optional[bool]:
        oid = _extract_owner_id(owner_id)
        nick = _extract_nickname(nickname)

        rows_nick = self.sql_adapter.query("SELECT owner_id FROM Owner_Nickname WHERE nickname = ?;", (nick,))
        if rows_nick:
            if str(rows_nick[0]["owner_id"]) != oid:
                return False
            return True

        rows_owner = self.sql_adapter.query("SELECT nickname FROM Owner_Nickname WHERE owner_id = ?;", (oid,))
        if rows_owner:
            return self.change_nickname(owner_id=owner_id, nickname=nickname)

        try:
            self.sql_adapter.execute_transaction(
                "INSERT INTO Owner_Nickname (nickname, owner_id) VALUES (?, ?);",
                (nick, oid)
            )
            return True
        except sqlite3.IntegrityError:
            return False

    def change_nickname(self, owner_id: Union[OwnerID, str, int], nickname: Union[Nickname, str]) -> Optional[bool]:
        oid = _extract_owner_id(owner_id)
        nick = _extract_nickname(nickname)

        rows_owner = self.sql_adapter.query("SELECT nickname FROM Owner_Nickname WHERE owner_id = ?;", (oid,))
        if not rows_owner:
            return self.register_nickname(owner_id=owner_id, nickname=nickname)

        rows_nick = self.sql_adapter.query("SELECT owner_id FROM Owner_Nickname WHERE nickname = ?;", (nick,))
        if rows_nick and str(rows_nick[0]["owner_id"]) != oid:
            return False

        self.sql_adapter.execute_transaction(
            "UPDATE Owner_Nickname SET nickname = ? WHERE owner_id = ?;",
            (nick, oid)
        )
        return True

    def get_user_id_by_nickname(self, nickname: Union[Nickname, str]) -> Optional[OwnerID]:
        nick = _extract_nickname(nickname)
        get_id_by_nick = "SELECT owner_id FROM Owner_Nickname WHERE nickname = ?;"
        rows = self.sql_adapter.query(get_id_by_nick, (nick,))
        if rows:
            return OwnerID(owner_id=str(rows[0]["owner_id"]))
        return None

    def get_nickname(self, owner_id: Union[OwnerID, str, int]) -> Optional[Nickname]:
        oid = _extract_owner_id(owner_id)
        get_nick = "SELECT nickname FROM Owner_Nickname WHERE owner_id = ?;"
        rows = self.sql_adapter.query(get_nick, (oid,))
        if rows:
            return Nickname(nickname=str(rows[0]["nickname"]))
        return None

    def get_largest_id(self) -> OwnerID:
        get_largid = "SELECT MAX(CAST(owner_id AS INTEGER)) as max_id FROM Owner_Credentials;"
        rows = self.sql_adapter.query(get_largid)
        if rows and rows[0]["max_id"] is not None:
            return OwnerID(owner_id=str(rows[0]["max_id"]))
        return OwnerID(owner_id="0")


class SQLite3IDGenerator(AbstractIDGenerator):
    def __init__(self, repository: SQLite3OwnerRepo):
        self.repo = repository

    def generate_id(self) -> OwnerID:
        largest = self.repo.get_largest_id()
        max_val = int(largest.owner_id) if (largest and largest.owner_id) else 0
        return OwnerID(owner_id=str(max_val + 1))

    def expose_repo(self) -> SQLite3OwnerRepo:
        return self.repo

