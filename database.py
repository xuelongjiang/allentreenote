import sqlite3
from typing import Optional, List, Tuple
from uuid import uuid4

class Database:
    def __init__(self):
        self.db_path = "d:\\program\\tree\\notes.db"
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT,
                    parent_id TEXT,
                    position INTEGER,
                    FOREIGN KEY (parent_id) REFERENCES notes(id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS note_images (
                    id TEXT PRIMARY KEY,
                    note_id TEXT NOT NULL,
                    image_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
                )
            """)
            conn.commit()
    
    def save_note(self, note_id: str, title: str, content: str, parent_id: Optional[str], position: int) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO notes (id, title, content, parent_id, position)
                    VALUES (?, ?, ?, ?, ?)
                """, (note_id, title, content, parent_id, position))
                conn.commit()
            return True
        except Exception as e:
            print(f"保存笔记失败: {e}")
            return False
    
    def delete_note(self, note_id: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
                conn.commit()
            return True
        except Exception as e:
            print(f"删除笔记失败: {e}")
            return False
    
    def get_all_notes(self) -> List[Tuple]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, title, content, parent_id, position 
                    FROM notes 
                    ORDER BY position
                """)
                return cursor.fetchall()
        except Exception as e:
            print(f"获取笔记失败: {e}")
            return []
    
    def add_image(self, note_id: str, image_path: str) -> str:
        image_id = str(uuid4())
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO note_images (id, note_id, image_path)
                    VALUES (?, ?, ?)
                """, (image_id, note_id, image_path))
                conn.commit()
            return image_id
        except Exception as e:
            print(f"添加图片记录失败: {e}")
            return None
    
    def get_note_images(self, note_id: str) -> List[Tuple[str, str]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, image_path 
                    FROM note_images 
                    WHERE note_id = ?
                """, (note_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"获取笔记图片失败: {e}")
            return []