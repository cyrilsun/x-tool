import os
import sys
import importlib
from typing import List, Dict, Any, Optional
from src.plugins.base_plugin import BasePlugin


def get_plugin_directory() -> str:
    """获取插件目录路径，从.app同级目录查找"""
    plugin_dir = "plugins"

    if getattr(sys, 'frozen', False):
        executable_path = sys.executable
        exe_dir = os.path.dirname(executable_path)

        if sys.platform == 'darwin':
            if executable_path.endswith('/Contents/MacOS/X-Tool'):
                app_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(executable_path))))
                sibling_plugins = os.path.join(app_path, "plugins")
                if os.path.exists(sibling_plugins):
                    return sibling_plugins
        else:
            sibling_plugins = os.path.join(exe_dir, "plugins")
            if os.path.exists(sibling_plugins):
                return sibling_plugins

    return plugin_dir


class PluginLoader:
    def __init__(self, plugin_dir: str = None):
        self.plugin_dir = plugin_dir if plugin_dir is not None else get_plugin_directory()
        self.plugins: Dict[str, Any] = {}
        self.loaded_plugins: List[Any] = []

    def discover_plugins(self) -> List[Dict[str, Any]]:
        plugins = []

        if not os.path.exists(self.plugin_dir):
            return plugins

        for item in os.listdir(self.plugin_dir):
            plugin_path = os.path.join(self.plugin_dir, item)
            if item.endswith(".py") and not item.startswith("__"):
                plugin_name = item[:-3]
                plugins.append({
                    "name": plugin_name,
                    "path": plugin_path,
                    "type": "single_file"
                })

        return plugins

    def load_plugin(self, plugin_info: Dict[str, Any]) -> Optional[Any]:
        try:
            plugin_name = plugin_info["name"]
            plugin_path = plugin_info["path"]

            plugins_dir = os.path.dirname(os.path.abspath(plugin_path))
            if plugins_dir not in sys.path:
                sys.path.insert(0, plugins_dir)

            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, BasePlugin) and
                    attr is not BasePlugin):
                    plugin = attr()
                    self.plugins[plugin.name] = plugin
                    self.loaded_plugins.append(plugin)
                    return plugin

        except Exception:
            return None
        return None

    def load_all_plugins(self) -> List[Any]:
        plugins = self.discover_plugins()
        for plugin_info in plugins:
            plugin = self.load_plugin(plugin_info)
        return self.loaded_plugins

    def get_plugin(self, name: str) -> Optional[Any]:
        return self.plugins.get(name)

    def get_all_plugins(self) -> List[Any]:
        return self.loaded_plugins
