import traceback

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, \
    QStackedWidget

from src.ui.collapsible_sidebar import CollapsibleSidebar
from src.ui.folder_manager import FolderManager
from src.ui.menu_manager import MenuManager
from src.ui.tool_manager import ToolManager
from src.ui.welcome_page import WelcomePageManager
from src.utils.logger import logger


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
                background-color: #f5f6fa;
            }
            QMainWindow::separator {
                background-color: #dcdde1;
                width: 1px;
            }
            QMenuBar {
                background-color: #ffffff;
                border-bottom: 1px solid #dcdde1;
                padding: 5px 10px;
                font-family: "Segoe UI", "Microsoft YaHei";
                font-size: 14px;
                color: #2f3640;
            }
            QMenuBar::item {
                background: transparent;
                padding: 4px 10px;
                margin-right: 5px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #f1f2f6;
                color: #3498db;
            }
            QMenu {
                background-color: #ffffff;
                border: 1px solid #dcdde1;
                padding: 5px;
                border-radius: 6px;
            }
            QMenu::item {
                padding: 8px 25px 8px 20px;
                border-radius: 4px;
                margin: 2px;
                font-size: 13px;
                color: #2f3640;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background: #f1f2f6;
                margin: 5px 10px;
            }
            QSplitter::handle {
                background-color: #dcdde1;
            }
            QSplitter::handle:horizontal {
                width: 1px;
            }
            QMessageBox {
                background-color: #ffffff;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 13px;
            }
        """)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建水平布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建可折叠侧边栏
        self.sidebar = CollapsibleSidebar(self)
        main_layout.addWidget(self.sidebar)

        # 获取侧边栏中的控件引用
        self.tool_list_widget = self.sidebar.get_tree_widget()
        self.search_input = self.sidebar.get_search_input()

        # 创建右侧工具使用界面容器
        self.tool_stack_widget = QStackedWidget()
        self.tool_stack_widget.setStyleSheet("""
            QStackedWidget {
                background-color: #f5f6fa;
                border: none;
            }
        """)
        main_layout.addWidget(self.tool_stack_widget, 1)  # 添加 stretch factor

        # 创建管理器实例
        self.welcome_page_manager = WelcomePageManager(self)
        self.menu_manager = MenuManager(self)
        self.tool_manager = ToolManager(self)
        self.folder_manager = FolderManager(self)

        # 连接信号
        self.tool_list_widget.currentItemChanged.connect(self.tool_manager.on_tool_selected)
        self.tool_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tool_list_widget.customContextMenuRequested.connect(self.menu_manager.show_context_menu)
        self.tool_list_widget.itemExpanded.connect(self.on_item_expanded)
        self.search_input.textChanged.connect(self.filter_plugins)
        
        # 连接文件夹变化信号到首页刷新
        self.folder_manager.folders_changed.connect(self.on_folders_changed)

        # 初始化界面
        self.welcome_page_manager.add_home_button()
        self.welcome_page_manager.init_welcome_page()
        self.menu_manager.create_menus()


    def on_sidebar_toggled(self, is_expanded):
        """侧边栏收起/展开时的回调"""
        # 可以在这里添加额外的布局调整逻辑
        pass
        
    def on_folders_changed(self):
        """文件夹结构变化时的回调 - 刷新首页分类"""
        # 通知首页刷新分类
        if (hasattr(self.welcome_page_manager, 'home_page') and 
            self.welcome_page_manager.home_page):
            self.welcome_page_manager.home_page.load_categories_from_sidebar()
        
    def on_item_expanded(self, expanded_item):
        """当文件夹展开时，收起其它所有文件夹（手风琴模式）"""
        # 如果正在搜索，不执行手风琴模式，允许展开多个搜索结果
        if self.search_input.text().strip():
            return
            
        self.tool_list_widget.blockSignals(True)
        
        # 获取展开项的所有祖先，祖先不能收起
        ancestors = []
        curr = expanded_item.parent()
        while curr:
            ancestors.append(curr)
            curr = curr.parent()
            
        def traverse_and_collapse(parent_item=None):
            if parent_item is None:
                # 遍历顶层项
                for i in range(self.tool_list_widget.topLevelItemCount()):
                    item = self.tool_list_widget.topLevelItem(i)
                    if item.childCount() > 0:  # 只处理文件夹
                        if item != expanded_item and item not in ancestors:
                            item.setExpanded(False)
                        traverse_and_collapse(item)
            else:
                # 遍历子项
                for i in range(parent_item.childCount()):
                    item = parent_item.child(i)
                    if item.childCount() > 0:  # 只处理文件夹
                        if item != expanded_item and item not in ancestors:
                            item.setExpanded(False)
                        traverse_and_collapse(item)

        try:
            traverse_and_collapse()
        finally:
            self.tool_list_widget.blockSignals(False)

    def filter_plugins(self, text):
        """模糊搜索过滤插件"""
        search_text = text.strip().lower()
        
        # 递归遍历所有项
        for i in range(self.tool_list_widget.topLevelItemCount()):
            item = self.tool_list_widget.topLevelItem(i)
            self._filter_item(item, search_text)

    def _filter_item(self, item, search_text):
        """递归过滤单个项目"""
        item_visible = False
        item_text = item.text(0).lower()
        
        # 首页始终显示
        item_data = item.data(0, Qt.ItemDataRole.UserRole)
        if item_data and item_data.get("type") == "home":
            item.setHidden(False)
            return True

        # 检查当前项是否匹配
        if search_text in item_text:
            item_visible = True
            
        # 递归检查子项
        child_match = False
        for i in range(item.childCount()):
            if self._filter_item(item.child(i), search_text):
                child_match = True
        
        # 如果当前项匹配，或其子项有匹配，则显示
        final_visible = item_visible or child_match
        item.setHidden(not final_visible)
        
        # 如果搜索中且有匹配，展开文件夹
        if search_text and final_visible and item.childCount() > 0:
            item.setExpanded(True)
        elif not search_text and item.childCount() > 0:
            # 搜索清空时，不强制展开
            pass
            
        return final_visible


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
        
        # 调试日志
        logger.info(f"[on_item_moved] 被调用: item_data={item_data}, new_parent={new_parent}")
        if new_parent:
            new_parent_data = new_parent.data(0, Qt.ItemDataRole.UserRole)
            logger.info(f"[on_item_moved] new_parent_data={new_parent_data}")
        
        try:
            with Database() as db:
                # 如果移动的是插件，更新其文件夹关联
                if item_data and item_data.get('type') == 'tool':
                    tool_name = item_data.get('name')
                    if tool_name:
                        # 获取新父文件夹ID
                        new_folder_id = None
                        if new_parent:
                            new_parent_data = new_parent.data(0, Qt.ItemDataRole.UserRole)
                            if new_parent_data and new_parent_data.get('type') == 'folder':
                                new_folder_id = new_parent_data.get('folder_id')
                        
                        logger.info(f"[on_item_moved] 准备保存: tool_name={tool_name}, new_folder_id={new_folder_id}")
                        
                        # 更新插件与文件夹的关联
                        db.plugin_association_manager.associate_plugin_with_folder(tool_name, new_folder_id)
                        # 更新插件文件夹映射
                        self.plugin_folder_map[tool_name] = new_folder_id
                        logger.info(f"[on_item_moved] 插件 '{tool_name}' 已移动到文件夹 ID: {new_folder_id}")
                
                # 更新所有文件夹的排序顺序
                self.folder_manager.save_folder_sort_order(db)
                logger.info(f"[on_item_moved] 文件夹排序顺序已保存")
        except Exception as e:
            logger.error(f"[on_item_moved] 保存移动结果失败: {e}")
            logger.error(traceback.format_exc())
