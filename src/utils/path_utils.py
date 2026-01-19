import os
import sys

def get_app_root() -> str:
    """获取应用根目录"""
    if getattr(sys, 'frozen', False):
        executable_path = sys.executable
        exe_dir = os.path.dirname(executable_path)

        if sys.platform == 'darwin':
            # macOS .app bundle structure: X-Tool.app/Contents/MacOS/X-Tool
            if executable_path.endswith('/Contents/MacOS/X-Tool'):
                # 返回 .app 所在的目录
                return os.path.dirname(os.path.dirname(os.path.dirname(executable_path)))
        
        return exe_dir
    
    # 源码运行模式：假设当前文件在 src/utils/path_utils.py
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def get_data_directory() -> str:
    """获取数据存储目录"""
    root = get_app_root()
    # 如果是 macOS .app，数据放在 .app 同级
    if root.endswith('.app'):
        data_dir = os.path.join(os.path.dirname(root), "data")
    else:
        data_dir = os.path.join(root, "data")
    
    if not os.path.exists(data_dir):
        try:
            os.makedirs(data_dir, exist_ok=True)
        except:
            pass
    return data_dir

def get_log_directory() -> str:
    """获取日志存储目录"""
    root = get_app_root()
    if root.endswith('.app'):
        log_dir = os.path.join(os.path.dirname(root), "log")
    else:
        log_dir = os.path.join(root, "log")
        
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
        except:
            pass
    return log_dir

def get_plugin_directory() -> str:
    """获取插件存储目录"""
    root = get_app_root()
    # 如果是 macOS .app，root 就是包含 .app 的目录（因为 get_app_root 做了处理）
    # 但要注意 get_app_root 对于 macOS 返回的是 os.path.dirname(app_bundle_path)
    # 所以直接 join 即可
    if root.endswith('.app'):
        plugin_dir = os.path.join(os.path.dirname(root), "plugins")
    else:
        plugin_dir = os.path.join(root, "plugins")
        
    if not os.path.exists(plugin_dir):
        try:
            os.makedirs(plugin_dir, exist_ok=True)
        except:
            pass
    return os.path.abspath(plugin_dir)
