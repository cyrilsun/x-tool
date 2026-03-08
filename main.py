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

# 调试信息：打印关键路径（便于排查打包环境问题）
if getattr(sys, 'frozen', False):
    print(f"[DEBUG] Running in packaged mode")
    print(f"[DEBUG] sys.executable: {sys.executable}")
    print(f"[DEBUG] root_dir: {root_dir}")
    print(f"[DEBUG] lib_dir: {lib_dir}")
    print(f"[DEBUG] lib_dir exists: {os.path.exists(lib_dir)}")
    print(f"[DEBUG] lib_dir in sys.path: {lib_dir in sys.path}")
    if os.path.exists(lib_dir):
        print(f"[DEBUG] lib_dir contents: {os.listdir(lib_dir)[:5]}...")  # 只显示前5个

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
    app.setDesktopFileName("com.bitouyun.app")
    app.setOrganizationName("X-Tool")
    app.setOrganizationDomain("com.bitouyun.app")
    
    # 设置翻译功能
    setup_translation(app)

    # 设置应用程序图标（支持 Windows/macOS/Linux）
    icon_path = None
    if getattr(sys, 'frozen', False):
        # 打包后的环境，查找图标文件
        if sys.platform == 'win32':
            icon_path = os.path.join(root_dir, 'icon.ico')
        elif sys.platform == 'darwin':
            icon_path = os.path.join(root_dir, 'icon.icns')
        else:
            icon_path = os.path.join(root_dir, 'icon.png')
    else:
        # 开发环境
        if sys.platform == 'win32':
            icon_path = os.path.join(current_dir, 'icon.ico')
        elif sys.platform == 'darwin':
            icon_path = os.path.join(current_dir, 'icon.icns')
        else:
            icon_path = os.path.join(current_dir, 'icon.png')

    if icon_path and os.path.exists(icon_path):
        from PyQt6.QtGui import QIcon
        app.setWindowIcon(QIcon(icon_path))

    try:
        window = MainWindow()
        window.setWindowTitle(f"X-Tool v{VERSION}")
        
        # 设置窗口属性
        window.setObjectName("XToolMainWindow")
        
        # 在macOS上使用原生菜单系统
        if sys.platform == 'darwin':
            window.menuBar().setNativeMenuBar(True)

        logger.info("[main] 开始加载插件...")
        load_plugins(window)
        logger.info("[main] 插件加载完成")

        # 插件加载完成后，刷新首页插件列表
        logger.info("[main] 开始刷新首页...")
        if hasattr(window.welcome_page_manager, 'home_page') and window.welcome_page_manager.home_page:
            window.welcome_page_manager.home_page.refresh_plugins()
        logger.info("[main] 首页刷新完成")

        # 默认选中首页
        # 获取首页项
        home_item = window.tool_list_widget.topLevelItem(0)  # 首页是第一个顶层项
        if home_item:
            window.tool_list_widget.setCurrentItem(home_item)

        logger.info("[main] 显示主窗口...")
        window.show()
        logger.info("[main] 主窗口已显示")

        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"[main] 程序启动失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise
