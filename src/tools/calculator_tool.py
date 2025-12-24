from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit
from PyQt6.QtCore import Qt
from .base_tool import BaseTool

class CalculatorTool(BaseTool):
    """计算器工具"""
    def __init__(self):
        super().__init__("计算器", "简单的计算器工具")
        
        # 创建显示区域
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setStyleSheet("font-size: 24px; padding: 10px;")
        self.layout.addWidget(self.display)
        
        # 创建按钮网格
        buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['0', '.', '=', '+']
        ]
        
        for row in buttons:
            row_layout = QHBoxLayout()
            for btn_text in row:
                button = QPushButton(btn_text)
                button.setStyleSheet("font-size: 18px; padding: 15px;")
                button.clicked.connect(lambda checked, text=btn_text: self.on_button_click(text))
                row_layout.addWidget(button)
            self.layout.addLayout(row_layout)
        
        # 清除按钮
        clear_button = QPushButton("清除")
        clear_button.setStyleSheet("font-size: 18px; padding: 15px; background-color: #ff6b6b;")
        clear_button.clicked.connect(self.on_clear)
        self.layout.addWidget(clear_button)
        
        # 当前表达式
        self.expression = ""
    
    def on_button_click(self, text):
        """按钮点击事件"""
        if text == "=":
            try:
                result = str(eval(self.expression))
                self.display.setText(result)
                self.expression = result
            except:
                self.display.setText("错误")
                self.expression = ""
        else:
            self.expression += text
            self.display.setText(self.expression)
    
    def on_clear(self):
        """清除显示"""
        self.expression = ""
        self.display.setText("")
