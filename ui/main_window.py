from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QTreeWidget, QTreeWidgetItem, QTextEdit, QPushButton,
                           QInputDialog, QMessageBox, QFileDialog, QLineEdit)
from PyQt6.QtCore import Qt, QTimer
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from note_manager import NoteManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.note_manager = NoteManager()
        self.search_text = ""
        self.current_search_item = None
        self.init_ui()
        self.setup_shortcuts()
    
    def init_ui(self):
        self.setWindowTitle('Tree Note')
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout()
        central_widget.setLayout(layout)
        
        # 左侧面板
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # 添加搜索框
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索笔记 (F3查找下一个)")
        self.search_box.textChanged.connect(self.on_search_text_changed)
        left_layout.addWidget(self.search_box)
        
        # 添加树形控件
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("笔记")
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.tree.itemClicked.connect(self.on_item_clicked)
        self.tree.dropEvent = self.handle_drop
        left_layout.addWidget(self.tree)
        
        # 添加按钮
        btn_new = QPushButton("新建笔记")
        btn_new.clicked.connect(self.create_new_note)
        left_layout.addWidget(btn_new)
        
        btn_delete = QPushButton("删除笔记")
        btn_delete.clicked.connect(self.delete_current_note)
        left_layout.addWidget(btn_delete)
        
        layout.addWidget(left_panel)
        
        # 右侧面板
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        self.editor = QTextEdit()
        self.editor.textChanged.connect(self.on_content_changed)
        
        btn_insert_image = QPushButton("插入图片")
        btn_insert_image.clicked.connect(self.insert_image)
        
        right_layout.addWidget(self.editor)
        right_layout.addWidget(btn_insert_image)
        
        layout.addWidget(right_panel)
        
        self.refresh_tree()
    
    def setup_shortcuts(self):
        self.tree.itemDoubleClicked.connect(self.rename_note)
        self.tree.keyPressEvent = self.handle_tree_key_press
    
    def handle_tree_key_press(self, event):
        if event.key() == Qt.Key.Key_F2:
            current_item = self.tree.currentItem()
            if current_item:
                self.rename_note(current_item)
        elif event.key() == Qt.Key.Key_F3:
            self.find_next()
        else:
            QTreeWidget.keyPressEvent(self.tree, event)
    
    def on_search_text_changed(self, text):
        self.search_text = text.lower()
        self.current_search_item = None
        if text:
            self.find_next()
    
    def find_next(self):
        if not self.search_text:
            return
            
        start_item = self.current_search_item or self.tree.topLevelItem(0)
        if not start_item:
            return
            
        if self.current_search_item:
            start_item = self.get_next_item(start_item)
            if not start_item:
                start_item = self.tree.topLevelItem(0)
        
        item = start_item
        first_search = True
        while item and (first_search or item != start_item):
            first_search = False
            if self.search_text in item.text(0).lower():
                self.tree.setCurrentItem(item)
                item.setExpanded(True)
                if item.parent():
                    item.parent().setExpanded(True)
                self.current_search_item = item
                return
            item = self.get_next_item(item)
        
        if self.current_search_item:
            self.current_search_item = None
            self.find_next()
    
    def get_next_item(self, item):
        if item.childCount() > 0:
            return item.child(0)
            
        next_sibling = self.get_next_sibling(item)
        if next_sibling:
            return next_sibling
            
        parent = item.parent()
        while parent:
            next_sibling = self.get_next_sibling(parent)
            if next_sibling:
                return next_sibling
            parent = parent.parent()
            
        return self.tree.topLevelItem(0)
    
    def get_next_sibling(self, item):
        parent = item.parent()
        if not parent:
            index = self.tree.indexOfTopLevelItem(item)
            if index < self.tree.topLevelItemCount() - 1:
                return self.tree.topLevelItem(index + 1)
            return None
            
        index = parent.indexOfChild(item)
        if index < parent.childCount() - 1:
            return parent.child(index + 1)
        return None
    
    def on_item_clicked(self, item):
        note_id = item.data(0, Qt.ItemDataRole.UserRole)
        note = self.note_manager.notes[note_id]
        self.editor.setText(note.content)
    
    def create_new_note(self):
        current_item = self.tree.currentItem()
        if not current_item:
            current_item = self.tree.topLevelItem(0)
        
        parent_id = current_item.data(0, Qt.ItemDataRole.UserRole)
        title = "新建笔记"
        note_id = self.note_manager.create_note(title, parent_id)
        
        new_item = QTreeWidgetItem([title])
        new_item.setData(0, Qt.ItemDataRole.UserRole, note_id)
        current_item.addChild(new_item)
        current_item.setExpanded(True)
        
        self.tree.setCurrentItem(new_item)
        self.rename_note(new_item)
    
    def delete_current_note(self):
        current_item = self.tree.currentItem()
        if not current_item:
            return
            
        note_id = current_item.data(0, Qt.ItemDataRole.UserRole)
        note = self.note_manager.notes[note_id]
        
        # 如果有子笔记，需要确认
        if note.children:
            reply = QMessageBox.question(
                self,
                "确认删除",
                f"笔记「{note.title}」包含 {len(note.children)} 个子笔记，确定要删除吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        if self.note_manager.delete_note(note_id):
            parent = current_item.parent()
            parent.removeChild(current_item)
            if parent:
                self.tree.setCurrentItem(parent)
    
    def rename_note(self, item):
        note_id = item.data(0, Qt.ItemDataRole.UserRole)
        if note_id == self.note_manager.root.id:
            return
            
        note = self.note_manager.notes[note_id]
        title, ok = QInputDialog.getText(self, "重命名", "请输入新标题：", text=note.title)
        
        if ok and title:
            note.title = title
            item.setText(0, title)
            self.note_manager.update_note(note_id, title=title)
    
    def on_content_changed(self):
        current_item = self.tree.currentItem()
        if not current_item:
            return
            
        note_id = current_item.data(0, Qt.ItemDataRole.UserRole)
        content = self.editor.toPlainText()
        self.note_manager.update_note(note_id, content=content)
    
    def insert_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        if file_name:
            self.editor.insertHtml(f'<img src="{file_name}" />')
    
    def handle_drop(self, event):
        if not event.isAccepted() and event.source() == self.tree:
            drop_item = self.tree.itemAt(event.pos())
            drag_item = self.tree.currentItem()
            
            if drop_item and drag_item and drag_item != drop_item:
                drag_id = drag_item.data(0, Qt.ItemDataRole.UserRole)
                drop_id = drop_item.data(0, Qt.ItemDataRole.UserRole)
                
                if self.note_manager.move_note(drag_id, drop_id):
                    event.accept()
                    self.refresh_tree()
                    return
                
        event.ignore()
    
    def refresh_tree(self):
        # 保存当前展开状态
        expanded_items = {}
        root_item = self.tree.topLevelItem(0)
        if root_item:
            self._save_expanded_state(root_item, expanded_items)
        
        # 清空并重建树
        self.tree.clear()
        root_item = self._create_tree_item(self.note_manager.root)
        self.tree.addTopLevelItem(root_item)
        
        # 默认展开根节点
        root_item.setExpanded(True)
        
        # 恢复之前的展开状态
        self._restore_expanded_state(root_item, expanded_items)
    
    def _create_tree_item(self, note):
        item = QTreeWidgetItem([note.title])
        item.setData(0, Qt.ItemDataRole.UserRole, note.id)
        
        for child in note.children:
            child_item = self._create_tree_item(self.note_manager.notes[child])
            item.addChild(child_item)
        
        return item
    
    def _save_expanded_state(self, item, expanded_items):
        note_id = item.data(0, Qt.ItemDataRole.UserRole)
        expanded_items[note_id] = item.isExpanded()
        for i in range(item.childCount()):
            self._save_expanded_state(item.child(i), expanded_items)
    
    def _restore_expanded_state(self, item, expanded_items):
        note_id = item.data(0, Qt.ItemDataRole.UserRole)
        if note_id in expanded_items:
            item.setExpanded(expanded_items[note_id])
        for i in range(item.childCount()):
            self._restore_expanded_state(item.child(i), expanded_items)