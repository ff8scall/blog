import sqlite3
import os

class HistoryManager:
    def __init__(self, db_path="automation/news_history.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """DB 및 테이블 초기화"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def is_already_processed(self, url):
        """이미 처리된 URL인지 확인"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id FROM history WHERE url = ?", (url,))
        result = cur.fetchone()
        conn.close()
        return result is not None

    def add_to_history(self, url, title):
        """처리된 URL 추가"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("INSERT INTO history (url, title) VALUES (?, ?)", (url, title))
            conn.commit()
            conn.close()
            return True
        except:
            return False
