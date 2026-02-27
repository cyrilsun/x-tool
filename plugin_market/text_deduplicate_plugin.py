import os
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox,
    QMessageBox, QWidget, QScrollArea, QTextEdit, QApplication
)
from PyQt6.QtCore import Qt
from src.plugins.base_plugin import BasePlugin
from src.utils.logger import logger

class TextDeduplicatePlugin(BasePlugin):
    """
    文本处理插件：文本去重
    """

    PLUGIN_INFO = {
        "name": "文本去重工具",
        "description": "支持按行去重，并保留文本原有顺序",
        "version": "1.0.0",
        "category": "文本工具"
    }

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def get_widget(self) -> QWidget:
        return self

    def on_activate(self):
        logger.info("文本去重工具插件被激活")

    def _setup_ui(self):
        """设置UI界面"""
        layout = self.get_content_layout()

        # 核心对比区域 (水平布局)
        comparison_layout = QHBoxLayout()
        comparison_layout.setSpacing(15)

        # 1. 输入区域 (左侧)
        input_group = QGroupBox("待转换内容")
        input_group.setStyleSheet(self._get_group_box_qss())
        input_layout = QVBoxLayout()
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("在这里粘贴或输入需要去重的文本...")
        self.input_text.setStyleSheet(self._get_text_edit_qss(False))
        self.input_text.setMinimumHeight(400)
        input_layout.addWidget(self.input_text)
        input_group.setLayout(input_layout)

        # 2. 中间操作按钮区域
        center_btn_layout = QVBoxLayout()
        center_btn_layout.setSpacing(10)
        center_btn_layout.addStretch()

        self.dedup_btn = QPushButton("文本去重")
        self.dedup_btn.setStyleSheet(self._get_btn_qss("#3498db", "#2980b9"))
        self.dedup_btn.clicked.connect(self.remove_duplicates)
        
        self.copy_btn = QPushButton("复制文本")
        self.copy_btn.setStyleSheet(self._get_btn_qss("#3498db", "#2980b9"))
        self.copy_btn.clicked.connect(self.copy_result)

        self.clear_input_btn = QPushButton("清空输入")
        self.clear_input_btn.setStyleSheet(self._get_btn_qss("#e67e22", "#d35400"))
        self.clear_input_btn.clicked.connect(lambda: self.input_text.clear())

        self.clear_result_btn = QPushButton("清空输出")
        self.clear_result_btn.setStyleSheet(self._get_btn_qss("#e74c3c", "#c0392b"))
        self.clear_result_btn.clicked.connect(lambda: self.result_text.clear())

        center_btn_layout.addWidget(self.dedup_btn)
        center_btn_layout.addWidget(self.copy_btn)
        center_btn_layout.addWidget(self.clear_input_btn)
        center_btn_layout.addWidget(self.clear_result_btn)
        center_btn_layout.addStretch()

        # 3. 结果显示区域 (右侧)
        result_group = QGroupBox("去重后结果")
        result_group.setStyleSheet(self._get_group_box_qss())
        result_layout = QVBoxLayout()
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("去重后的结果将显示在这里...")
        self.result_text.setStyleSheet(self._get_text_edit_qss(True))
        self.result_text.setMinimumHeight(400)
        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)

        comparison_layout.addWidget(input_group, 4)
        comparison_layout.addLayout(center_btn_layout, 1)
        comparison_layout.addWidget(result_group, 4)
        
        layout.addLayout(comparison_layout)

        # 4. 插件说明
        description_html = """
            <p><strong>文本去重工具</strong> 能够快速清理冗余内容：</p>
            <ul>
                <li><strong>顺序保留</strong>：在去除重复行的同时，严格保持第一行出现的先后顺序。</li>
                <li><strong>精准匹配</strong>：对每一行进行完全匹配（包括前后的不可见空格也会被纳入对比）。</li>
                <li><strong>大文本支持</strong>：优化了处理逻辑，支持万级行数的快速去重。</li>
            </ul>
        """
        description_header_layout, self.description_content, self.toggle_description_btn, self.description_scroll = self.create_description_section(description_html)
        layout.addLayout(description_header_layout)
        layout.addWidget(self.description_scroll)

    def _get_group_box_qss(self):
        return """
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
        """

    def _get_text_edit_qss(self, is_readonly):
        bg_color = "#f8f9fa" if is_readonly else "white"
        return f"""
            QTextEdit {{
                font-family: 'Courier New', monospace;
                font-size: 14px;
                padding: 10px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: {bg_color};
                color: #2c3e50;
            }}
        """

    def _get_btn_qss(self, normal_color, hover_color):
        return f"""
            QPushButton {{ background-color: {normal_color}; color: white; border: none; padding: 10px 12px; font-size: 13px; font-weight: bold; border-radius: 4px; min-width: 100px; }}
            QPushButton:hover {{ background-color: {hover_color}; }}
        """

    def remove_duplicates(self):
        """文本去重核心逻辑"""
        raw_text = self.input_text.toPlainText()
        if not raw_text:
            self.result_text.clear()
            return
            
        # 分行处理
        lines = raw_text.splitlines()
        seen = set()
        unique_lines = []
        
        for line in lines:
            if line not in seen:
                seen.add(line)
                unique_lines.append(line)
        
        # 重新组合
        result = "\n".join(unique_lines)
        self.result_text.setPlainText(result)

    def copy_result(self):
        """复制结果到剪贴板"""
        text = self.result_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "提示", "已成功复制到剪贴板")
        else:
            QMessageBox.warning(self, "警告", "没有可复制的内容")
