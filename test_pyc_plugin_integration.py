import os
import sys
import importlib
import importlib.util
from PyQt6.QtWidgets import QApplication
from src.plugins.base_plugin import BasePlugin
from src.plugins.plugin_loader import PluginLoader, load_pyc_module

# 创建QApplication上下文
app = QApplication([])

# 源文件和输出目录
test_file = "/Users/sunxiaogang/study/pyproject/pyqt/x-tool/src/plugins/bak/huitoukan_plugin.py"
output_dir = "/Users/sunxiaogang/study/pyproject/pyqt/x-tool/plugins"
pyc_file = os.path.join(output_dir, "huitoukan_plugin.pyc")

print("集成测试 1: 使用 PycCompilerPlugin 代码进行编译")
try:
    # 模拟 PycCompilerPlugin 的编译逻辑
    import py_compile
    
    pyc_file = py_compile.compile(
        test_file,
        cfile=os.path.join(output_dir, os.path.basename(test_file) + "c"),
        doraise=True
    )
    print(f"编译成功: {pyc_file}")
except Exception as e:
    print(f"编译失败: {e}")
    sys.exit(1)

print("\n集成测试 2: 使用 PluginLoader 加载插件")
try:
    plugin_loader = PluginLoader()
    plugin_info = {
        "name": "huitoukan_plugin",
        "path": pyc_file,
        "type": "single_file"
    }
    
    print(f"尝试加载插件: {plugin_info}")
    plugin = plugin_loader.load_plugin(plugin_info)
    
    if plugin:
        print(f"插件加载成功！")
        print(f"插件名称: {plugin.name}")
        print(f"插件描述: {plugin.description}")
    else:
        print("插件加载失败")
        
except Exception as e:
    print(f"插件加载过程出错: {e}")
    import traceback
    traceback.print_exc()

print("\n集成测试 3: 直接使用 load_pyc_module 函数")
try:
    module_name = "huitoukan_plugin"
    module = load_pyc_module(module_name, pyc_file)
    print(f"模块加载成功: {module_name}")
    
    # 查找插件类
    plugin_class = None
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if (isinstance(attr, type) and 
            issubclass(attr, BasePlugin) and 
            attr is not BasePlugin):
            plugin_class = attr
            break
    
    if plugin_class:
        print(f"找到插件类: {plugin_class.__name__}")
        print("插件类验证成功！")
    else:
        print("未找到有效的插件类")
        print("模块属性:")
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            print(f"  {attr_name}: {type(attr).__name__}")
    
except Exception as e:
    print(f"load_pyc_module 失败: {e}")
    import traceback
    traceback.print_exc()

print("\n集成测试 4: 检查插件目录是否能被发现")
try:
    plugin_loader = PluginLoader()
    discovered_plugins = plugin_loader.discover_plugins()
    print(f"发现的插件: {[p['name'] for p in discovered_plugins]}")
    
    for plugin in discovered_plugins:
        if plugin['path'].endswith('.pyc'):
            print(f"Pyc插件: {plugin['name']} -> {plugin['path']}")
            # 尝试加载这个pyc插件
            loaded_plugin = plugin_loader.load_plugin(plugin)
            if loaded_plugin:
                print(f"  ✅ 加载成功: {loaded_plugin.name}")
            else:
                print(f"  ❌ 加载失败")

except Exception as e:
    print(f"发现插件过程出错: {e}")
    import traceback
    traceback.print_exc()

print("\n测试完成！")
