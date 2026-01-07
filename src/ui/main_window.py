from PyQt6.QtWidgets import QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QStackedWidget, \
    QListWidgetItem, QHeaderView, QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("X-Tool")
        self.setGeometry(100, 100, 1200, 700)

        # 设置应用样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QMainWindow::separator {
                background-color: #d0d0d0;
            }
            QMenuBar {
                background-color: #f5f5f5;
                border-bottom: 1px solid #d0d0d0;
                padding: 4px;
                font-size: 14px;
            }
            QMenuBar::item:selected {
                background-color: #e0e0e0;
            }
            QMenu {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
            }
            QMenu::item:selected {
                background-color: #4a90e2;
                color: white;
            }
            QSplitter::handle {
                background-color: #d0d0d0;
            }
            QSplitter::handle:horizontal {
                width: 1px;
            }
        """)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建水平布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建分割器
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        # 创建左侧工具列表
        self.tool_list_widget = QListWidget()
        self.tool_list_widget.setMinimumWidth(220)
        self.tool_list_widget.setMaximumWidth(300)
        self.tool_list_widget.setObjectName("toolList")
        self.tool_list_widget.setStyleSheet("""
            QListWidget#toolList {
                background-color: #ffffff;
                border: none;
                border-right: 1px solid #d0d0d0;
                outline: none;
            }
            QListWidget#toolList::item {
                padding: 12px 15px;
                border-bottom: 1px solid #eee;
                font-size: 14px;
            }
            QListWidget#toolList::item:selected {
                background-color: #4a90e2;
                color: white;
            }
            QListWidget#toolList::item:hover {
                background-color: #e6f0fa;
            }
            QListWidget#toolList::item:selected:hover {
                background-color: #3a7bc8;
            }
        """)
        self.splitter.addWidget(self.tool_list_widget)

        # 创建右侧工具使用界面容器
        self.tool_stack_widget = QStackedWidget()
        self.tool_stack_widget.setStyleSheet("""
            QStackedWidget {
                background-color: #fafafa;
            }
        """)
        self.splitter.addWidget(self.tool_stack_widget)

        # 设置分割器比例
        self.splitter.setSizes([220, 980])

        # 连接工具列表点击信号
        self.tool_list_widget.currentRowChanged.connect(self.on_tool_selected)

        # 添加首页按钮和欢迎页面
        self._add_home_button()
        self._init_welcome_page()

    def _init_welcome_page(self):
        """初始化欢迎页面"""
        welcome_page = self._create_welcome_page()
        self.tool_stack_widget.addWidget(welcome_page)

    def _add_home_button(self):
        """添加首页按钮"""
        item = QListWidgetItem("首页")
        item.setFont(QFont("Microsoft YaHei", 10))
        self.tool_list_widget.addItem(item)

    def _create_welcome_page(self):
        """创建欢迎页面"""
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setContentsMargins(60, 60, 60, 60)
        welcome_layout.setSpacing(20)

        # 标题
        title_label = QLabel("欢迎使用 X-Tool")
        title_font = QFont("Microsoft YaHei", 28, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #333;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(title_label)

        # 副标题
        subtitle_label = QLabel("多功能工具集合平台")
        subtitle_font = QFont("Microsoft YaHei", 16)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #666;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(subtitle_label)

        # 添加弹性空间
        welcome_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # 说明文字
        info_label = QLabel("请从左侧列表选择工具开始使用")
        info_font = QFont("Microsoft YaHei", 14)
        info_label.setFont(info_font)
        info_label.setStyleSheet("color: #888;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(info_label)

        # 添加弹性空间
        welcome_layout.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # 版本信息
        version_label = QLabel("版本 1.0.0")
        version_font = QFont("Microsoft YaHei", 11)
        version_label.setFont(version_font)
        version_label.setStyleSheet("color: #aaa;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(version_label)

        return welcome_widget

    def _add_welcome_page(self):
        """添加欢迎页面作为默认页面"""
        welcome_page = self._create_welcome_page()
        self.tool_stack_widget.addWidget(welcome_page)

    def _clear_welcome_page(self):
        """清除欢迎页面"""
        # 移除欢迎页面（索引0）
        if self.tool_stack_widget.count() > 0:
            welcome_page = self.tool_stack_widget.widget(0)
            self.tool_stack_widget.removeWidget(welcome_page)
            welcome_page.deleteLater()

    def add_tool(self, name, widget):
        """添加工具到列表和堆栈"""
        # 添加到工具列表
        item = QListWidgetItem(name)
        item.setFont(QFont("Microsoft YaHei", 10))
        self.tool_list_widget.addItem(item)

        # 添加到堆栈部件（索引+1，因为索引0是欢迎页面）
        self.tool_stack_widget.addWidget(widget)

    def on_tool_selected(self, index):
        """工具列表选择事件"""
        if index == 0:
            # 首页显示欢迎页面
            self.tool_stack_widget.setCurrentIndex(0)
        elif index > 0:
            # 工具从索引1开始（对应stack的索引1）
            self.tool_stack_widget.setCurrentIndex(index)
