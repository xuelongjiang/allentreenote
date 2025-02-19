from datetime import datetime
from typing import Optional, List

class Note:
    def __init__(self, title: str, content: str = "", parent: Optional['Note'] = None):
        self.id = str(datetime.now().timestamp())
        self.title = title
        self.content = content
        self.parent = parent
        self.children: List[Note] = []
        
    def add_child(self, child: 'Note') -> bool:
        if self._would_create_cycle(child):
            return False
        
        child.parent = self
        self.children.append(child)
        return True
    
    def remove_child(self, child: 'Note') -> None:
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            
    def _would_create_cycle(self, new_child: 'Note') -> bool:
        current = self
        while current:
            if current == new_child:
                return True
            current = current.parent
        return False