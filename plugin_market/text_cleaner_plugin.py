"""
文本处理插件：去除空行
"""
from typing import TYPE_CHECKING
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGroupBox, QTextEdit, QApplication
)
from src.plugins.base_plugin import BasePlugin
from src.utils.logger import logger

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QWidget


class TextCleanerPlugin(BasePlugin):
    """
    文本处理插件：去除空行
    """

    PLUGIN_INFO = {
        "name": "文本去除空行",
        "description": "将用户粘贴的文本去除所有空行（包括仅含空格的行）",
        "version": "1.0.0",
        "category": "文本工具",
    }

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def get_widget(self) -> QWidget:
        return self

    def on_activate(self):
        logger.info("文本去除空行插件被激活")

    def _setup_ui(self):
        """设置UI界面"""
        # 直接获取内容布局，滚动条已自动设置
        layout = self.get_content_layout()

        # 1. 输入区域
        input_group = QGroupBox("待转换内容")
        input_layout = QVBoxLayout()

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("在这里粘贴或输入需要处理的文本...")
        self.input_text.setMinimumHeight(200)
        input_layout.addWidget(self.input_text)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # 2. 操作按钮区域
        btn_layout = QHBoxLayout()

        self.clean_btn = self.create_button("去除空行", "primary")
        self.clean_btn.clicked.connect(self.remove_blank_lines)

        self.demo_btn = self.create_button("示例demo", "success")
        self.demo_btn.clicked.connect(self.load_demo_data)

        self.clear_btn = self.create_button("清空输入", "warning")
        self.clear_btn.clicked.connect(lambda: self.input_text.clear())

        self.clear_result_btn = self.create_button("清空结果", "danger")
        self.clear_result_btn.clicked.connect(lambda: self.result_text.clear())

        self.copy_btn = self.create_button("复制结果", "info")
        self.copy_btn.clicked.connect(self.copy_result)

        btn_layout.addWidget(self.clean_btn)
        btn_layout.addWidget(self.demo_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.clear_result_btn)
        btn_layout.addWidget(self.copy_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 3. 结果显示区域
        result_group = QGroupBox("转换后结果")
        result_layout = QVBoxLayout()

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("处理后的结果将显示在这里...")
        self.result_text.setMinimumHeight(200)
        result_layout.addWidget(self.result_text)

        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        # 4. 插件说明
        description_html = """
            <p><strong>文本去除空行插件</strong> 提供简单高效的文本清理功能：</p>
            <ul>
                <li><strong>彻底清除</strong>：删除所有完全空白的行。</li>
                <li><strong>智能识别</strong>：对于仅包含空格、制表符（Tab）等不可见字符的行，也会视为"空行"进行清理。</li>
                <li><strong>格式保留</strong>：保留非空行原有的缩进和内容。</li>
            </ul>
        """
        header_layout, content_text, toggle_btn, scroll_area = self.create_description_section(description_html)
        layout.addLayout(header_layout)
        layout.addWidget(scroll_area)

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
        self.log_info("已去除空行")

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
            self.show_info("已成功复制到剪贴板")
        else:
            self.show_warning("没有可复制的内容")
