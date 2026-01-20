import sys
import os

# 导入路径工具
from src.utils.path_utils import get_app_root, get_lib_directory

# 1. 将项目根目录添加到 sys.path
root_dir = get_app_root()
# 如果是 .app 模式，root_dir 是 .app 路径，我们需要把 .app 内部的 Contents/Resources 
# 或者源代码目录加入 path。但对于 src 来说，我们已经在 main.py 所在的目录了。
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 2. 集中管理第三方库：将 lib 目录添加到 sys.path
lib_dir = get_lib_directory()
if lib_dir not in sys.path:
    sys.path.insert(0, lib_dir)

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
    
    # 设置应用程序信息（必须在设置翻译前）
    app.setApplicationName("X-Tool")
    app.setApplicationDisplayName("X-Tool")
    app.setDesktopFileName("com.xtool.app")
    app.setOrganizationName("X-Tool")
    app.setOrganizationDomain("com.xtool.app")
    
    # 设置翻译功能
    setup_translation(app)
    
    window = MainWindow()
    window.setWindowTitle(f"X-Tool v{VERSION}")
    
    # 设置窗口属性
    window.setObjectName("XToolMainWindow")
    
    # 在macOS上使用原生菜单系统
    if sys.platform == 'darwin':
        window.menuBar().setNativeMenuBar(True)

    load_plugins(window)

    # 默认选中首页
    # 获取首页项
    home_item = window.tool_list_widget.topLevelItem(0)  # 首页是第一个顶层项
    if home_item:
        window.tool_list_widget.setCurrentItem(home_item)

    window.show()

    sys.exit(app.exec())
