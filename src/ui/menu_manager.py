from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMenu

from src.plugins.plugin_manager import import_plugin, backup_plugins, restore_plugins
from src.utils.app_utils import show_about_dialog


class MenuManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def create_menus(self):
        """创建主菜单"""
        menubar = self.main_window.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件")

        # 新建子菜单
        new_menu = file_menu.addMenu("新建")
        
        # 新建文件夹
        new_folder_action = new_menu.addAction("文件夹")
        new_folder_action.triggered.connect(lambda: self.main_window.folder_manager._create_folder())

        # 分隔线
        file_menu.addSeparator()

        # 导入插件
        import_plugin_action = file_menu.addAction("导入插件")
        import_plugin_action.triggered.connect(lambda: import_plugin(self.main_window))

        # 备份插件
        backup_plugin_action = file_menu.addAction("备份插件")
        backup_plugin_action.triggered.connect(lambda: backup_plugins(self.main_window))

        # 恢复插件
        restore_plugin_action = file_menu.addAction("恢复插件")
        restore_plugin_action.triggered.connect(lambda: restore_plugins(self.main_window))

        # 帮助菜单
        help_menu = menubar.addMenu("帮助")

        # 关于
        about_action = help_menu.addAction("关于")
        about_action.triggered.connect(lambda: show_about_dialog(self.main_window))

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
