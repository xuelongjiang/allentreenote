from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QTreeWidget, QTreeWidgetItem, QTextEdit, QPushButton,
                           QInputDialog, QMessageBox, QFileDialog, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCharFormat, QTextCursor
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
    def on_item_clicked(self, item):
        """处理树形控件项点击事件"""
        note_id = item.data(0, Qt.ItemDataRole.UserRole)
        note = self.note_manager.notes[note_id]
        self.editor.setText(note.content)
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
        
        # 添加搜索面板
        search_panel = QWidget()
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_panel.setLayout(search_layout)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索笔记")
        self.search_box.textChanged.connect(self.on_search_text_changed)
        search_layout.addWidget(self.search_box)
        
        btn_search = QPushButton("查找下一个")
        btn_search.setToolTip("F3")
        btn_search.clicked.connect(self.find_next)
        search_layout.addWidget(btn_search)
        
        left_layout.addWidget(search_panel)
        
        # 添加树形控件
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("笔记")
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.tree.itemClicked.connect(self.on_item_clicked)
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
        # 清除之前的高亮
        self.clear_highlight()
    def find_next(self):
        if not self.search_text:
            self.search_text = self.search_box.text().lower()
            if not self.search_text:
                QMessageBox.information(self, "搜索", "请输入搜索内容")
                return
        
        # 获取所有节点
        all_items = []
        self._collect_tree_items(self.tree.topLevelItem(0), all_items)
        
        if not all_items:
            QMessageBox.information(self, "搜索", "没有可搜索的项目")
            return
        
        # 确定开始位置
        start_index = 0
        if self.current_search_item in all_items:
            start_index = all_items.index(self.current_search_item) + 1
        
        # 搜索下一个匹配项
        found = False
        for i in range(len(all_items)):
            index = (start_index + i) % len(all_items)
            if index == 0 and i > 0:
                QMessageBox.information(self, "搜索", "已到尾部，将从头开始搜索")
            item = all_items[index]
            note_id = item.data(0, Qt.ItemDataRole.UserRole)
            note = self.note_manager.notes[note_id]
            
            # 检查标题和内容
            if self.search_text in item.text(0).lower() or self.search_text in note.content.lower():
                self.tree.setCurrentItem(item)
                item.setExpanded(True)
                if item.parent():
                    item.parent().setExpanded(True)
                self.current_search_item = item
                
                # 自动显示匹配的笔记内容
                self.editor.setText(note.content)
                
                # 高亮显示搜索内容
                self.highlight_search_text(note.content)
                found = True
                break
        
        # 未找到新的匹配项
        if not found:
            QMessageBox.information(self, "搜索", "搜索已完成，没有新的匹配项")
            self.current_search_item = None
    def clear_highlight(self):
        cursor = self.editor.textCursor()
        cursor.setPosition(0)
        cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
        cursor.setCharFormat(QTextCharFormat())
    def highlight_search_text(self, content):
        cursor = self.editor.textCursor()
        format = QTextCharFormat()
        format.setBackground(Qt.GlobalColor.yellow)
        
        # 清除之前的高亮
        self.clear_highlight()
        
        # 搜索并高亮
        pos = 0
        while pos >= 0:
            pos = content.lower().find(self.search_text, pos)
            if pos >= 0:
                # 确保光标位置在文本范围内
                if pos + len(self.search_text) <= len(content):
                    cursor.setPosition(pos)
                    cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, len(self.search_text))
                    cursor.setCharFormat(format)
                pos += len(self.search_text)
    def _collect_tree_items(self, item, items):
        if not item:
            return
        items.append(item)
        for i in range(item.childCount()):
            self._collect_tree_items(item.child(i), items)
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
    def create_new_note(self):
        """创建新笔记"""
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
            if parent:
                parent.removeChild(current_item)
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
        content = self.editor.toHtml()
        self.note_manager.update_note(note_id, content=content)
    def insert_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        if file_name:
            current_item = self.tree.currentItem()
            if current_item:
                note_id = current_item.data(0, Qt.ItemDataRole.UserRole)
                saved_path = self.note_manager.save_image(note_id, file_name)
                if saved_path:
                    self.editor.insertHtml(f'<img src="{saved_path}" />')
                    self.on_content_changed()
    def refresh_tree(self):
        expanded_items = {}
        root_item = self.tree.topLevelItem(0)
        if root_item:
            self._save_expanded_state(root_item, expanded_items)
        
        self.tree.clear()
        root_item = self._create_tree_item(self.note_manager.root)
        self.tree.addTopLevelItem(root_item)
        root_item.setExpanded(True)
        
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