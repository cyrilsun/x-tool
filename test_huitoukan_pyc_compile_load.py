import os
import sys
import py_compile
import importlib.util
from src.plugins.base_plugin import BasePlugin

# 测试文件路径
test_file = "/Users/sunxiaogang/study/pyproject/pyqt/x-tool/src/plugins/bak/huitoukan_plugin.py"
output_dir = "/Users/sunxiaogang/study/pyproject/pyqt/x-tool/plugins"
pyc_file = os.path.join(output_dir, "huitoukan_plugin.pyc")

print("测试步骤 1: 编译 huitoukan_plugin.py 为 .pyc 文件")
try:
    # 使用 py_compile 编译
    compiled_file = py_compile.compile(
        test_file,
        cfile=pyc_file,
        doraise=True
    )
    print(f"编译成功: {compiled_file}")
except Exception as e:
    print(f"编译失败: {e}")
    sys.exit(1)

print("\n测试步骤 2: 验证 .pyc 文件存在")
if os.path.exists(pyc_file):
    print(f".pyc 文件已创建: {pyc_file}")
    print(f"文件大小: {os.path.getsize(pyc_file)} 字节")
else:
    print(f".pyc 文件不存在: {pyc_file}")
    sys.exit(1)

print("\n测试步骤 3: 尝试加载 .pyc 文件")
try:
    # 添加 plugins 目录到 sys.path
    if output_dir not in sys.path:
        sys.path.insert(0, output_dir)
    
    # 加载 .pyc 文件
    module_name = "huitoukan_plugin"
    spec = importlib.util.spec_from_file_location(module_name, pyc_file)
    if spec is None:
        print(f"无法创建模块规范: {pyc_file}")
        sys.exit(1)
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    
    # 执行模块
    spec.loader.exec_module(module)
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
        print(f"插件类继承关系验证: {issubclass(plugin_class, BasePlugin)}")
        print(f"是否为BasePlugin本身: {plugin_class is BasePlugin}")
        print("插件类验证成功！")
    else:
        print("未找到有效的插件类")
        print("模块属性:")
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            print(f"  {attr_name}: {type(attr).__name__}")
        
except Exception as e:
    print(f"模块加载失败: {e}")
    import traceback
    traceback.print_exc()

print("\n测试步骤 4: 清理测试文件")
try:
    os.remove(pyc_file)
    print(f"测试文件已删除: {pyc_file}")
except Exception as e:
    print(f"删除测试文件失败: {e}")

print("\n测试完成！")
