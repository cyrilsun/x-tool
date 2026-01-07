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
    """构建macOS版本"""
    print("正在构建macOS版本...")
    
    cmd = [
        "pyinstaller",
        "--name=X-Tool",
        "--windowed",
        "--osx-bundle-identifier=com.xtool.app",
        "--add-data=resources:resources",
        "--add-data=plugins:plugins",
        "--collect-data=src.plugins",
        "--hidden-import=pymysql",
        "--hidden-import=PyQt6",
        "--icon=icon.icns",
        "main.py"
    ]
    
    if args.onefile:
        cmd.append("--onefile")
    
    try:
        subprocess.run(cmd, check=True)
        print("macOS版本构建完成!")
    except subprocess.CalledProcessError as e:
        print(f"macOS版本构建失败: {e}")
        return False
    
    return True

def build_windows(args):
    """构建Windows版本"""
    print("正在构建Windows版本...")
    
    cmd = [
        "pyinstaller",
        "--name=X-Tool",
        "--windowed",
        "--add-data=resources;resources",
        "--add-data=plugins;plugins",
        "--collect-data=src.plugins",
        "--hidden-import=pymysql",
        "--hidden-import=PyQt6",
        "main.py"
    ]
    
    if args.onefile:
        cmd.append("--onefile")
    
    try:
        subprocess.run(cmd, check=True)
        print("Windows版本构建完成!")
    except subprocess.CalledProcessError as e:
        print(f"Windows版本构建失败: {e}")
        return False
    
    return True

def build_linux(args):
    """构建Linux版本"""
    print("正在构建Linux版本...")
    
    cmd = [
        "pyinstaller",
        "--name=X-Tool",
        "--windowed",
        "--add-data=resources:resources",
        "--add-data=plugins:plugins",
        "--collect-data=src.plugins",
        "--hidden-import=pymysql",
        "--hidden-import=PyQt6",
        "main.py"
    ]
    
    if args.onefile:
        cmd.append("--onefile")
    
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
    
    # 确保资源目录存在
    if not os.path.exists("resources"):
        os.makedirs("resources")
    
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
        print("\n所有构建任务完成!")
    else:
        print("\n构建过程中出现错误!")
        sys.exit(1)

if __name__ == "__main__":
    main()
