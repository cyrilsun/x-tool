import os
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox, 
    QMessageBox, QWidget, QScrollArea, QTextEdit, QFrame, QApplication
)
from PyQt6.QtCore import Qt
from src.plugins.base_plugin import BasePlugin
from src.utils.logger import logger

class TextCleanerPlugin(BasePlugin):
    """
    文本处理插件：去除空行
    """
    
    def __init__(self):
        super().__init__("文本去除空行", "将用户粘贴的文本去除所有空行（包括仅含空格的行）")
        self._setup_ui()

    def get_widget(self) -> QWidget:
        return self

    def on_activate(self):
        logger.info("文本去除空行插件被激活")

    def _setup_ui(self):
        """设置UI界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 全局滚动区域
        main_scroll = QScrollArea(self)
        main_scroll.setWidgetResizable(True)
        main_scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        scroll_widget = QWidget()
        scroll_widget.setObjectName("pluginContainer")
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        main_scroll.setWidget(scroll_widget)
        main_layout.addWidget(main_scroll)

        # 1. 输入区域
        input_group = QGroupBox("待转换内容")
        input_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        input_layout = QVBoxLayout()
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("在这里粘贴或输入需要处理的文本...")
        self.input_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 14px;
                padding: 10px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                color: #2c3e50;
            }
        """)
        self.input_text.setMinimumHeight(200)
        input_layout.addWidget(self.input_text)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # 2. 操作按钮区域 (参考图片样式)
        btn_layout = QHBoxLayout()
        
        self.clean_btn = QPushButton("去除空行")
        self.clean_btn.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white; border: none; padding: 10px 24px; font-size: 14px; font-weight: bold; border-radius: 4px; }
            QPushButton:hover { background-color: #2980b9; }
        """)
        self.clean_btn.clicked.connect(self.remove_blank_lines)
        
        self.demo_btn = QPushButton("示例demo")
        self.demo_btn.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white; border: none; padding: 10px 24px; font-size: 14px; font-weight: bold; border-radius: 4px; }
            QPushButton:hover { background-color: #229954; }
        """)
        self.demo_btn.clicked.connect(self.load_demo_data)
        
        self.clear_btn = QPushButton("清空输入框")
        self.clear_btn.setStyleSheet("""
            QPushButton { background-color: #e74c3c; color: white; border: none; padding: 10px 24px; font-size: 14px; font-weight: bold; border-radius: 4px; }
            QPushButton:hover { background-color: #c0392b; }
        """)
        self.clear_btn.clicked.connect(lambda: self.input_text.clear())

        self.copy_btn = QPushButton("复制结果")
        self.copy_btn.setStyleSheet("""
            QPushButton { background-color: #9b59b6; color: white; border: none; padding: 10px 24px; font-size: 14px; font-weight: bold; border-radius: 4px; }
            QPushButton:hover { background-color: #8e44ad; }
        """)
        self.copy_btn.clicked.connect(self.copy_result)

        btn_layout.addWidget(self.clean_btn)
        btn_layout.addWidget(self.demo_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.copy_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 3. 结果显示区域
        result_group = QGroupBox("转换后结果")
        result_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        result_layout = QVBoxLayout()
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("处理后的结果将显示在这里...")
        self.result_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 14px;
                padding: 10px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #f8f9fa;
                color: #2c3e50;
            }
        """)
        self.result_text.setMinimumHeight(200)
        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        # 4. 插件说明
        self.description_expanded = False
        description_header_layout = QHBoxLayout()
        description_title = QLabel("<h3 style='margin: 0;'>插件说明</h3>")
        self.toggle_description_btn = QPushButton("▼ 展开")
        self.toggle_description_btn.setStyleSheet("background-color: #f8f9fa; color: #343a40; border: 1px solid #dee2e6; padding: 4px 8px; font-size: 12px; border-radius: 4px;")
        self.toggle_description_btn.clicked.connect(self.toggle_description)
        description_header_layout.addWidget(description_title)
        description_header_layout.addStretch()
        description_header_layout.addWidget(self.toggle_description_btn)
        
        self.description_content = QTextEdit()
        self.description_content.setReadOnly(True)
        self.description_content.setHtml("""
            <p><strong>文本去除空行插件</strong> 提供简单高效的文本清理功能：</p>
            <ul>
                <li><strong>彻底清除</strong>：删除所有完全空白的行。</li>
                <li><strong>智能识别</strong>：对于仅包含空格、制表符（Tab）等不可见字符的行，也会视为“空行”进行清理。</li>
                <li><strong>格式保留</strong>：保留非空行原有的缩进和内容。</li>
            </ul>
        """)
        self.description_scroll = QScrollArea()
        self.description_scroll.setWidget(self.description_content)
        self.description_scroll.setWidgetResizable(True)
        self.description_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.description_scroll.setFixedHeight(50)
        
        layout.addLayout(description_header_layout)
        layout.addWidget(self.description_scroll)

    def toggle_description(self):
        if self.description_expanded:
            self.description_scroll.setFixedHeight(50)
            self.toggle_description_btn.setText("▼ 展开")
            self.description_expanded = False
        else:
            self.description_scroll.setFixedHeight(150)
            self.toggle_description_btn.setText("▲ 收起")
            self.description_expanded = True

    def remove_blank_lines(self):
        """去除空行核心逻辑"""
        raw_text = self.input_text.toPlainText()
        if not raw_text.strip():
            self.result_text.clear()
            return
            
        # 分行处理，过滤掉 strip() 后为空的行
        lines = raw_text.splitlines()
        clean_lines = [line for line in lines if line.strip()]
        
        # 重新组合
        result = "\n".join(clean_lines)
        self.result_text.setPlainText(result)

    def load_demo_data(self):
        """加载示例数据"""
        demo_text = (
            "白日依山尽\n"
            "\n"
            "黄河入海流\n"
            "    \n"
            "欲穷千里目\n"
            " \t \n"
            "更上一层楼"
        )
        self.input_text.setPlainText(demo_text)

    def copy_result(self):
        """复制结果到剪贴板"""
        text = self.result_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "提示", "已成功复制到剪贴板")
        else:
            QMessageBox.warning(self, "警告", "没有可复制的内容")
