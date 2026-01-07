import os
import sys
import importlib
from typing import List, Dict, Any, Optional

DEBUG_LOG = os.path.expanduser("~/Library/Logs/X-Tool.log")


def log_debug(msg: str):
    try:
        with open(DEBUG_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{os.path.basename(sys.executable)}] {msg}\n")
    except Exception:
        pass


def get_plugin_directory() -> str:
    """获取插件目录路径，从.app同级目录查找"""
    plugin_dir = "plugins"

    log_debug(f"get_plugin_directory: START")
    log_debug(f"get_plugin_directory: sys.frozen={getattr(sys, 'frozen', False)}")
    log_debug(f"get_plugin_directory: sys.executable={sys.executable}")
    log_debug(f"get_plugin_directory: sys.platform={sys.platform}")

    if getattr(sys, 'frozen', False):
        executable_path = sys.executable
        exe_dir = os.path.dirname(executable_path)

        log_debug(f"get_plugin_directory: executable={executable_path}")
        log_debug(f"get_plugin_directory: exe_dir={exe_dir}")

        if sys.platform == 'darwin':
            log_debug(f"get_plugin_directory: darwin platform, path ends check: {executable_path.endswith('/Contents/MacOS/X-Tool')}")
            if executable_path.endswith('/Contents/MacOS/X-Tool'):
                app_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(executable_path))))
                sibling_plugins = os.path.join(app_path, "plugins")
                log_debug(f"get_plugin_directory: app_path={app_path}")
                log_debug(f"get_plugin_directory: sibling_plugins={sibling_plugins}")
                log_debug(f"get_plugin_directory: exists={os.path.exists(sibling_plugins)}")
                if os.path.exists(sibling_plugins):
                    return sibling_plugins
        else:
            sibling_plugins = os.path.join(exe_dir, "plugins")
            log_debug(f"get_plugin_directory: sibling_plugins={sibling_plugins}")
            log_debug(f"get_plugin_directory: exists={os.path.exists(sibling_plugins)}")
            if os.path.exists(sibling_plugins):
                return sibling_plugins

    log_debug(f"get_plugin_directory: END, returning {plugin_dir}")
    return plugin_dir


class PluginLoader:
    def __init__(self, plugin_dir: str = None):
        self.plugin_dir = plugin_dir if plugin_dir is not None else get_plugin_directory()
        log_debug(f"PluginLoader.__init__: plugin_dir={self.plugin_dir}")
        self.plugins: Dict[str, Any] = {}
        self.loaded_plugins: List[Any] = []

    def discover_plugins(self) -> List[Dict[str, Any]]:
        plugins = []

        log_debug(f"discover_plugins: self.plugin_dir={self.plugin_dir}")
        log_debug(f"discover_plugins: exists={os.path.exists(self.plugin_dir)}")

        if not os.path.exists(self.plugin_dir):
            return plugins

        for item in os.listdir(self.plugin_dir):
            plugin_path = os.path.join(self.plugin_dir, item)
            if item.endswith(".py") and not item.startswith("__"):
                plugin_name = item[:-3]
                log_debug(f"discover_plugins: found {plugin_name}")
                plugins.append({
                    "name": plugin_name,
                    "path": plugin_path,
                    "type": "single_file"
                })

        log_debug(f"discover_plugins: total={len(plugins)}")
        return plugins

    def load_plugin(self, plugin_info: Dict[str, Any]) -> Optional[Any]:
        try:
            plugin_name = plugin_info["name"]
            plugin_path = plugin_info["path"]
            log_debug(f"load_plugin: {plugin_name}, path={plugin_path}")

            plugins_dir = os.path.dirname(os.path.abspath(plugin_path))
            if plugins_dir not in sys.path:
                sys.path.insert(0, plugins_dir)
                log_debug(f"load_plugin: added to sys.path: {plugins_dir}")

            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    attr.__name__ == "WorkOrderPlugin" and
                    hasattr(attr, 'name') and
                    hasattr(attr, 'get_widget')):
                    plugin = attr()
                    self.plugins[plugin.name] = plugin
                    self.loaded_plugins.append(plugin)
                    log_debug(f"load_plugin: success {plugin.name}")
                    return plugin

        except Exception as e:
            log_debug(f"load_plugin: failed {plugin_info['name']}: {e}")
            import traceback
            log_debug(traceback.format_exc())
            return None
        return None

    def load_all_plugins(self) -> List[Any]:
        plugins = self.discover_plugins()
        for plugin_info in plugins:
            plugin = self.load_plugin(plugin_info)
            if plugin:
                log_debug(f"已加载插件: {plugin.name}")
        return self.loaded_plugins

    def get_plugin(self, name: str) -> Optional[Any]:
        return self.plugins.get(name)

    def get_all_plugins(self) -> List[Any]:
        return self.loaded_plugins
