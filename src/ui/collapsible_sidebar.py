from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLineEdit, QLabel, QSizePolicy, QStackedWidget)
from PyQt6.QtGui import QFont

from src.ui.custom_tree_widget import CustomTreeWidget


class CollapsibleSidebar(QWidget):
    """可折叠侧边栏组件 - 收起时完全隐藏，只显示展开按钮"""
    
    # 展开和收起时的宽度
    EXPANDED_WIDTH = 220
    COLLAPSED_WIDTH = 36  # 只够显示展开按钮的宽度
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.is_expanded = True
        
        # 设置固定宽度
        self.setFixedWidth(self.EXPANDED_WIDTH)
        
        # 创建布局
        self.setup_ui()
        
        # 创建动画
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # 连接动画值变化信号
        self.animation.valueChanged.connect(self.on_animation_value_changed)
        
    def setup_ui(self):
        """初始化UI"""
        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
            QPushButton {
                border: none;
                background-color: transparent;
                padding: 10px;
                font-size: 13px;
                color: #2f3640;
            }
            QPushButton:hover {
                background-color: #f1f2f6;
                color: #3498db;
            }
            QLineEdit {
                padding: 6px 10px;
                border: 1px solid #dcdde1;
                border-radius: 6px;
                background-color: #f8f9fa;
                font-size: 13px;
                color: #2f3640;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
                background-color: #ffffff;
            }
        """)
        
        # 内容容器（包含搜索框和树形控件）
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # 搜索框容器
        self.search_container = QWidget()
        self.search_layout = QVBoxLayout(self.search_container)
        self.search_layout.setContentsMargins(15, 10, 15, 5)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索插件...")
        self.search_layout.addWidget(self.search_input)
        
        self.content_layout.addWidget(self.search_container)
        
        # 树形控件
        self.tree_widget = CustomTreeWidget(self)
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setIndentation(12)
        self.tree_widget.setObjectName("toolList")
        self.tree_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tree_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tree_widget.setStyleSheet("""
            QTreeWidget#toolList {
                background-color: #ffffff;
                border: none;
                outline: none;
                padding-top: 10px;
                selection-background-color: transparent;
                show-decoration-selected: 0;
            }
            QTreeWidget#toolList::item {
                padding: 8px 12px;
                margin: 2px 8px;
                border-radius: 6px;
                color: #2f3640;
                font-family: "Segoe UI", "Microsoft YaHei";
                font-size: 13px;
                border: 1px solid transparent;
            }
            QTreeWidget#toolList::item:hover {
                background-color: #f1f2f6;
                color: #3498db;
            }
            QTreeWidget#toolList::item:selected {
                background-color: #3498db;
                color: #ffffff !important;
                font-weight: bold;
            }
            QTreeWidget#toolList::item:!has-children:selected {
                background-color: #3498db; 
                margin-left: 8px;
            }
            QTreeWidget#toolList::item:selected:hover {
                background-color: #2980b9;
            }
            QTreeWidget#toolList::item:has-children {
                font-weight: bold;
                color: #7f8c8d;
                margin-top: 6px;
            }
            QTreeWidget#toolList::item:has-children:selected {
                color: #ffffff !important;
            }
            QTreeWidget#toolList::branch {
                background-color: transparent;
                width: 0px;
            }
            QTreeWidget#toolList::branch:selected,
            QTreeWidget#toolList::branch:adjoins-item:selected,
            QTreeWidget#toolList::branch:has-children:selected {
                background-color: transparent;
            }
            QTreeWidget#toolList::branch:has-children:open,
            QTreeWidget#toolList::branch:has-children:closed {
                image: none;
            }
        """)
        
        # 设置拖放功能
        self.tree_widget.setDragEnabled(True)
        self.tree_widget.setAcceptDrops(True)
        self.tree_widget.setDropIndicatorShown(True)
        self.tree_widget.setDragDropMode(self.tree_widget.DragDropMode.InternalMove)
        
        self.content_layout.addWidget(self.tree_widget, 1)  # 添加 stretch factor，让树形控件占满剩余空间
        
        # 展开状态下的收起按钮（放在内容容器底部）
        self.button_area = QWidget()
        self.button_area.setFixedHeight(46)
        self.button_area_layout = QHBoxLayout(self.button_area)
        self.button_area_layout.setContentsMargins(10, 5, 10, 5)
        self.button_area_layout.setSpacing(0)

        self.toggle_button_expanded = QPushButton("☰")
        self.toggle_button_expanded.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_button_expanded.setFixedSize(36, 36)
        self.toggle_button_expanded.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                padding: 8px;
                font-size: 16px;
                color: #7f8c8d;
                border-radius: 6px;
                font-family: "Segoe UI", "Microsoft YaHei";
            }
            QPushButton:hover {
                background-color: #f1f2f6;
                color: #3498db;
            }
        """)
        self.toggle_button_expanded.setToolTip("收起侧边栏")
        self.toggle_button_expanded.clicked.connect(self.toggle_sidebar)
        self.button_area_layout.addWidget(self.toggle_button_expanded, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.content_layout.addWidget(self.button_area)
        
        self.main_layout.addWidget(self.content_container, 1)  # 添加 stretch factor

        # 添加弹性空间，将collapsed_button_area推到底部
        self.main_layout.addStretch()

        # 收起状态下的展开按钮（固定在主布局底部，与内容容器互斥显示）
        self.collapsed_button_area = QWidget()
        self.collapsed_button_area.setFixedHeight(46)
        self.collapsed_button_area.setStyleSheet("background-color: transparent;")
        self.collapsed_button_layout = QHBoxLayout(self.collapsed_button_area)
        self.collapsed_button_layout.setContentsMargins(0, 5, 0, 5)
        self.collapsed_button_layout.setSpacing(0)
        self.collapsed_button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.toggle_button_collapsed = QPushButton("☰")
        self.toggle_button_collapsed.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_button_collapsed.setFixedSize(36, 36)
        self.toggle_button_collapsed.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: #f1f2f6;
                padding: 8px;
                font-size: 16px;
                color: #7f8c8d;
                border-radius: 6px;
                font-family: "Segoe UI", "Microsoft YaHei";
            }
            QPushButton:hover {
                background-color: #ffffff;
                color: #3498db;
            }
        """)
        self.toggle_button_collapsed.setToolTip("展开侧边栏")
        self.toggle_button_collapsed.clicked.connect(self.toggle_sidebar)
        self.collapsed_button_layout.addWidget(self.toggle_button_collapsed)

        self.main_layout.addWidget(self.collapsed_button_area)

        # 更新按钮文本和图标
        self.update_toggle_button()

        # 设置初始可见性状态
        self.update_content_visibility()
        
    def update_toggle_button(self):
        """更新切换按钮的显示"""
        if self.is_expanded:
            self.toggle_button_expanded.setText("☰")
            self.toggle_button_expanded.setToolTip("收起侧边栏")
        else:
            self.toggle_button_expanded.setText("☰")
            self.toggle_button_expanded.setToolTip("展开侧边栏")
            
    def update_content_visibility(self):
        """更新内容区域的可见性"""
        if self.is_expanded:
            # 展开状态：显示内容容器（包含展开按钮），隐藏收起按钮区域
            self.content_container.setVisible(True)
            self.collapsed_button_area.setVisible(False)
        else:
            # 收起状态：隐藏内容容器，显示收起按钮区域
            self.content_container.setVisible(False)
            self.collapsed_button_area.setVisible(True)
            
    def toggle_sidebar(self):
        """切换侧边栏展开/收起状态"""
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()
            
    def on_animation_value_changed(self, value):
        """动画值变化时的回调"""
        self.setFixedWidth(int(value))
        
    def collapse(self):
        """收起侧边栏 - 完全隐藏内容，只显示展开按钮"""
        self.is_expanded = False
        
        # 更新按钮文本
        self.update_toggle_button()
        
        # 隐藏内容容器
        self.update_content_visibility()
        
        # 动画收起
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(self.COLLAPSED_WIDTH)
        self.animation.start()
        
        # 通知父窗口调整布局
        if self.parent_window and hasattr(self.parent_window, 'on_sidebar_toggled'):
            self.parent_window.on_sidebar_toggled(self.is_expanded)
            
    def expand(self):
        """展开侧边栏"""
        self.is_expanded = True
        
        # 更新按钮文本
        self.update_toggle_button()
        
        # 显示内容容器
        self.update_content_visibility()
        
        # 动画展开
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(self.EXPANDED_WIDTH)
        self.animation.start()
        
        # 通知父窗口调整布局
        if self.parent_window and hasattr(self.parent_window, 'on_sidebar_toggled'):
            self.parent_window.on_sidebar_toggled(self.is_expanded)
            
    def get_tree_widget(self):
        """获取树形控件"""
        return self.tree_widget
        
    def get_search_input(self):
        """获取搜索框"""
        return self.search_input
