import uuid
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox, 
    QMessageBox, QSpinBox, QCheckBox, QWidget, QScrollArea, 
    QTextEdit, QFrame, QApplication
)
from src.plugins.base_plugin import BasePlugin
from src.utils.logger import logger

class UuidGeneratorPlugin(BasePlugin):
    """
    UUID 生成器插件
    支持批量生成 UUID，可选是否包含中划线
    """
    def __init__(self):
        super().__init__("UUID生成", "批量生成通用唯一识别码 (UUID)")
        self._setup_ui()

    def get_widget(self) -> QWidget:
        return self

    def on_activate(self):
        logger.info("UUID生成器插件被激活")

    def _setup_ui(self):
        """
        设置插件UI界面
        """
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建主滚动区域
        main_scroll = QScrollArea(self)
        main_scroll.setWidgetResizable(True)
        main_scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # 创建滚动区域内的主widget
        scroll_widget = QWidget()
        scroll_widget.setObjectName("pluginContainer")
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        main_scroll.setWidget(scroll_widget)
        main_layout.addWidget(main_scroll)

        # 1. 生成设置区域
        settings_group = QGroupBox("生成设置")
        settings_group.setStyleSheet("""
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
        
        settings_layout = QVBoxLayout()
        
        # 数量设置
        count_layout = QHBoxLayout()
        count_label = QLabel("生成数量:")
        count_label.setStyleSheet("font-size: 14px;")
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 1000)
        self.count_spin.setValue(10)
        self.count_spin.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                min-width: 100px;
            }
        """)
        count_layout.addWidget(count_label)
        count_layout.addWidget(self.count_spin)
        count_layout.addStretch()
        
        # 选项设置
        options_layout = QHBoxLayout()
        self.hyphen_check = QCheckBox("包含中划线 (Hyphens)")
        self.hyphen_check.setChecked(True)
        self.hyphen_check.setStyleSheet("font-size: 14px;")
        
        self.uppercase_check = QCheckBox("大写 (Uppercase)")
        self.uppercase_check.setStyleSheet("font-size: 14px;")
        
        options_layout.addWidget(self.hyphen_check)
        options_layout.addWidget(self.uppercase_check)
        options_layout.addStretch()
        
        settings_layout.addLayout(count_layout)
        settings_layout.addLayout(options_layout)
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # 2. 操作按钮区域
        btn_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("生成 UUID")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_uuids)
        
        self.copy_btn = QPushButton("复制全部")
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        
        self.clear_btn = QPushButton("清空结果")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.clear_btn.clicked.connect(lambda: self.result_text.clear())

        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(self.copy_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 3. 结果显示区域
        result_group = QGroupBox("生成结果")
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
        self.result_text.setPlaceholderText("生成的 UUID 将显示在这里...")
        self.result_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 13px;
                padding: 10px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #fdfdfd;
                color: #2c3e50;
            }
        """)
        self.result_text.setMinimumHeight(300)
        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        # 4. 插件说明区域 (可折叠)
        self.description_expanded = False
        
        description_header_layout = QHBoxLayout()
        description_title = QLabel("<h3 style='margin: 0;'>插件说明</h3>")
        
        self.toggle_description_btn = QPushButton("▼ 展开")
        self.toggle_description_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                color: #343a40;
                border: 1px solid #dee2e6;
                padding: 4px 8px;
                font-size: 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        self.toggle_description_btn.clicked.connect(self.toggle_description)
        
        description_header_layout.addWidget(description_title)
        description_header_layout.addStretch()
        description_header_layout.addWidget(self.toggle_description_btn)
        
        self.description_content = QTextEdit()
        self.description_content.setReadOnly(True)
        self.description_content.setHtml("""
            <p><strong>UUID 生成器</strong> 是一款实用的开发者工具，用于快速生成符合 RFC 4122 标准的 UUID v4。</p>
            <ul>
                <li><strong>中划线选项</strong>：默认生成带标准分隔符的 UUID (如: 550e8400-e29b-41d4-a716-446655440000)。取消勾选可生成 32 位的纯字符。</li>
                <li><strong>批量生成</strong>：支持一次性生成最多 1000 个 UUID。</li>
                <li><strong>复制功能</strong>：一键将所有生成的结果复制到剪贴板，方便粘贴到代码或文档中。</li>
            </ul>
        """)
        
        self.description_scroll = QScrollArea()
        self.description_scroll.setWidget(self.description_content)
        self.description_scroll.setWidgetResizable(True)
        self.description_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.description_scroll.setMaximumHeight(200)
        self.description_scroll.setFixedHeight(50)  # 默认高度
        
        layout.addLayout(description_header_layout)
        layout.addWidget(self.description_scroll)

    def toggle_description(self):
        """切换插件说明的展开/收起状态"""
        if self.description_expanded:
            self.description_scroll.setFixedHeight(50)
            self.toggle_description_btn.setText("▼ 展开")
            self.description_expanded = False
        else:
            self.description_scroll.setFixedHeight(180)
            self.toggle_description_btn.setText("▲ 收起")
            self.description_expanded = True

    def generate_uuids(self):
        """执行生成逻辑"""
        try:
            count = self.count_spin.value()
            include_hyphen = self.hyphen_check.isChecked()
            is_uppercase = self.uppercase_check.isChecked()
            
            uuids = []
            for _ in range(count):
                u = uuid.uuid4()
                u_str = str(u)
                if not include_hyphen:
                    u_str = u_str.replace("-", "")
                if is_uppercase:
                    u_str = u_str.upper()
                uuids.append(u_str)
            
            self.result_text.setPlainText("\n".join(uuids))
            logger.info(f"生成了 {count} 个 UUID")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成 UUID 失败: {str(e)}")

    def copy_to_clipboard(self):
        """将结果复制到剪贴板"""
        text = self.result_text.toPlainText()
        if not text:
            return
            
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        # 弹出一个临时的气泡提示或简单的状态显示（这里用简短的消息框代替）
        QMessageBox.information(self, "成功", "已复制到剪贴板")
