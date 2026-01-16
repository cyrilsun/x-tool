import sys
import os

from PyQt6.QtWidgets import QApplication

from src.config.app_config import VERSION
from src.plugins.plugin_manager import load_plugins
from src.ui.main_window import MainWindow
from src.utils.logger import logger
from src.utils.translation_utils import setup_translation

if __name__ == "__main__":
    # 记录应用程序启动信息
    logger.info(f"X-Tool v{VERSION} 正在启动...")
    
    app = QApplication(sys.argv)
    
    # 设置翻译功能
    setup_translation(app)
    
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
