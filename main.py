import sys

from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox

from src.plugins.plugin_loader import get_plugin_directory
from src.ui.main_window import MainWindow
from src.plugins.plugin_manager import load_plugins, import_plugin, backup_plugins, restore_plugins
from src.utils.app_utils import show_about_dialog, check_update
from src.config.app_config import VERSION, APP_NAME





if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setApplicationName("X-Tool")
    app.setApplicationDisplayName("X-Tool")
    app.setDesktopFileName("com.xtool.app")
    
    window = MainWindow()
    window.setWindowTitle(f"X-Tool v{VERSION}")

    menubar = window.menuBar()
    
    # 添加文件菜单，位于帮助菜单之前
    file_menu = menubar.addMenu("文件")
    
    # 添加新建子菜单
    new_menu = file_menu.addMenu("新建")
    
    # 添加新建文件夹功能
    new_folder_action = new_menu.addAction("文件夹")
    new_folder_action.triggered.connect(lambda: window._create_folder())
    
    # 添加分隔符
    file_menu.addSeparator()
    
    # 添加导入插件功能
    import_plugin_action = file_menu.addAction("导入插件")
    import_plugin_action.triggered.connect(lambda: import_plugin(window))
    
    # 添加备份插件功能
    backup_plugin_action = file_menu.addAction("备份插件")
    backup_plugin_action.triggered.connect(lambda: backup_plugins(window))
    
    # 添加恢复插件功能
    restore_plugin_action = file_menu.addAction("恢复插件")
    restore_plugin_action.triggered.connect(lambda: restore_plugins(window))

    # 添加帮助菜单
    help_menu = menubar.addMenu("帮助")

    about_action = help_menu.addAction("关于")
    about_action.triggered.connect(lambda: show_about_dialog(window))

    load_plugins(window)

    # 默认选中首页
    # 获取首页项
    home_item = window.tool_list_widget.topLevelItem(0)  # 首页是第一个顶层项
    if home_item:
        window.tool_list_widget.setCurrentItem(home_item)

    window.show()

    sys.exit(app.exec())
