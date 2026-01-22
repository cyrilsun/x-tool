import os
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox, 
    QMessageBox, QWidget, QScrollArea, QTextEdit, QFrame, QApplication,
    QLineEdit, QFormLayout
)
from PyQt6.QtCore import Qt
from src.plugins.base_plugin import BasePlugin
from src.utils.logger import logger

class TextPrefixSuffixPlugin(BasePlugin):
    """
    文本处理插件：批量添加前后缀
    """
    
    def __init__(self):
        super().__init__("批量添加前后缀", "为文本的每一行批量添加指定的前缀和后缀")
        self._setup_ui()

    def get_widget(self) -> QWidget:
        return self

    def on_activate(self):
        logger.info("批量添加前后缀插件被激活")

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
        
        # 文本内容输入
        text_label = QLabel("请输入文本信息:")
        text_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("在这里输入或粘贴文本，每行将被视为一个独立单元...")
        self.input_text.setStyleSheet(self._get_text_edit_qss(False))
        self.input_text.setMinimumHeight(150)
        
        input_layout.addWidget(text_label)
        input_layout.addWidget(self.input_text)
        
        # 前后缀配置 (使用表单布局)
        config_layout = QFormLayout()
        config_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)  # 设置标签左对齐
        config_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)  # 设置整个表单左对齐
        config_layout.setSpacing(10)
        config_layout.setContentsMargins(0, 10, 0, 0)
        
        prefix_label = QLabel("前缀:")
        prefix_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("例如: -->")
        self.prefix_input.setStyleSheet(self._get_line_edit_qss())
        
        suffix_label = QLabel("后缀:")
        suffix_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        self.suffix_input = QLineEdit()
        self.suffix_input.setPlaceholderText("例如: <--")
        self.suffix_input.setStyleSheet(self._get_line_edit_qss())
        
        config_layout.addRow(prefix_label, self.prefix_input)
        config_layout.addRow(suffix_label, self.suffix_input)
        
        input_layout.addLayout(config_layout)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # 2. 结果显示区域
        result_group = QGroupBox("转换结果")
        result_group.setStyleSheet(self._get_group_box_qss())
        result_layout = QVBoxLayout()
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("转换后的结果将显示在这里...")
        self.result_text.setStyleSheet(self._get_text_edit_qss(True))
        self.result_text.setMinimumHeight(150)
        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        # 3. 操作按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.convert_btn = QPushButton("转换")
        self.convert_btn.setStyleSheet(self._get_btn_qss("#3498db", "#2980b9"))
        self.convert_btn.clicked.connect(self.process_text)
        
        self.copy_btn = QPushButton("复制")
        self.copy_btn.setStyleSheet(self._get_btn_qss("#3498db", "#2980b9"))
        self.copy_btn.clicked.connect(self.copy_result)
        
        self.clear_btn = QPushButton("清空输入")
        self.clear_btn.setStyleSheet(self._get_btn_qss("#e67e22", "#d35400"))
        self.clear_btn.clicked.connect(self.clear_inputs)
        
        self.clear_result_btn = QPushButton("清空结果")
        self.clear_result_btn.setStyleSheet(self._get_btn_qss("#e74c3c", "#c0392b"))
        self.clear_result_btn.clicked.connect(lambda: self.result_text.clear())

        btn_layout.addWidget(self.convert_btn)
        btn_layout.addWidget(self.copy_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.clear_result_btn)
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
        
        self.description_content = QTextEdit()
        self.description_content.setReadOnly(True)
        self.description_content.setHtml("""
            <p><strong>批量添加前后缀工具</strong> 用于快速美化或格式化多行文本：</p>
            <ul>
                <li><strong>逐行处理</strong>：自动识别文本行，并为每一行（包括非空行）添加指定内容。</li>
                <li><strong>实时预览</strong>：输入前后缀并点击转换即可看到结果。</li>
                <li><strong>灵活应用</strong>：常用于生成 SQL In 查询列表、格式化日志、代码生成等场景。</li>
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

    def _get_line_edit_qss(self):
        return """
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """

    def _get_btn_qss(self, normal_color, hover_color):
        return f"""
            QPushButton {{ background-color: {normal_color}; color: white; border: none; padding: 10px 24px; font-size: 14px; font-weight: bold; border-radius: 4px; }}
            QPushButton:hover {{ background-color: {hover_color}; }}
        """

    def toggle_description(self):
        if self.description_expanded:
            self.description_scroll.setFixedHeight(50)
            self.toggle_description_btn.setText("▼ 展开")
            self.description_expanded = False
        else:
            self.description_scroll.setFixedHeight(150)
            self.toggle_description_btn.setText("▲ 收起")
            self.description_expanded = True

    def process_text(self):
        """添加前后缀核心逻辑"""
        raw_text = self.input_text.toPlainText()
        prefix = self.prefix_input.text()
        suffix = self.suffix_input.text()
        
        if not raw_text:
            self.result_text.clear()
            return
            
        lines = raw_text.splitlines()
        processed_lines = []
        
        for line in lines:
            # 即使是空行也添加前后缀，符合通用逻辑
            processed_lines.append(f"{prefix}{line}{suffix}")
            
        self.result_text.setPlainText("\n".join(processed_lines))

    def copy_result(self):
        """复制结果到剪贴板"""
        text = self.result_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "提示", "已成功复制到剪贴板")
        else:
            QMessageBox.warning(self, "警告", "没有可复制的内容")

    def clear_inputs(self):
        """清空所有输入配置"""
        self.input_text.clear()
        self.prefix_input.clear()
        self.suffix_input.clear()

    def clear_all(self):
        """清空所有内容"""
        self.clear_inputs()
        self.result_text.clear()
