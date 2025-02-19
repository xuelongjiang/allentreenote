from typing import Dict, Optional
from note import Note
from database import Database
from image_manager import ImageManager

class NoteManager:
    def __init__(self):
        self.notes = {}  # 使用字典存储笔记，key 是笔记 ID，value 是笔记对象
        self.db = Database()  # 添加数据库实例
        self.root = Note("根目录")
        self.notes[self.root.id] = self.root  # 将根节点添加到笔记字典中
        
        # 从数据库加载笔记
        self._load_notes()
    
    def _load_notes(self):
        # 从数据库加载所有笔记
        notes_data = self.db.load_all_notes()
        for note_data in notes_data:
            note = Note(
                note_data['title'],
                note_data['id'],
                note_data['content']
            )
            self.notes[note.id] = note
            
        # 建立父子关系
        for note_data in notes_data:
            if note_data['parent_id']:
                parent = self.notes[note_data['parent_id']]
                parent.children.append(note_data['id'])
    
    def update_note(self, note_id, title=None, content=None):
        note = self.notes[note_id]
        if title is not None:
            note.title = title
        if content is not None:
            note.content = content
            
        # 查找父节点ID
        parent_id = None
        position = 0
        for potential_parent in self.notes.values():
            if note_id in potential_parent.children:
                parent_id = potential_parent.id
                position = potential_parent.children.index(note_id)
                break
                
        return self.db.save_note(note_id, note.title, note.content, parent_id, position)