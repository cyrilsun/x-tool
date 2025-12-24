from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QListWidget, QListWidgetItem, QInputDialog
from PyQt6.QtCore import Qt
from .base_tool import BaseTool
from src.db.database import Database

class NoteTool(BaseTool):
    """笔记工具"""
    def __init__(self):
        super().__init__("笔记", "记录和管理笔记")
        
        # 初始化数据库
        self.db = Database()
        
        # 创建主布局
        main_layout = QHBoxLayout()
        self.layout.addLayout(main_layout)
        
        # 左侧笔记列表
        self.note_list = QListWidget()
        self.note_list.setMinimumWidth(200)
        main_layout.addWidget(self.note_list)
        
        # 右侧笔记编辑区域
        self.note_edit = QTextEdit()
        main_layout.addWidget(self.note_edit, 1)
        
        # 按钮布局
        btn_layout = QHBoxLayout()
        self.layout.addLayout(btn_layout)
        
        # 新建笔记按钮
        new_btn = QPushButton("新建笔记")
        new_btn.clicked.connect(self.on_new_note)
        btn_layout.addWidget(new_btn)
        
        # 保存笔记按钮
        save_btn = QPushButton("保存笔记")
        save_btn.clicked.connect(self.on_save_note)
        btn_layout.addWidget(save_btn)
        
        # 删除笔记按钮
        delete_btn = QPushButton("删除笔记")
        delete_btn.clicked.connect(self.on_delete_note)
        btn_layout.addWidget(delete_btn)
        
        # 当前选中的笔记ID
        self.current_note_id = None
        
        # 加载笔记列表
        self.load_notes()
        
        # 连接笔记列表点击信号
        self.note_list.currentRowChanged.connect(self.on_note_selected)
    
    def load_notes(self):
        """加载笔记列表"""
        self.note_list.clear()
        notes = self.db.get_notes()
        for note in notes:
            item = QListWidgetItem(note[1])  # note[1]是笔记标题
            item.setData(Qt.ItemDataRole.UserRole, note[0])  # 存储笔记ID
            self.note_list.addItem(item)
    
    def on_new_note(self):
        """新建笔记"""
        title, ok = QInputDialog.getText(self, "新建笔记", "输入笔记标题:")
        if ok and title:
            note_id = self.db.add_note(title, "")
            if note_id:
                self.load_notes()
                # 选中新创建的笔记
                for i in range(self.note_list.count()):
                    item = self.note_list.item(i)
                    if item.data(Qt.ItemDataRole.UserRole) == note_id:
                        self.note_list.setCurrentItem(item)
                        break
    
    def on_save_note(self):
        """保存笔记"""
        if self.current_note_id is not None:
            content = self.note_edit.toPlainText()
            self.db.update_note(self.current_note_id, content)
    
    def on_delete_note(self):
        """删除笔记"""
        current_item = self.note_list.currentItem()
        if current_item:
            note_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.db.delete_note(note_id)
            self.load_notes()
            self.note_edit.clear()
            self.current_note_id = None
    
    def on_note_selected(self, index):
        """笔记选择事件"""
        if index >= 0:
            current_item = self.note_list.item(index)
            note_id = current_item.data(Qt.ItemDataRole.UserRole)
            note = self.db.get_note(note_id)
            if note:
                self.current_note_id = note_id
                self.note_edit.setPlainText(note[2])  # note[2]是笔记内容
