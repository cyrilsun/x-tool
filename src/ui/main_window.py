from PyQt6.QtWidgets import QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QStackedWidget, QListWidgetItem
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("X-Tool")
        self.setGeometry(100, 100, 1000, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建水平布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # 创建左侧工具列表
        self.tool_list_widget = QListWidget()
        self.tool_list_widget.setMinimumWidth(200)
        self.tool_list_widget.setMaximumWidth(300)
        splitter.addWidget(self.tool_list_widget)
        
        # 创建右侧工具使用界面容器
        self.tool_stack_widget = QStackedWidget()
        splitter.addWidget(self.tool_stack_widget)
        
        # 设置分割器比例
        splitter.setSizes([200, 800])
        
        # 连接工具列表点击信号
        self.tool_list_widget.currentRowChanged.connect(self.on_tool_selected)
        
    def add_tool(self, name, widget):
        """添加工具到列表和堆栈"""
        # 添加到工具列表
        item = QListWidgetItem(name)
        self.tool_list_widget.addItem(item)
        
        # 添加到堆栈部件
        self.tool_stack_widget.addWidget(widget)
        
    def on_tool_selected(self, index):
        """工具列表选择事件"""
        if index >= 0:
            self.tool_stack_widget.setCurrentIndex(index)
