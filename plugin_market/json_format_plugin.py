import json
import os
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox, 
    QMessageBox, QWidget, QScrollArea, QPlainTextEdit, QFrame, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QTextFormat
from src.plugins.base_plugin import BasePlugin
from src.utils.logger import logger

class JsonFormatPlugin(BasePlugin):
    """
    JSON 格式化与压缩插件
    """
    
    def __init__(self):
        super().__init__("JSON格式化", "支持 JSON 数据的格式化排版与压缩")
        self._setup_ui()

    def get_widget(self) -> QWidget:
        return self

    def on_activate(self):
        logger.info("JSON格式化插件被激活")

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
        layout.setSpacing(15)
        
        main_scroll.setWidget(scroll_widget)
        main_layout.addWidget(main_scroll)

        # 1. 标题
        title_label = QLabel("JSON格式化")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 5px;")
        layout.addWidget(title_label)

        # 2. 编辑器区域 (采用深色风格)
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("在这里粘贴或输入 JSON 字符串...")
        self.editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: #ffffff;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 14px;
                padding: 10px;
                line-height: 1.5;
            }
        """)
        self.editor.setMinimumHeight(450)
        layout.addWidget(self.editor)

        # 3. 底部操作按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.format_btn = QPushButton("格式化")
        self.format_btn.setStyleSheet(self._get_btn_qss("#3498db", "#2980b9"))
        self.format_btn.clicked.connect(self.format_json)
        
        self.compress_btn = QPushButton("压缩")
        self.compress_btn.setStyleSheet(self._get_btn_qss("#2c3e50", "#34495e"))
        self.compress_btn.clicked.connect(self.compress_json)

        self.copy_btn = QPushButton("复制内容")
        self.copy_btn.setStyleSheet(self._get_btn_qss("#2ecc71", "#27ae60"))
        self.copy_btn.clicked.connect(self.copy_to_clipboard)

        self.clear_btn = QPushButton("清空")
        self.clear_btn.setStyleSheet(self._get_btn_qss("#e74c3c", "#c0392b"))
        self.clear_btn.clicked.connect(lambda: self.editor.clear())

        btn_layout.addWidget(self.format_btn)
        btn_layout.addWidget(self.compress_btn)
        btn_layout.addWidget(self.copy_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

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
        
        self.description_content = QPlainTextEdit()
        self.description_content.setReadOnly(True)
        self.description_content.setPlainText(
            "JSON格式化工具：\n"
            "1. 格式化：将凌乱的 JSON 字符串转为缩进整齐（4空格）的易读格式。\n"
            "2. 压缩：去除 JSON 中的所有空格和换行，减小体积。\n"
            "3. 兼容性：支持包含中文等非 ASCII 字符的处理。\n"
            "4. 容错：如果 JSON 格式有误，会弹出错误提示并准确定位原因。"
        )
        self.description_scroll = QScrollArea()
        self.description_scroll.setWidget(self.description_content)
        self.description_scroll.setWidgetResizable(True)
        self.description_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.description_scroll.setFixedHeight(50)
        
        layout.addLayout(description_header_layout)
        layout.addWidget(self.description_scroll)

    def _get_btn_qss(self, normal_color, hover_color):
        return f"""
            QPushButton {{ 
                background-color: {normal_color}; 
                color: white; 
                border: none; 
                padding: 10px 24px; 
                font-size: 14px; 
                font-weight: bold; 
                border-radius: 4px; 
            }}
            QPushButton:hover {{ 
                background-color: {hover_color}; 
            }}
        """

    def toggle_description(self):
        if self.description_expanded:
            self.description_scroll.setFixedHeight(50)
            self.toggle_description_btn.setText("▼ 展开")
            self.description_expanded = False
        else:
            self.description_scroll.setFixedHeight(120)
            self.toggle_description_btn.setText("▲ 收起")
            self.description_expanded = True

    def format_json(self):
        """JSON 格式化排版"""
        text = self.editor.toPlainText().strip()
        if not text:
            return
        
        try:
            data = json.loads(text)
            formatted = json.dumps(data, indent=4, ensure_ascii=False)
            self.editor.setPlainText(formatted)
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "JSON 解析错误", f"格式不合法！\n错误信息: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"操作失败: {str(e)}")

    def compress_json(self):
        """JSON 压缩"""
        text = self.editor.toPlainText().strip()
        if not text:
            return
        
        try:
            data = json.loads(text)
            compressed = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
            self.editor.setPlainText(compressed)
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "JSON 解析错误", f"格式不合法！\n错误信息: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"操作失败: {str(e)}")

    def copy_to_clipboard(self):
        """复制内容到剪贴板"""
        text = self.editor.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "提示", "已成功复制到剪贴板")
        else:
            QMessageBox.warning(self, "警告", "没有可复制的内容")
