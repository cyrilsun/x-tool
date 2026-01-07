from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class BaseTool(QWidget):
    """工具基类"""

    def __init__(self, name, description):
        super().__init__()
        self.name = name
        self.description = description

        # 设置背景颜色
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.GlobalColor.white)
        self.setPalette(palette)

        # 创建基础布局
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # 添加标题
        self.title_label = QLabel(f"{name}")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                padding-bottom: 10px;
                border-bottom: 2px solid #3498db;
                margin-bottom: 10px;
            }
        """)
        self.layout.addWidget(self.title_label)

        # 添加描述
        self.desc_label = QLabel(description)
        self.desc_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 14px;
                margin-bottom: 20px;
            }
        """)
        self.layout.addWidget(self.desc_label)
