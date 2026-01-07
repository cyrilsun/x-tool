from PyQt6.QtWidgets import QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QStackedWidget, \
    QListWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


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

    def add_tool(self, name, widget):
        """添加工具到列表和堆栈"""
        # 添加到工具列表
        item = QListWidgetItem(name)
        item.setFont(QFont("Microsoft YaHei", 10))
        self.tool_list_widget.addItem(item)

        # 添加到堆栈部件
        self.tool_stack_widget.addWidget(widget)

    def on_tool_selected(self, index):
        """工具列表选择事件"""
        if index >= 0:
            self.tool_stack_widget.setCurrentIndex(index)
