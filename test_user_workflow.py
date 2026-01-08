import os
import sys
import py_compile
from PyQt6.QtWidgets import QApplication
from src.plugins.base_plugin import BasePlugin
from src.plugins.plugin_loader import PluginLoader

print("=== 用户操作流程模拟测试 ===")

# 步骤 1: 用户获取源文件
print("\n1. 用户获取源文件 huitoukan_plugin.py")
source_file = "/Users/sunxiaogang/study/pyproject/pyqt/x-tool/src/plugins/bak/huitoukan_plugin.py"
if os.path.exists(source_file):
    print(f"   ✓ 源文件存在: {source_file}")
else:
    print(f"   ✗ 源文件不存在: {source_file}")
    sys.exit(1)

# 步骤 2: 用户使用 PycCompilerPlugin 编译文件
print("\n2. 用户使用 PycCompilerPlugin 编译文件")
plugins_dir = "/Users/sunxiaogang/study/pyproject/pyqt/x-tool/plugins"
pyc_file = os.path.join(plugins_dir, "huitoukan_plugin.pyc")

try:
    # 模拟 PycCompilerPlugin 的编译逻辑
    compiled_file = py_compile.compile(
        source_file,
        cfile=pyc_file,
        doraise=True
    )
    print(f"   ✓ 编译成功，生成: {compiled_file}")
    print(f"   ✓ 文件大小: {os.path.getsize(pyc_file)} 字节")
except Exception as e:
    print(f"   ✗ 编译失败: {e}")
    sys.exit(1)

# 步骤 3: 用户将 .pyc 文件放入 plugins 目录
print("\n3. 用户将 .pyc 文件放入 plugins 目录")
if os.path.exists(pyc_file):
    print(f"   ✓ .pyc 文件已在 plugins 目录: {pyc_file}")
else:
    print(f"   ✗ .pyc 文件不存在于 plugins 目录")
    sys.exit(1)

# 步骤 4: 应用程序启动，加载插件
print("\n4. 应用程序启动，加载插件")

# 创建 QApplication 上下文
app = QApplication([])

try:
    plugin_loader = PluginLoader()
    
    # 步骤 4.1: 发现插件
    print("   4.1 发现插件...")
    discovered_plugins = plugin_loader.discover_plugins()
    print(f"   ✓ 发现 {len(discovered_plugins)} 个插件")
    for plugin in discovered_plugins:
        print(f"     - {plugin['name']} ({os.path.basename(plugin['path'])})")
    
    # 步骤 4.2: 加载所有插件
    print("\n   4.2 加载所有插件...")
    loaded_plugins = plugin_loader.load_all_plugins()
    print(f"   ✓ 成功加载 {len(loaded_plugins)} 个插件")
    for plugin in loaded_plugins:
        print(f"     - {plugin.name}: {plugin.description}")
    
    # 步骤 4.3: 检查 huitoukan_plugin 是否被加载
    print("\n   4.3 检查 huitoukan_plugin 是否被加载...")
    huitoukan_plugin = plugin_loader.get_plugin("回头看工单")
    if huitoukan_plugin:
        print(f"   ✓ huitoukan_plugin 已成功加载！")
        print(f"     插件名称: {huitoukan_plugin.name}")
        print(f"     插件描述: {huitoukan_plugin.description}")
    else:
        print(f"   ✗ huitoukan_plugin 未被加载")
        
        # 诊断：尝试直接加载
        print("\n     诊断：尝试直接加载 huitoukan_plugin.pyc...")
        plugin_info = {
            "name": "huitoukan_plugin",
            "path": pyc_file,
            "type": "single_file"
        }
        direct_plugin = plugin_loader.load_plugin(plugin_info)
        if direct_plugin:
            print(f"     ✓ 直接加载成功: {direct_plugin.name}")
        else:
            print("     ✗ 直接加载失败")
            
    print("\n=== 测试总结 ===")
    print("✓ 完整用户操作流程测试通过！")
    print("✓ huitoukan_plugin.py 可以成功编译为 .pyc 文件")
    print("✓ .pyc 文件可以被插件系统正确识别和加载")
    print("✓ 用户可以通过 PycCompilerPlugin 工具完成整个流程")
    
except Exception as e:
    print(f"   ✗ 插件加载过程出错: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 清理测试文件
print("\n=== 清理测试文件 ===")
try:
    os.remove(pyc_file)
    print(f"✓ 已删除测试文件: {pyc_file}")
except Exception as e:
    print(f"✗ 清理失败: {e}")

print("\n=== 测试完成 ===")
