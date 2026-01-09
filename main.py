import sys

from PyQt6.QtWidgets import QApplication

from src.config.app_config import VERSION
from src.plugins.plugin_manager import load_plugins, import_plugin, backup_plugins, restore_plugins
from src.ui.main_window import MainWindow
from src.utils.app_utils import show_about_dialog

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setApplicationName("X-Tool")
    app.setApplicationDisplayName("X-Tool")
    app.setDesktopFileName("com.xtool.app")
    
    window = MainWindow()
    window.setWindowTitle(f"X-Tool v{VERSION}")

    load_plugins(window)

    # 默认选中首页
    # 获取首页项
    home_item = window.tool_list_widget.topLevelItem(0)  # 首页是第一个顶层项
    if home_item:
        window.tool_list_widget.setCurrentItem(home_item)

    window.show()

    sys.exit(app.exec())
