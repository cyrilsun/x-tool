import sys
import os
import py_compile

# 添加项目根目录到Python路径
sys.path.append('/')

print("测试Pyc插件加载功能")
print("=" * 50)

# 源文件路径
source_file = '/test/test_plugin.py'
# 目标pyc文件路径
target_pyc = '/Users/sunxiaogang/study/pyproject/pyqt/x-tool/plugins/test_plugin.pyc'

print(f"编译源文件: {source_file}")
print(f"到目标文件: {target_pyc}")

# 编译为pyc文件
try:
    py_compile.compile(source_file, cfile=target_pyc)
    print("✓ 编译成功")
    
    # 删除原有的.py文件
    os.remove('/Users/sunxiaogang/study/pyproject/pyqt/x-tool/plugins/test_plugin.py')
    print("✓ 已删除原有的.py文件")
    
    print("\n现在运行主程序，测试是否能加载pyc插件...")
    print("按Ctrl+C退出主程序")
    print("=" * 50)
    
    # 运行主程序
    import subprocess
    subprocess.run(['python', 'main.py'], cwd='/Users/sunxiaogang/study/pyproject/pyqt/x-tool')
    
except Exception as e:
    print(f"✗ 编译失败: {e}")

print("=" * 50)
print("测试完成")
