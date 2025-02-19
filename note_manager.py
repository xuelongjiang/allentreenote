from typing import Dict, Optional
from pathlib import Path
import shutil
from note import Note
from database import Database

class NoteManager:
    def __init__(self):
        self.notes = {}
        self.db = Database()
        self.root = Note("根目录")
        self.notes[self.root.id] = self.root
        self.images_dir = Path("images")
        self.images_dir.mkdir(exist_ok=True)
        self._load_notes()
    
    def _load_notes(self):
        notes_data = self.db.get_all_notes()
        for note_data in notes_data:
            note_id, title, content, parent_id, position = note_data
            if note_id == self.root.id:
                continue
            note = Note(title, content)
            note.id = note_id
            self.notes[note_id] = note
            
        for note_data in notes_data:
            note_id, _, _, parent_id, _ = note_data
            if note_id == self.root.id or not parent_id:
                continue
            parent = self.notes.get(parent_id, self.root)
            if note_id in self.notes:
                parent.children.append(note_id)
    
    def create_note(self, title: str, parent_id: str) -> str:
        if parent_id not in self.notes:
            return None
        
        new_note = Note(title)
        parent = self.notes[parent_id]
        parent.children.append(new_note.id)
        self.notes[new_note.id] = new_note
        
        position = len(parent.children) - 1
        self.db.save_note(new_note.id, title, "", parent_id, position)
        return new_note.id
    
    def delete_note(self, note_id: str) -> bool:
        if note_id == self.root.id:
            return False
            
        note = self.notes[note_id]
        parent = None
        
        for potential_parent in self.notes.values():
            if note_id in potential_parent.children:
                parent = potential_parent
                break
        
        if parent:
            parent.children.remove(note_id)
            children = note.children.copy()
            for child_id in children:
                self.delete_note(child_id)
            
            del self.notes[note_id]
            self.db.delete_note(note_id)
            return True
            
        return False
    
    def update_note(self, note_id: str, title: str = None, content: str = None) -> bool:
        if note_id not in self.notes:
            return False
            
        note = self.notes[note_id]
        if title is not None:
            note.title = title
        if content is not None:
            note.content = content
            
        parent_id = None
        position = 0
        for potential_parent in self.notes.values():
            if note_id in potential_parent.children:
                parent_id = potential_parent.id
                position = potential_parent.children.index(note_id)
                break
                
        return self.db.save_note(note_id, note.title, note.content, parent_id, position)
    
    def save_image(self, note_id: str, image_path: str) -> str:
        note_images_dir = self.images_dir / note_id
        note_images_dir.mkdir(exist_ok=True)
        
        source_path = Path(image_path)
        target_name = f"{len(list(note_images_dir.glob('*')))}{source_path.suffix}"
        target_path = note_images_dir / target_name
        
        shutil.copy2(image_path, target_path)
        return str(target_path)