import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu

from src.plugins.plugin_manager import import_plugin, backup_plugins, restore_plugins
from src.utils.app_utils import show_about_dialog


class MenuManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self._init_menus()

    def _init_menus(self):
        """初始化菜单结构，只执行一次"""
        menubar = self.main_window.menuBar()
        
        # 清除现有的所有菜单
        menubar.clear()

        # 创建并保存文件菜单引用
        self.file_menu = menubar.addMenu("文件")

        # 创建并保存新建子菜单引用
        self.new_menu = self.file_menu.addMenu("新建")

        # 创建并保存新建文件夹菜单项引用
        self.new_folder_action = QAction("文件夹", self.main_window)
        self.new_folder_action.triggered.connect(lambda: self.main_window.folder_manager._create_folder())
        self.new_menu.addAction(self.new_folder_action)

        # 添加分隔线
        self.file_menu.addSeparator()

        # 创建并保存导入插件菜单项引用
        self.import_plugin_action = QAction("导入插件", self.main_window)
        self.import_plugin_action.triggered.connect(lambda: import_plugin(self.main_window))
        self.file_menu.addAction(self.import_plugin_action)

        # 创建并保存备份插件菜单项引用
        self.backup_plugin_action = QAction("备份插件", self.main_window)
        self.backup_plugin_action.triggered.connect(lambda: backup_plugins(self.main_window))
        self.file_menu.addAction(self.backup_plugin_action)

        # 创建并保存恢复插件菜单项引用
        self.restore_plugin_action = QAction("恢复插件", self.main_window)
        self.restore_plugin_action.triggered.connect(lambda: restore_plugins(self.main_window))
        self.file_menu.addAction(self.restore_plugin_action)

        # 添加分隔线
        self.file_menu.addSeparator()

        # 创建并保存退出菜单项引用
        self.quit_action = QAction("退出X-Tool", self.main_window)
        self.quit_action.triggered.connect(self.main_window.close)
        self.file_menu.addAction(self.quit_action)

        # 创建并保存帮助菜单引用
        self.help_menu = menubar.addMenu("帮助")

        # 创建并保存关于菜单项引用
        self.about_action = QAction("关于", self.main_window)
        self.about_action.triggered.connect(lambda: show_about_dialog(self.main_window))
        self.help_menu.addAction(self.about_action)

    def create_menus(self):
        """创建/更新菜单显示"""
        # 不再重建菜单结构，只确保菜单可见
        self.file_menu.menuAction().setVisible(True)
        self.help_menu.menuAction().setVisible(True)
        
        # 确保所有菜单项可见
        for action in self.file_menu.actions():
            action.setVisible(True)
        for action in self.help_menu.actions():
            action.setVisible(True)
        for action in self.new_menu.actions():
            action.setVisible(True)
    
    def update_translations(self):
        """更新菜单翻译文本"""
        # 更新菜单标题
        self.file_menu.setTitle("文件")
        self.new_menu.setTitle("新建")
        self.help_menu.setTitle("帮助")
        
        # 更新菜单项文本
        self.new_folder_action.setText("文件夹")
        self.import_plugin_action.setText("导入插件")
        self.backup_plugin_action.setText("备份插件")
        self.restore_plugin_action.setText("恢复插件")
        self.quit_action.setText("退出X-Tool")
        self.about_action.setText("关于")

    def show_context_menu(self, position):
        """显示上下文菜单"""
        # 获取鼠标位置的项目
        item = self.main_window.tool_list_widget.itemAt(position)

        if not item:
            # 如果没有项目（点击空白区域）
            self._show_empty_area_context_menu(position)
        else:
            # 获取项目数据
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            if item_data:
                item_type = item_data.get("type")
                if item_type == "folder":
                    # 显示文件夹上下文菜单
                    self._show_folder_context_menu(position, item)
                elif item_type == "tool":
                    # 显示工具上下文菜单
                    self._show_tool_context_menu(position, item)

    def _show_empty_area_context_menu(self, position):
        """显示空白区域的上下文菜单"""
        menu = QMenu()

        # 创建文件夹
        create_folder_action = menu.addAction("创建文件夹")
        create_folder_action.triggered.connect(lambda: self.main_window.folder_manager._create_folder())

        menu.exec(self.main_window.tool_list_widget.mapToGlobal(position))

    def _show_folder_context_menu(self, position, folder_item):
        """显示文件夹的上下文菜单"""
        menu = QMenu()

        # 创建文件夹
        create_folder_action = menu.addAction("创建文件夹")
        create_folder_action.triggered.connect(lambda: self.main_window.folder_manager._create_folder(folder_item))

        # 编辑名称
        edit_folder_action = menu.addAction("编辑名称")
        edit_folder_action.triggered.connect(lambda: self.main_window.folder_manager._edit_folder_name(folder_item))

        # 删除文件夹
        delete_folder_action = menu.addAction("删除文件夹")
        delete_folder_action.triggered.connect(lambda: self.main_window.folder_manager._delete_folder(folder_item))

        menu.addSeparator()

        # 导入插件到文件夹
        import_plugin_action = menu.addAction("导入插件")
        import_plugin_action.triggered.connect(lambda: self.main_window.tool_manager.import_plugin_to_folder(folder_item))

        menu.exec(self.main_window.tool_list_widget.mapToGlobal(position))

    def _show_tool_context_menu(self, position, tool_item):
        """显示工具的上下文菜单"""
        menu = QMenu()

        # 删除插件
        delete_plugin_action = menu.addAction("删除插件")
        delete_plugin_action.triggered.connect(lambda: self.main_window.tool_manager.delete_plugin(tool_item))

        menu.exec(self.main_window.tool_list_widget.mapToGlobal(position))
    
    def _open_plugin_market(self):
        """打开插件市场窗口"""
        from src.plugins.plugin_market_window import PluginMarketWindow
        self.plugin_market_window = PluginMarketWindow(self.main_window)
        self.plugin_market_window.show()
