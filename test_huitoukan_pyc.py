import sys
import os
import py_compile

# 添加项目根目录到Python路径
sys.path.append('/Users/sunxiaogang/study/pyproject/pyqt/x-tool')

from src.plugins.plugin_loader import PluginLoader, load_pyc_module


def test_huitoukan_pyc():
    """测试huitoukan_plugin.pyc文件的加载"""
    print("开始测试huitoukan_plugin.pyc加载功能...")
    
    # 首先直接编译源文件
    py_path = os.path.join(os.path.dirname(__file__), 'src', 'plugins', 'bak', 'huitoukan_plugin.py')
    pyc_path = os.path.join(os.path.dirname(__file__), 'plugins', 'huitoukan_plugin.pyc')
    
    if not os.path.exists(py_path):
        print(f"错误: 找不到源文件 {py_path}")
        return
    
    print(f"找到源文件: {py_path}")
    
    # 编译源文件
    print(f"编译到: {pyc_path}")
    try:
        py_compile.compile(py_path, cfile=pyc_path, doraise=True)
        print("✓ 编译成功")
    except Exception as e:
        print(f"✗ 编译失败: {e}")
        return
    
    if not os.path.exists(pyc_path):
        print(f"错误: 编译后找不到文件 {pyc_path}")
        return
    
    print(f"找到pyc文件: {pyc_path}")
    
    try:
        # 直接测试load_pyc_module函数
        module_name = 'huitoukan_plugin'
        print(f"尝试加载模块: {module_name}")
        
        module = load_pyc_module(module_name, pyc_path)
        
        if module:
            print("✓ Pyc模块加载成功")
            
            # 检查模块内容
            print(f"模块属性: {dir(module)}")
            
            # 检查是否有HuitoukanPlugin类
            if hasattr(module, 'HuitoukanPlugin'):
                print("✓ 找到了HuitoukanPlugin类")
                
                # 尝试创建实例（注意：这可能会失败，因为它依赖于PyQt6和BasePlugin）
                try:
                    from src.plugins.base_plugin import BasePlugin
                    plugin_class = module.HuitoukanPlugin
                    print(f"插件类继承关系: {plugin_class.__mro__}")
                    print(f"插件类名称: {plugin_class.__name__}")
                    print("✓ 插件类检查通过")
                except Exception as e:
                    print(f"⚠️  无法创建插件实例（可能需要完整的运行环境）: {e}")
            else:
                print("✗ 找不到HuitoukanPlugin类")
        else:
            print("✗ Pyc模块加载失败")
            
    except Exception as e:
        print(f"✗ 加载pyc模块时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("测试huitoukan_plugin.pyc加载")
    print("=" * 50)
    
    test_huitoukan_pyc()
    
    print("=" * 50)
    print("测试完成")
