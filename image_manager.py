import os
import shutil
from uuid import uuid4
from typing import Optional

class ImageManager:
    def __init__(self):
        self.base_dir = "d:\\program\\tree\\images"
        os.makedirs(self.base_dir, exist_ok=True)
    
    def _get_note_image_dir(self, note_id: str) -> str:
        note_image_dir = os.path.join(self.base_dir, note_id)
        os.makedirs(note_image_dir, exist_ok=True)
        return note_image_dir
    
    def save_image(self, note_id: str, source_path: str) -> Optional[str]:
        try:
            note_image_dir = self._get_note_image_dir(note_id)
            ext = os.path.splitext(source_path)[1]
            new_filename = f"{uuid4()}{ext}"
            new_path = os.path.join(note_image_dir, new_filename)
            
            shutil.copy2(source_path, new_path)
            return f"images/{note_id}/{new_filename}"
        except Exception as e:
            print(f"保存图片失败: {e}")
            return None
    
    def delete_note_images(self, note_id: str) -> bool:
        try:
            note_image_dir = os.path.join(self.base_dir, note_id)
            if os.path.exists(note_image_dir):
                shutil.rmtree(note_image_dir)
            return True
        except Exception as e:
            print(f"删除笔记图片失败: {e}")
            return False