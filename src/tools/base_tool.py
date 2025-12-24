from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class BaseTool(QWidget):
    """工具基类"""
    def __init__(self, name, description):
        super().__init__()
        self.name = name
        self.description = description
        
        # 创建基础布局
        self.layout = QVBoxLayout(self)
        
        # 添加标题
        self.title_label = QLabel(f"{name}")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.title_label)
        
        # 添加描述
        self.desc_label = QLabel(description)
        self.desc_label.setStyleSheet("color: #666;")
        self.layout.addWidget(self.desc_label)
