import sqlite3
import json
from typing import Dict, Any, List
from pathlib import Path
from dingdong.domain.interfaces import MailboxRepository

class SQLiteMailboxRepository(MailboxRepository):
    """
    Implementação persistente do MailboxRepository utilizando SQLite.
    Os dados são gravados fisicamente no disco rígido.
    """
    def __init__(self, db_path: str = "mailbox_storage.db"):
        # Define o caminho do arquivo físico na raiz do projeto
        self.db_path = Path(__file__).resolve().parent / db_path
        self._initialize_database()

    def _initialize_database(self) -> None:
        """
        Cria o arquivo físico e a tabela de banco de dados caso não existam.
        """
        # A instrução 'with' garante que a conexão com o disco seja fechada com segurança
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Criamos uma tabela relacional simples. 
            # O payload (que é um dicionário) será salvo como uma string JSON (TEXT).
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    owner_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save(self, owner_id: str, payload: Dict[str, Any]) -> bool:
        """
        Serializa o dicionário para JSON e o persiste no disco rígido.
        """
        try:
            payload_json = json.dumps(payload)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO notifications (owner_id, payload) VALUES (?, ?)",
                    (owner_id, payload_json)
                )
                conn.commit()
            print(f"[Storage] Salvo fisicamente no disco para {owner_id}")
            return True
        except sqlite3.Error as e:
            print(f"[-] Erro de I/O no disco: {e}")
            return False

    def get_notifications(self, owner_id: str) -> List[Dict[str, Any]]:
        """
        Lê o disco, filtra pelo dono e desserializa o JSON de volta para dicionário.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT payload FROM notifications WHERE owner_id = ? ORDER BY created_at ASC",
                    (owner_id,)
                )
                rows = cursor.fetchall()
                
                # rows é uma lista de tuplas ex: [('{"nome": "ClienteA"}',), ...]
                # Convertendo as strings JSON de volta para dicionários Python
                return [json.loads(row[0]) for row in rows]
                
        except sqlite3.Error as e:
            print(f"[-] Erro de I/O no disco: {e}")
            return []