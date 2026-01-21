#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import shutil

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="X-Tool多平台构建脚本")
    parser.add_argument(
        "--platform", 
        choices=["windows", "macos", "linux", "all"],
        default="all",
        help="选择构建平台 (默认: all)"
    )
    parser.add_argument(
        "--clean", 
        action="store_true",
        help="清理构建文件"
    )
    parser.add_argument(
        "--onefile", 
        action="store_true",
        help="生成单文件可执行程序"
    )
    return parser.parse_args()

def clean_build_files():
    """清理构建文件"""
    print("正在清理构建文件...")
    
    # 清理PyInstaller生成的文件
    for dir_name in ["dist", "build", "__pycache__"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    # 清理.spec文件
    for file_name in os.listdir("."):
        if file_name.endswith(".spec"):
            os.remove(file_name)
    
    print("清理完成!")

def build_macos(args):
    """构建macOS版本（优化版）"""
    print("正在构建macOS版本...")
    
    # 获取PyQt6翻译文件路径
    import PyQt6
    pyqt_path = os.path.dirname(PyQt6.__file__)
    translations_src = os.path.join(pyqt_path, 'Qt6', 'translations')
    
    # 排除不需要的模块（减小体积）
    exclude_modules = [
        'tkinter',           # Tk GUI 框架
        'test',              # Python 测试模块
        'unittest',          # 单元测试
        # 'email',           # ❗️ 不能排除！requests 和 openai 依赖此模块
        'http.server',       # HTTP 服务器
        # 'urllib',          # ⚠️ 不能排除！被 zipfile、pathlib 等核心模块依赖
        'pydoc',             # 文档生成
        'distutils',         # 打包工具
        'setuptools',        # 安装工具
        'pip',               # 包管理器
        'PyQt6.QtWebEngineWidgets',  # Web引擎（如不用广告）
        'PyQt6.QtWebEngineCore',
        'PyQt6.QtBluetooth',
        'PyQt6.QtNfc',
        'PyQt6.QtPositioning',
        'PyQt6.QtSensors',
        'PyQt6.QtSerialPort',
        'PyQt6.QtMultimedia',
        'PyQt6.QtMultimediaWidgets',
    ]
    
    cmd = [
        "pyinstaller",
        "--name=X-Tool",
        "--windowed",
        "--osx-bundle-identifier=com.bitouyun.app",
        "--add-data=resources:resources",
        f"--add-data={translations_src}:translations",
        # 注释掉：不打包 plugins 目录，让应用从外部 dist/plugins/ 加载
        # "--collect-data=src.plugins",
        "--hidden-import=PyQt6",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=configparser",
        # requests/openai 依赖的标准库模块
        "--hidden-import=email",
        "--hidden-import=email.mime",
        "--hidden-import=email.mime.text",
        "--hidden-import=email.mime.multipart",
        "--hidden-import=ipaddress",
        "--hidden-import=http.cookies",
        "--hidden-import=http.client",
        "--hidden-import=zoneinfo",
        "--hidden-import=urllib",
        "--hidden-import=urllib.parse",
        "--hidden-import=urllib.request",
        "--icon=icon.icns",
    ]
    
    # 添加排除模块
    for module in exclude_modules:
        cmd.append(f"--exclude-module={module}")
    
    # 启用 UPX 压缩（如果已安装）
    upx_path = "/usr/local/bin/upx"  # macOS Homebrew 默认路径
    if os.path.exists(upx_path) or shutil.which("upx"):
        cmd.append("--upx-dir=/usr/local/bin")
        print("✅ 已启用 UPX 压缩")
    else:
        print("⚠️  未检测到 UPX，跳过压缩（提示：运行 'brew install upx' 安装）")
    
    if args.onefile:
        cmd.append("--onefile")
    
    cmd.append("main.py")
    
    try:
        subprocess.run(cmd, check=True)
        print("macOS版本构建完成!")
    except subprocess.CalledProcessError as e:
        print(f"macOS版本构建失败: {e}")
        return False
    
    return True

def build_windows(args):
    """构建 Windows版本（优化版）"""
    print("正在构建 Windows版本...")
    
    # 获取PyQt6翻译文件路径
    import PyQt6
    pyqt_path = os.path.dirname(PyQt6.__file__)
    translations_src = os.path.join(pyqt_path, 'Qt6', 'translations')
    
    # 排除不需要的模块
    exclude_modules = [
        'tkinter', 'test', 'unittest', 
        # 'email',  # ❗️ 不能排除！requests 和 openai 依赖此模块
        'http.server',
        # 'urllib',  # ⚠️ 不能排除！被 zipfile、pathlib 等核心模块依赖
        'pydoc', 'distutils', 'setuptools', 'pip',
        'PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebEngineCore',
        'PyQt6.QtBluetooth', 'PyQt6.QtNfc', 'PyQt6.QtPositioning',
        'PyQt6.QtSensors', 'PyQt6.QtSerialPort',
        'PyQt6.QtMultimedia', 'PyQt6.QtMultimediaWidgets',
    ]
    
    cmd = [
        "pyinstaller",
        "--name=X-Tool",
        "--windowed",
        "--add-data=resources;resources",
        f"--add-data={translations_src};translations",
        # 注释掉：不打包 plugins 目录，让应用从外部 dist/plugins/ 加载
        # "--collect-data=src.plugins",
        "--hidden-import=PyQt6",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=configparser",
        # requests/openai 依赖的标准库模块
        "--hidden-import=email",
        "--hidden-import=email.mime",
        "--hidden-import=email.mime.text",
        "--hidden-import=email.mime.multipart",
        "--hidden-import=ipaddress",
        "--hidden-import=http.cookies",
        "--hidden-import=http.client",
        "--hidden-import=zoneinfo",
        "--hidden-import=urllib",
        "--hidden-import=urllib.parse",
        "--hidden-import=urllib.request",
    ]
    
    for module in exclude_modules:
        cmd.append(f"--exclude-module={module}")
    
    # Windows UPX 检测
    if shutil.which("upx"):
        cmd.append("--upx-dir=upx")
        print("✅ 已启用 UPX 压缩")
    
    if args.onefile:
        cmd.append("--onefile")
    
    cmd.append("main.py")
    
    try:
        subprocess.run(cmd, check=True)
        print("Windows版本构建完成!")
    except subprocess.CalledProcessError as e:
        print(f"Windows版本构建失败: {e}")
        return False
    
    return True

def build_linux(args):
    """构建 Linux版本（优化版）"""
    print("正在构建 Linux版本...")
    
    # 获取PyQt6翻译文件路径
    import PyQt6
    pyqt_path = os.path.dirname(PyQt6.__file__)
    translations_src = os.path.join(pyqt_path, 'Qt6', 'translations')
    
    # 排除不需要的模块
    exclude_modules = [
        'tkinter', 'test', 'unittest', 
        # 'email',  # ❗️ 不能排除！requests 和 openai 依赖此模块
        'http.server',
        # 'urllib',  # ⚠️ 不能排除！被 zipfile、pathlib 等核心模块依赖
        'pydoc', 'distutils', 'setuptools', 'pip',
        'PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebEngineCore',
        'PyQt6.QtBluetooth', 'PyQt6.QtNfc', 'PyQt6.QtPositioning',
        'PyQt6.QtSensors', 'PyQt6.QtSerialPort',
        'PyQt6.QtMultimedia', 'PyQt6.QtMultimediaWidgets',
    ]
    
    cmd = [
        "pyinstaller",
        "--name=X-Tool",
        "--windowed",
        "--add-data=resources:resources",
        f"--add-data={translations_src}:translations",
        # 注释掉：不打包 plugins 目录，让应用从外部 dist/plugins/ 加载
        # "--collect-data=src.plugins",
        "--hidden-import=PyQt6",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=configparser",
        # requests/openai 依赖的标准库模块
        "--hidden-import=email",
        "--hidden-import=email.mime",
        "--hidden-import=email.mime.text",
        "--hidden-import=email.mime.multipart",
        "--hidden-import=ipaddress",
        "--hidden-import=http.cookies",
        "--hidden-import=http.client",
        "--hidden-import=zoneinfo",
        "--hidden-import=urllib",
        "--hidden-import=urllib.parse",
        "--hidden-import=urllib.request",
    ]
    
    for module in exclude_modules:
        cmd.append(f"--exclude-module={module}")
    
    # Linux UPX 检测
    if shutil.which("upx"):
        cmd.append("--upx-dir=/usr/bin")
        print("✅ 已启用 UPX 压缩")
    
    if args.onefile:
        cmd.append("--onefile")
    
    cmd.append("main.py")
    
    try:
        subprocess.run(cmd, check=True)
        print("Linux版本构建完成!")
    except subprocess.CalledProcessError as e:
        print(f"Linux版本构建失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    args = parse_args()
    
    # 如果需要清理
    if args.clean:
        clean_build_files()
        return
    
    # 确保必要目录存在
    for d in ["resources", "plugins"]:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"创建目录: {d}")
    
    # 根据平台构建
    success = True
    
    if args.platform in ["macos", "all"]:
        if not build_macos(args):
            success = False
    
    if args.platform in ["windows", "all"]:
        if not build_windows(args):
            success = False
    
    if args.platform in ["linux", "all"]:
        if not build_linux(args):
            success = False
    
    if success:
        # 后置处理：拷贝外部文件夹到 dist 目录
        print("\n正在执行后置处理（拷贝外部文件夹）...")
        dist_dir = "dist"
        folders_to_copy = ["plugins"]  # 移除 lib，由插件按需下载依赖
        
        for folder in folders_to_copy:
            src_path = folder
            # macOS .app 模式，文件夹应放在 .app 旁边
            # Windows/Linux 模式，文件夹应放在生成的程序文件夹内
            target_dirs = []
            if sys.platform == 'darwin':
                target_dirs.append(dist_dir)
            else:
                target_dirs.append(os.path.join(dist_dir, "X-Tool"))
            
            for t_dir in target_dirs:
                if os.path.exists(t_dir):
                    dest_path = os.path.join(t_dir, folder)
                    # 无论源目录是否有内容，都确保目标目录存在
                    if not os.path.exists(dest_path):
                        os.makedirs(dest_path)
                    
                    if os.path.exists(src_path) and os.listdir(src_path):
                        # 如果源目录有内容，则拷贝
                        if os.path.exists(dest_path):
                            shutil.rmtree(dest_path)
                        shutil.copytree(src_path, dest_path)
                        print(f"✅ 已同步内容到: {dest_path}")
                    else:
                        print(f"✅ 已创建空目录: {dest_path}")

        print("\n所有构建任务完成!")
    else:
        print("\n构建过程中出现错误!")
        sys.exit(1)

if __name__ == "__main__":
    main()
