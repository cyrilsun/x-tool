from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy, QTreeWidgetItem

from src.config.app_config import VERSION


class WelcomePageManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def add_home_button(self):
        """添加首页按钮"""
        # 创建首页项
        home_item = QTreeWidgetItem(["首页"])
        home_item.setFont(0, QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        
        # 设置首页数据
        home_item.setData(0, Qt.ItemDataRole.UserRole, {
            "type": "home"
        })
        
        # 添加到工具列表
        self.main_window.tool_list_widget.addTopLevelItem(home_item)

    def init_welcome_page(self):
        """初始化欢迎页面"""
        welcome_page = self.create_welcome_page()
        self.main_window.tool_stack_widget.addWidget(welcome_page)

    def create_welcome_page(self):
        """创建欢迎页面"""
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setContentsMargins(60, 60, 60, 60)
        welcome_layout.setSpacing(20)

        # 标题
        title_label = QLabel("欢迎使用 X-Tool")
        title_label.setFont(QFont("Microsoft YaHei", 36, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #4a90e2;")
        welcome_layout.addWidget(title_label)

        # 副标题
        subtitle_label = QLabel("您的一站式工具集合")
        subtitle_label.setFont(QFont("Microsoft YaHei", 18))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #666;")
        welcome_layout.addWidget(subtitle_label)

        # 分隔符
        welcome_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # 信息说明
        info_label = QLabel("X-Tool 是一个灵活的工具平台，您可以通过导入插件来扩展功能。\n\n" \
                           "功能特点：\n" \
                           "• 支持插件导入和管理\n" \
                           "• 灵活的文件夹分类\n" \
                           "• 插件拖拽排序\n" \
                           "• 插件备份和恢复")
        info_label.setFont(QFont("Microsoft YaHei", 12))
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #666;")
        info_label.setWordWrap(True)
        welcome_layout.addWidget(info_label)

        # 分隔符
        welcome_layout.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # 版本信息
        version_label = QLabel(f"版本: {VERSION}")
        version_label.setFont(QFont("Microsoft YaHei", 10))
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #999;")
        welcome_layout.addWidget(version_label)

        return welcome_widget

    def add_welcome_page(self):
        """添加欢迎页面"""
        welcome_page = self.create_welcome_page()
        self.main_window.tool_stack_widget.addWidget(welcome_page)

    def clear_welcome_page(self):
        """清除欢迎页面"""
        # 检查是否存在欢迎页面（索引0）
        if self.main_window.tool_stack_widget.count() > 0:
            welcome_page = self.main_window.tool_stack_widget.widget(0)
            self.main_window.tool_stack_widget.removeWidget(welcome_page)
            welcome_page.deleteLater()
