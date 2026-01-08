import sys
import os
import py_compile
import tempfile
from PyQt6.QtWidgets import QApplication

# 添加项目根目录到Python路径
sys.path.append('/Users/sunxiaogang/study/pyproject/pyqt/x-tool')

from src.plugins.plugin_loader import PluginLoader, get_plugin_directory


def test_pyc_compilation():
    """测试Python文件到Pyc文件的编译功能"""
    print("开始测试Pyc编译功能...")
    
    # 创建临时测试文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('''
# 简单的测试类，不继承自QWidget
class TestPlugin:
    def __init__(self):
        self.name = "Test Plugin"
        self.description = "This is a test plugin"
''')
        test_py_file = f.name
    
    try:
        print(f"创建测试文件: {test_py_file}")
        
        # 编译为pyc文件
        pyc_file = test_py_file + 'c'
        print(f"编译到: {pyc_file}")
        py_compile.compile(test_py_file, cfile=pyc_file)
        
        # 检查pyc文件是否存在
        if os.path.exists(pyc_file):
            print("✓ Pyc文件编译成功")
            
            # 测试插件加载器能否加载pyc文件
            print("测试插件加载器加载pyc文件...")
            
            # 创建临时plugins目录并复制pyc文件
            temp_plugins_dir = tempfile.mkdtemp()
            try:
                temp_pyc_file = os.path.join(temp_plugins_dir, os.path.basename(pyc_file))
                import shutil
                shutil.copy(pyc_file, temp_pyc_file)
                
                # 直接测试load_pyc_module函数
                from src.plugins.plugin_loader import load_pyc_module
                module_name = os.path.splitext(os.path.basename(temp_pyc_file))[0]
                try:
                    module = load_pyc_module(module_name, temp_pyc_file)
                    if module and hasattr(module, 'TestPlugin'):
                        print("✓ Pyc模块加载成功")
                        # 创建类实例
                        test_instance = module.TestPlugin()
                        if test_instance:
                            print(f"✓ 成功创建TestPlugin实例: {test_instance.name}")
                    else:
                        print("✗ Pyc模块加载失败或缺少TestPlugin类")
                except Exception as e:
                    print(f"✗ 加载pyc模块时出错: {e}")
            finally:
                # 清理临时plugins目录
                shutil.rmtree(temp_plugins_dir)
        else:
            print("✗ Pyc文件编译失败")
    finally:
        # 清理测试文件
        if os.path.exists(test_py_file):
            os.remove(test_py_file)
        if os.path.exists(pyc_file):
            os.remove(pyc_file)


if __name__ == "__main__":
    print("测试Pyc编译器插件")
    print("=" * 50)
    
    test_pyc_compilation()
    
    print("=" * 50)
    print("测试完成")
