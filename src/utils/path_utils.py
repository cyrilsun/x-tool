import os
import sys

def get_app_root() -> str:
    """获取应用根目录
    
    - 打包环境：返回 .app 所在的目录（不包含 .app 本身）
    - 源码运行：返回项目根目录
    """
    if getattr(sys, 'frozen', False):
        executable_path = sys.executable
        exe_dir = os.path.dirname(executable_path)

        if sys.platform == 'darwin':
            # macOS .app bundle structure: X-Tool.app/Contents/MacOS/X-Tool
            if '/Contents/MacOS/' in executable_path:
                # 返回 .app 所在的目录（不包含 .app）
                app_path = executable_path.split('/Contents/MacOS/')[0]
                return os.path.dirname(app_path)
        
        return exe_dir
    
    # 源码运行模式：假设当前文件在 src/utils/path_utils.py
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def get_data_directory() -> str:
    """获取数据存储目录"""
    root = get_app_root()
    # 打包环境下，root 已经是 .app 所在的目录
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
    # 打包环境下，root 已经是 .app 所在的目录
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
    # 打包环境下，root 已经是 .app 所在的目录
    plugin_dir = os.path.join(root, "plugins")
        
    # 自动创建目录，方便用户直接使用
    if not os.path.exists(plugin_dir):
        try:
            os.makedirs(plugin_dir, exist_ok=True)
            # 创建一个空的 __init__.py 确保目录被识别为包
            with open(os.path.join(plugin_dir, "__init__.py"), "w") as f:
                pass
        except:
            pass
    return os.path.abspath(plugin_dir)

def get_lib_directory() -> str:
    """获取第三方库(lib)目录"""
    root = get_app_root()
    # 打包环境下，root 已经是 .app 所在的目录
    lib_dir = os.path.join(root, "lib")
        
    # 自动创建目录
    if not os.path.exists(lib_dir):
        try:
            os.makedirs(lib_dir, exist_ok=True)
        except:
            pass
    return os.path.abspath(lib_dir)
