import os
import sys
import importlib
import importlib.util
import marshal
import types
from typing import List, Dict, Any, Optional
from src.plugins.base_plugin import BasePlugin
from src.utils.logger import logger


def load_pyc_module(module_name, module_path):
    """
    加载 .pyc 文件模块
    使用 importlib.util 来加载，这是Python官方推荐的方式
    """
    try:
        # 使用 importlib.util 加载 pyc 文件
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None:
            raise ValueError(f"无法创建模块规范: {module_path}")
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        
        # 执行模块
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        # 如果 importlib 加载失败，尝试使用传统的 marshal 方式
        with open(module_path, 'rb') as f:
            # 跳过 pyc 文件头
            # Python 3.7+ 的 pyc 文件头格式：
            # 4字节魔数 + 可变长度的时间戳和元数据 + 4字节大小 + 代码对象
            magic = f.read(4)
            if not magic:
                raise ValueError("无效的pyc文件：文件为空")
            
            # 处理 Python 3.7+ 的可变长度头部
            if sys.version_info >= (3, 7):
                while True:
                    byte = f.read(1)
                    if byte == b'\x0a':
                        break
                    if not byte:
                        raise ValueError("无效的pyc文件：格式错误")
                f.read(4)  # 跳过大小信息
            else:
                # 处理旧版本 Python 的固定长度头部
                f.read(4)  # 时间戳
                if sys.version_info >= (3, 3):
                    f.read(4)  # 大小
            
            # 加载代码对象
            code = marshal.load(f)
            
        module = types.ModuleType(module_name)
        module.__file__ = module_path
        module.__spec__ = importlib.machinery.ModuleSpec(module_name, None)
        exec(code, module.__dict__)
        return module


def get_plugin_directory() -> str:
    """获取插件目录路径，从.app同级目录查找"""
    plugin_dir = "plugins"

    if getattr(sys, 'frozen', False):
        executable_path = sys.executable
        exe_dir = os.path.dirname(executable_path)

        if sys.platform == 'darwin':
            # macOS .app bundle structure
            if executable_path.endswith('/Contents/MacOS/X-Tool'):
                # Get the directory containing the .app bundle
                app_bundle_path = os.path.dirname(os.path.dirname(os.path.dirname(executable_path)))
                app_parent_dir = os.path.dirname(app_bundle_path)
                sibling_plugins = os.path.join(app_parent_dir, "plugins")
                if os.path.exists(sibling_plugins):
                    return sibling_plugins
        else:
            # Windows and Linux
            sibling_plugins = os.path.join(exe_dir, "plugins")
            if os.path.exists(sibling_plugins):
                return sibling_plugins

    # Default to current directory plugins, but ensure it's absolute
    return os.path.abspath(plugin_dir)


class PluginLoader:
    def __init__(self, plugin_dir: str = None):
        self.plugin_dir = plugin_dir if plugin_dir is not None else get_plugin_directory()
        self.plugins: Dict[str, Any] = {}
        self.loaded_plugins: List[Any] = []

    def get_plugin_details(self, plugin_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取插件的详细信息，包括名称、描述等
        """
        try:
            plugin_name = plugin_info["name"]
            plugin_path = plugin_info["path"]

            plugins_dir = os.path.dirname(os.path.abspath(plugin_path))
            if plugins_dir not in sys.path:
                sys.path.insert(0, plugins_dir)

            module = None
            if plugin_path.endswith(".pyc"):
                # 加载 .pyc 文件
                try:
                    module = load_pyc_module(plugin_name, plugin_path)
                except Exception as pyc_error:
                    logger.error(f"加载 .pyc 插件 {plugin_name} 失败: {pyc_error}")
                    # 尝试使用对应的 .py 文件
                    py_file_path = plugin_path[:-1]  # 去掉 c 扩展名
                    if os.path.exists(py_file_path):
                        spec = importlib.util.spec_from_file_location(plugin_name, py_file_path)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
            else:
                # 加载 .py 文件
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

            if module:
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and
                        issubclass(attr, BasePlugin) and
                        attr is not BasePlugin):
                        plugin_instance = attr()
                        return {
                            "file_name": plugin_name,
                            "name": plugin_instance.name,
                            "description": plugin_instance.description,
                            "path": plugin_path,
                            "type": "single_file"
                        }
        except Exception as e:
            logger.error(f"获取插件 {plugin_info['name']} 详细信息失败: {e}")
        
        # 如果获取详细信息失败，返回基本信息
        return {
            "file_name": plugin_info["name"],
            "name": plugin_info["name"],
            "description": "",
            "path": plugin_info["path"],
            "type": plugin_info["type"]
        }

    def discover_plugins(self) -> List[Dict[str, Any]]:
        """
        发现所有插件并返回详细信息列表
        """
        plugins = []

        if not os.path.exists(self.plugin_dir):
            return plugins

        for item in os.listdir(self.plugin_dir):
            if item.startswith("__"):
                continue
            if item.endswith(".py"):
                plugin_name = item[:-3]
                plugin_path = os.path.join(self.plugin_dir, item)
                plugin_details = self.get_plugin_details({
                    "name": plugin_name,
                    "path": plugin_path,
                    "type": "single_file"
                })
                plugins.append(plugin_details)
            elif item.endswith(".pyc"):
                plugin_name = item[:-4]
                plugin_path = os.path.join(self.plugin_dir, item)
                plugin_details = self.get_plugin_details({
                    "name": plugin_name,
                    "path": plugin_path,
                    "type": "single_file"
                })
                plugins.append(plugin_details)

        return plugins

    def load_plugin(self, plugin_info: Dict[str, Any]) -> Optional[Any]:
        try:
            plugin_name = plugin_info["name"]
            plugin_path = plugin_info["path"]

            plugins_dir = os.path.dirname(os.path.abspath(plugin_path))
            if plugins_dir not in sys.path:
                sys.path.insert(0, plugins_dir)

            module = None
            if plugin_path.endswith(".pyc"):
                # 加载 .pyc 文件
                try:
                    module = load_pyc_module(plugin_name, plugin_path)
                except Exception as pyc_error:
                    logger.error(f"加载 .pyc 插件 {plugin_name} 失败: {pyc_error}")
                    logger.info(f"尝试使用 .py 文件替代...")
                    # 尝试使用对应的 .py 文件
                    py_file_path = plugin_path[:-1]  # 去掉 c 扩展名
                    if os.path.exists(py_file_path):
                        spec = importlib.util.spec_from_file_location(plugin_name, py_file_path)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
            else:
                # 加载 .py 文件
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

            if module:
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and
                        issubclass(attr, BasePlugin) and
                        attr is not BasePlugin):
                        plugin = attr()
                        self.plugins[plugin.name] = plugin
                        self.loaded_plugins.append(plugin)
                        
                        # 保存插件信息到数据库
                        from src.db.database import Database
                        with Database() as db:
                            db.plugin_manager.add_plugin(
                                name=plugin.name,
                                file_name=plugin_info["file_name"],
                                description=plugin.description
                            )
                        
                        return plugin

        except Exception as e:
            logger.error(f"加载插件 {plugin_name} 失败: {e}")
            return None
        return None

    def load_all_plugins(self) -> List[Any]:
        # 清空之前的插件列表，避免重复加载
        self.plugins.clear()
        self.loaded_plugins.clear()
        
        plugins = self.discover_plugins()
        for plugin_info in plugins:
            plugin = self.load_plugin(plugin_info)
        return self.loaded_plugins

    def get_plugin(self, name: str) -> Optional[Any]:
        return self.plugins.get(name)

    def get_all_plugins(self) -> List[Any]:
        return self.loaded_plugins
