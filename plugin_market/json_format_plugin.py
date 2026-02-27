import json
import os
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox,
    QMessageBox, QWidget, QPlainTextEdit, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QTextFormat
from src.plugins.base_plugin import BasePlugin
from src.utils.logger import logger

class JsonFormatPlugin(BasePlugin):
    """
    JSON 格式化与压缩插件
    """

    # 插件元数据
    PLUGIN_INFO = {
        "name": "JSON格式化",
        "description": "支持 JSON 数据的格式化排版与压缩",
        "version": "1.0.0",
        "category": "开发工具",
        "author": "X-Tool",
    }

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def get_widget(self) -> QWidget:
        return self

    def on_activate(self):
        logger.info("JSON格式化插件被激活")

    def _setup_ui(self):
        """设置UI界面"""
        # 使用基类提供的内容布局
        layout = self.get_content_layout()

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
        description_html = """
            <h3>JSON格式化工具</h3>
            <ul>
                <li><strong>格式化</strong>：将凌乱的 JSON 字符串转为缩进整齐（4空格）的易读格式。</li>
                <li><strong>压缩</strong>：去除 JSON 中的所有空格和换行，减小体积。</li>
                <li><strong>兼容性</strong>：支持包含中文等非 ASCII 字符的处理。</li>
                <li><strong>容错</strong>：如果 JSON 格式有误，会弹出错误提示并准确定位原因。</li>
            </ul>
        """
        header_layout, content_text, toggle_btn, scroll_area = self.create_description_section(description_html)
        layout.addLayout(header_layout)
        layout.addWidget(scroll_area)

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
