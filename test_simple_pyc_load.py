import sys
import os
import py_compile
import importlib.util

# 添加项目根目录到Python路径
sys.path.append('/Users/sunxiaogang/study/pyproject/pyqt/x-tool')


def test_simple_pyc_load():
    """使用Python内置的importlib来测试pyc文件加载"""
    print("开始测试pyc文件加载功能...")
    
    # 测试文件路径
    test_files = [
        # 简单的测试文件
        os.path.join(os.path.dirname(__file__), 'test_plugin.py'),
        # 复杂的huitoukan文件
        os.path.join(os.path.dirname(__file__), 'src', 'plugins', 'bak', 'huitoukan_plugin.py')
    ]
    
    for py_path in test_files:
        if not os.path.exists(py_path):
            print(f"错误: 找不到源文件 {py_path}")
            continue
        
        print(f"\n=== 测试文件: {os.path.basename(py_path)} ===")
        
        # 编译源文件
        pyc_path = py_path + 'c'
        print(f"编译到: {pyc_path}")
        
        try:
            py_compile.compile(py_path, cfile=pyc_path, doraise=True)
            print("✓ 编译成功")
        except Exception as e:
            print(f"✗ 编译失败: {e}")
            continue
        
        if not os.path.exists(pyc_path):
            print(f"错误: 编译后找不到文件 {pyc_path}")
            continue
        
        # 尝试使用importlib加载
        print("尝试使用importlib加载pyc文件...")
        module_name = os.path.splitext(os.path.basename(pyc_path))[0]
        
        try:
            # 使用importlib.util.spec_from_file_location加载
            spec = importlib.util.spec_from_file_location(module_name, pyc_path)
            if spec is None:
                print(f"✗ 无法创建模块规范")
                continue
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            
            # 执行模块
            spec.loader.exec_module(module)
            print(f"✓ 使用importlib加载成功")
            
            # 检查模块内容
            print(f"模块属性: {[attr for attr in dir(module) if not attr.startswith('_')]}")
            
        except Exception as e:
            print(f"✗ 使用importlib加载失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 清理
        if os.path.exists(pyc_path):
            os.remove(pyc_path)


if __name__ == "__main__":
    print("测试pyc文件加载")
    print("=" * 50)
    
    test_simple_pyc_load()
    
    print("=" * 50)
    print("测试完成")
