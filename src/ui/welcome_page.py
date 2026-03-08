from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy, QTreeWidgetItem

from src.config.app_config import VERSION
from src.ui.home_page import HomePage


class WelcomePageManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.home_page = None

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
        # 创建新的首页组件，设置主窗口为父窗口
        self.home_page = HomePage(self.main_window)
        self.home_page.plugin_selected.connect(self.on_plugin_selected)
        self.main_window.tool_stack_widget.addWidget(self.home_page)

    def on_plugin_selected(self, plugin_name):
        """处理首页插件选择事件"""
        # 在侧边栏中找到对应的插件项并选中
        self.select_plugin_in_sidebar(plugin_name)
        
    def select_plugin_in_sidebar(self, plugin_name):
        """在侧边栏中选中指定插件"""
        tree = self.main_window.tool_list_widget
        
        # 遍历所有项查找匹配的插件
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i)
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            
            if item_data and item_data.get("type") == "tool":
                if item_data.get("name") == plugin_name:
                    tree.setCurrentItem(item)
                    return
                    
            # 检查子项
            for j in range(item.childCount()):
                child_item = item.child(j)
                child_data = child_item.data(0, Qt.ItemDataRole.UserRole)
                
                if child_data and child_data.get("type") == "tool":
                    if child_data.get("name") == plugin_name:
                        # 展开父项
                        item.setExpanded(True)
                        tree.setCurrentItem(child_item)
                        return

    def create_welcome_page(self):
        """创建欢迎页面（旧版，保留兼容）"""
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setContentsMargins(60, 60, 60, 60)
        welcome_layout.setSpacing(0)

        # 中心卡片容器
        card = QWidget()
        card.setObjectName("welcomeCard")
        card.setStyleSheet("""
            QWidget#welcomeCard {
                background-color: #ffffff;
                border: 1px solid #dcdde1;
                border-radius: 12px;
            }
            QLabel#welcomeTitle {
                color: #2c3e50;
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            QLabel#welcomeDesc {
                color: #7f8c8d;
                font-size: 16px;
            }
            QLabel#featureTitle {
                color: #2c3e50;
                font-size: 18px;
                font-weight: bold;
                margin-top: 20px;
            }
            QLabel#featureList {
                color: #636e72;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(15)

        # 标题
        title_label = QLabel("欢迎使用 X-Tool")
        title_label.setObjectName("welcomeTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        card_layout.addWidget(title_label)

        # 描述
        desc_label = QLabel("一站式插件化桌面工具箱，助力高效开发与办公")
        desc_label.setObjectName("welcomeDesc")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        card_layout.addWidget(desc_label)

        # 分隔线
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #f1f2f6;")
        card_layout.addWidget(line)

        # 功能特性
        feature_title = QLabel("核心功能")
        feature_title.setObjectName("featureTitle")
        card_layout.addWidget(feature_title)

        features = [
            "🚀 插件化架构：支持动态加载与热插拔",
            "📁 灵活分类：支持自定义文件夹与拖拽排序",
            "💾 安全备份：支持插件及关联数据的导出与还原",
            "🛠️ 极致简洁：原生流畅体验，极速启动"
        ]
        
        feature_label = QLabel("\n".join(features))
        feature_label.setObjectName("featureList")
        feature_label.setWordWrap(True)
        card_layout.addWidget(feature_label)

        card_layout.addStretch()

        # 版本信息
        version_label = QLabel(f"Version {VERSION}")
        version_label.setStyleSheet("color: #b2bec3; font-size: 12px;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        card_layout.addWidget(version_label)

        welcome_layout.addWidget(card)

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
