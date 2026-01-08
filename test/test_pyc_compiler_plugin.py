import sys
import os
import tempfile
import shutil

# 添加项目根目录到Python路径
sys.path.append('/')

from src.plugins.plugin_loader import PluginLoader, load_pyc_module

# 测试py_compile模块直接编译

def test_pyc_compilation():
    """测试py_compile模块的编译和加载功能"""
    print("开始测试py_compile模块功能...")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    print(f"创建临时目录: {temp_dir}")
    
    # 创建测试插件文件
    test_plugin_content = '''
from src.plugins.base_plugin import BasePlugin
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton


class TestPlugin(BasePlugin):
    def __init__(self):
        super().__init__("测试插件", "这是一个测试插件")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("这是一个测试插件")
        layout.addWidget(label)
        
        button = QPushButton("测试按钮")
        button.clicked.connect(self.on_button_clicked)
        layout.addWidget(button)

    def on_button_clicked(self):
        print("测试按钮被点击了！")

    def get_widget(self):
        return self

    def on_activate(self):
        print("测试插件被激活了！")

    def on_deactivate(self):
        print("测试插件被停用了！")
'''
    
    test_plugin_path = os.path.join(temp_dir, 'test_plugin_to_compile.py')
    with open(test_plugin_path, 'w') as f:
        f.write(test_plugin_content)
    
    print(f"创建测试插件文件: {test_plugin_path}")
    
    # 使用py_compile模块编译
    import py_compile
    print("使用py_compile模块编译测试插件...")
    
    try:
        pyc_file = py_compile.compile(
            test_plugin_path,
            cfile=os.path.join(temp_dir, 'test_plugin_to_compile.pyc'),
            doraise=True
        )
        print("✓ 编译成功")
        
        # 检查编译后的文件
        pyc_file_path = os.path.join(temp_dir, 'test_plugin_to_compile.pyc')
        if os.path.exists(pyc_file_path):
            print(f"✓ 找到编译后的pyc文件: {pyc_file_path}")
            
            # 测试加载编译后的插件
            print("测试加载编译后的pyc插件...")
            module_name = 'test_plugin_to_compile'
            
            try:
                module = load_pyc_module(module_name, pyc_file_path)
                if module:
                    print("✓ 成功加载pyc模块")
                    
                    # 检查是否有TestPlugin类
                    if hasattr(module, 'TestPlugin'):
                        print("✓ 找到了TestPlugin类")
                        
                        # 检查插件类是否正确
                        from src.plugins.base_plugin import BasePlugin
                        plugin_class = module.TestPlugin
                        if issubclass(plugin_class, BasePlugin):
                            print("✓ TestPlugin正确继承自BasePlugin")
                        else:
                            print("✗ TestPlugin没有正确继承自BasePlugin")
                    else:
                        print("✗ 找不到TestPlugin类")
                else:
                    print("✗ 无法加载pyc模块")
            except Exception as e:
                print(f"✗ 加载pyc模块时出错: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("✗ 找不到编译后的pyc文件")
    except Exception as e:
        print(f"✗ 编译过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)
        print(f"清理临时目录: {temp_dir}")


if __name__ == "__main__":
    print("测试py_compile模块和pyc插件加载")
    print("=" * 50)
    
    test_pyc_compilation()
    
    print("=" * 50)
    print("测试完成")
