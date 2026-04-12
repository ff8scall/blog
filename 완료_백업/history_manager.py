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

    def get_recent_posts(self, limit=10):
        """AI의 내부 링크 생성을 위해 최근 발행된 기사 제목과 URL 목록 반환"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT title, url FROM history ORDER BY processed_at DESC LIMIT ?", (limit,))
            rows = cur.fetchall()
            conn.close()
            return [{"title": row[0], "url": row[1]} for row in rows]
        except:
            return []

    def is_similar_title_exists(self, title, threshold=0.5):
        """최근 100건의 제목과 비교하여 유사도가 높은 것이 있는지 확인 (Jaccard Similarity)"""
        if not title: return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            # 최근 100건의 기사 제목을 가져옴
            cur.execute("SELECT title FROM history ORDER BY processed_at DESC LIMIT 100")
            recent_titles = [row[0] for row in cur.fetchall() if row[0]]
            conn.close()
            
            # 검색어 정규화 (공백 기준 단어 화이트리스트)
            new_words = set(title.split())
            if not new_words: return False
            
            for old_title in recent_titles:
                old_words = set(old_title.split())
                if not old_words: continue
                
                # 단어 교집합 / 합집합 비율 계산 (Jaccard Similarity)
                intersection = new_words.intersection(old_words)
                union = new_words.union(old_words)
                similarity = len(intersection) / len(union)
                
                if similarity >= threshold:
                    return True
            return False
        except:
            return False
