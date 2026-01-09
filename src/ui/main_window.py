from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QSplitter, QWidget, QHBoxLayout, \
    QStackedWidget

from src.ui.custom_tree_widget import CustomTreeWidget
from src.ui.folder_manager import FolderManager
from src.ui.menu_manager import MenuManager
from src.ui.tool_manager import ToolManager
from src.ui.welcome_page import WelcomePageManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("X-Tool")
        self.setGeometry(100, 100, 1200, 700)
        
        # 插件与widget映射
        self.plugin_widget_map = {}
        
        # 插件文件夹映射，用于数据库操作
        self.plugin_folder_map = {}  # plugin_name: folder_id

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

        # 创建左侧工具列表（树形结构）
        self.tool_list_widget = CustomTreeWidget(self)
        self.tool_list_widget.setMinimumWidth(220)
        self.tool_list_widget.setMaximumWidth(300)
        self.tool_list_widget.setObjectName("toolList")
        self.tool_list_widget.setHeaderHidden(True)
        self.tool_list_widget.setStyleSheet("""
            QTreeWidget#toolList {
                background-color: #ffffff;
                border: none;
                border-right: 1px solid #d0d0d0;
                outline: none;
            }
            QTreeWidget#toolList::item {
                padding: 8px 15px;
                border-bottom: 1px solid #eee;
                font-size: 14px;
            }
            QTreeWidget#toolList::item:selected {
                background-color: #4a90e2;
                color: white;
            }
            QTreeWidget#toolList::item:hover {
                background-color: #e6f0fa;
            }
            QTreeWidget#toolList::item:selected:hover {
                background-color: #3a7bc8;
            }
            QTreeWidget#toolList QTreeWidgetItem {
                margin-bottom: 2px;
            }
            /* 优化文件夹展开/折叠指示器样式 */
            QTreeWidget#toolList::branch {
                background-color: white;
            }
            QTreeWidget#toolList::branch:has-siblings:!adjoins-item {
                border-image: none;
                background-color: white;
            }
            QTreeWidget#toolList::branch:has-siblings:adjoins-item {
                border-image: none;
                background-color: white;
            }
            QTreeWidget#toolList::branch:!has-children:!has-siblings:adjoins-item {
                border-image: none;
                background-color: white;
            }
            /* 展开指示器颜色 */
            QTreeWidget#toolList::branch:open {
                background-color: white;
            }
            QTreeWidget#toolList::branch:closed {
                background-color: white;
            }
        """)
        
        # 设置拖放功能
        self.tool_list_widget.setDragEnabled(True)
        self.tool_list_widget.setAcceptDrops(True)
        self.tool_list_widget.setDropIndicatorShown(True)
        self.tool_list_widget.setDragDropMode(self.tool_list_widget.DragDropMode.InternalMove)
        
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

        # 创建管理器实例
        self.welcome_page_manager = WelcomePageManager(self)
        self.menu_manager = MenuManager(self)
        self.tool_manager = ToolManager(self)
        self.folder_manager = FolderManager(self)

        # 连接信号
        self.tool_list_widget.currentItemChanged.connect(self.tool_manager.on_tool_selected)
        self.tool_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tool_list_widget.customContextMenuRequested.connect(self.menu_manager.show_context_menu)

        # 初始化界面
        self.welcome_page_manager.add_home_button()
        self.welcome_page_manager.init_welcome_page()
        self.menu_manager.create_menus()


    def dragEnterEvent(self, event):
        """拖动进入事件"""
        # 只接受内部移动
        if event.source() == self.tool_list_widget:
            event.accept()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        """拖动移动事件"""
        # 允许文件夹之间的排序和工具到文件夹的拖动
        event.accept()
    
    def on_item_moved(self, item, old_parent, old_index, new_parent, new_index):
        """处理项目移动事件，保存文件夹排序顺序和插件关联"""
        # 从数据库模块导入Database类
        from src.db.database import Database
        
        item_data = item.data(0, Qt.ItemDataRole.UserRole)
        
        try:
            with Database() as db:
                # 如果移动的是插件，更新其文件夹关联
                if item_data and item_data.get('type') == 'tool':
                    tool_name = item_data.get('name')
                    if tool_name:
                        # 获取新父文件夹ID
                        new_folder_id = None
                        if new_parent and new_parent.data(0, Qt.ItemDataRole.UserRole).get('type') == 'folder':
                            new_folder_data = new_parent.data(0, Qt.ItemDataRole.UserRole)
                            new_folder_id = new_folder_data.get('folder_id')
                        
                        # 更新插件与文件夹的关联
                        db.plugin_association_manager.associate_plugin_with_folder(tool_name, new_folder_id)
                        # 更新插件文件夹映射
                        self.plugin_folder_map[tool_name] = new_folder_id
                
                # 更新所有文件夹的排序顺序
                self.folder_manager._save_folder_sort_order(db)
        except Exception as e:
            print(f"保存移动结果失败: {e}")
