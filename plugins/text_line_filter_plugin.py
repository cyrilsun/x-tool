import os
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox, 
    QMessageBox, QWidget, QScrollArea, QTextEdit, QFrame, QApplication
)
from PyQt6.QtCore import Qt
from src.plugins.base_plugin import BasePlugin
from src.utils.logger import logger

class TextLineFilterPlugin(BasePlugin):
    """
    文本处理插件：筛选奇数偶数行
    """
    
    def __init__(self):
        super().__init__("筛选奇偶行", "支持批量筛选文本的奇数行和偶数行")
        self._setup_ui()

    def get_widget(self) -> QWidget:
        return self

    def on_activate(self):
        logger.info("筛选奇偶行插件被激活")

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

        # 1. 输入区域
        input_group = QGroupBox("输入设置")
        input_group.setStyleSheet(self._get_group_box_qss())
        input_layout = QVBoxLayout()
        
        input_label = QLabel("文本内容 :")
        input_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("请在这里输入或粘贴待筛选的文本内容...")
        self.input_text.setStyleSheet(self._get_text_edit_qss(False))
        self.input_text.setMinimumHeight(180)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_text)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # 2. 操作按钮区域 (参考图片设计)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.filter_btn = QPushButton("筛选提取")
        self.filter_btn.setStyleSheet(self._get_btn_qss("#3498db", "#2980b9")) # 蓝色
        self.filter_btn.clicked.connect(self.filter_lines)
        
        self.clear_btn = QPushButton("清除文本")
        self.clear_btn.setStyleSheet(self._get_btn_qss("#e74c3c", "#c0392b")) # 红色
        self.clear_btn.clicked.connect(self.clear_all)
        
        self.copy_odd_btn = QPushButton("复制奇数行")
        self.copy_odd_btn.setStyleSheet(self._get_btn_qss("#2ecc71", "#27ae60")) # 绿色
        self.copy_odd_btn.clicked.connect(lambda: self.copy_to_clipboard(self.odd_text.toPlainText()))
        
        self.copy_even_btn = QPushButton("复制偶数行")
        self.copy_even_btn.setStyleSheet(self._get_btn_qss("#2ecc71", "#27ae60")) # 绿色
        self.copy_even_btn.clicked.connect(lambda: self.copy_to_clipboard(self.even_text.toPlainText()))

        btn_layout.addWidget(self.filter_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.copy_odd_btn)
        btn_layout.addWidget(self.copy_even_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 3. 结果显示区域
        # 奇数行
        odd_group = QGroupBox("筛选结果 - 奇数行")
        odd_group.setStyleSheet(self._get_group_box_qss())
        odd_layout = QVBoxLayout()
        odd_label = QLabel("奇数行 :")
        odd_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        self.odd_text = QTextEdit()
        self.odd_text.setReadOnly(True)
        self.odd_text.setStyleSheet(self._get_text_edit_qss(True))
        self.odd_text.setMinimumHeight(150)
        odd_layout.addWidget(odd_label)
        odd_layout.addWidget(self.odd_text)
        odd_group.setLayout(odd_layout)
        
        # 偶数行
        even_group = QGroupBox("筛选结果 - 偶数行")
        even_group.setStyleSheet(self._get_group_box_qss())
        even_layout = QVBoxLayout()
        even_label = QLabel("偶数行 :")
        even_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        self.even_text = QTextEdit()
        self.even_text.setReadOnly(True)
        self.even_text.setStyleSheet(self._get_text_edit_qss(True))
        self.even_text.setMinimumHeight(150)
        even_layout.addWidget(even_label)
        even_layout.addWidget(self.even_text)
        even_group.setLayout(even_layout)

        layout.addWidget(odd_group)
        layout.addWidget(even_group)

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
            <p><strong>筛选奇偶行工具</strong> 用于从文本中快速分离出奇数行和偶数行：</p>
            <ul>
                <li><strong>筛选规则</strong>：第1, 3, 5...行为奇数行；第2, 4, 6...行为偶数行。</li>
                <li><strong>空行处理</strong>：文本中的空行也会被计入行数。</li>
                <li><strong>快速复制</strong>：支持一键单独复制奇数行或偶数行内容。</li>
            </ul>
        """)
        self.description_scroll = QScrollArea()
        self.description_scroll.setWidget(self.description_content)
        self.description_scroll.setWidgetResizable(True)
        self.description_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.description_scroll.setFixedHeight(50)
        
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
            QPushButton {{ background-color: {normal_color}; color: white; border: none; padding: 10px 20px; font-size: 13px; font-weight: bold; border-radius: 4px; }}
            QPushButton:hover {{ background-color: {hover_color}; }}
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

    def filter_lines(self):
        """筛选核心逻辑"""
        raw_text = self.input_text.toPlainText()
        if not raw_text:
            self.odd_text.clear()
            self.even_text.clear()
            return
            
        lines = raw_text.splitlines()
        odd_lines = []
        even_lines = []
        
        for i, line in enumerate(lines):
            if (i + 1) % 2 != 0:
                odd_lines.append(line)
            else:
                even_lines.append(line)
                
        self.odd_text.setPlainText("\n".join(odd_lines))
        self.even_text.setPlainText("\n".join(even_lines))

    def copy_to_clipboard(self, text):
        """复制到剪贴板"""
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "提示", "已成功复制到剪贴板")
        else:
            QMessageBox.warning(self, "警告", "内容为空，无法复制")

    def clear_all(self):
        """清空所有内容"""
        self.input_text.clear()
        self.odd_text.clear()
        self.even_text.clear()
