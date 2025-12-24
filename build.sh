#!/bin/bash

# X-Tool 构建脚本
echo "========================================"
echo "X-Tool 构建脚本"
echo "========================================"

# 定义函数：显示菜单并获取用户选择
show_menu() {
    echo "请选择要执行的操作："
    echo "1. 构建所有平台"
    echo "2. 选择特定平台构建"
    echo "3. 清理构建文件"
    echo "4. 退出"
    echo -n "请输入选项 (1-4): "
    read -r choice
}

# 定义函数：选择构建平台
select_platform() {
    echo "请选择构建平台："
    echo "1. Windows"
    echo "2. macOS"
    echo "3. Linux"
    echo "4. 所有平台"
    echo -n "请输入选项 (1-4): "
    read -r platform_choice
    
    case $platform_choice in
        1) PLATFORM="windows" ;;
        2) PLATFORM="macos" ;;
        3) PLATFORM="linux" ;;
        4) PLATFORM="all" ;;
        *) echo "无效选项，默认使用所有平台" ; PLATFORM="all" ;;
    esac
}

# 定义函数：选择是否生成单文件
select_onefile() {
    echo -n "是否生成单文件可执行程序？(y/n): "
    read -r onefile_choice
    
    if [[ $onefile_choice == "y" || $onefile_choice == "Y" ]]; then
        ONEFILE="--onefile"
    else
        ONEFILE=""
    fi
}

# 初始化变量
PLATFORM="all"
ONEFILE=""
CLEAN="false"

# 显示菜单并处理用户选择
while true; do
    show_menu
    
    case $choice in
        1) # 构建所有平台
            PLATFORM="all"
            select_onefile
            break
            ;;
        2) # 选择特定平台构建
            select_platform
            select_onefile
            break
            ;;
        3) # 清理构建文件
            CLEAN="true"
            break
            ;;
        4) # 退出
            echo "退出构建脚本"
            exit 0
            ;;
        *) # 无效选项
            echo "无效选项，请重新输入"
            ;;
    esac
done

# 检查虚拟环境
if [ -d "venv" ]; then
    echo "检测到虚拟环境，正在激活..."
    source venv/bin/activate
else
    echo "警告: 未检测到虚拟环境，将使用当前 Python 环境"
fi

# 安装构建依赖
echo "正在安装/更新构建依赖..."
pip install --upgrade pyinstaller

# 执行操作
if [ "$CLEAN" == "true" ]; then
    echo "正在清理构建文件..."
    python build.py --clean
else
    echo "正在构建 X-Tool ($PLATFORM)${ONEFILE:+, 单文件模式}..."
    python build.py --platform "$PLATFORM" $ONEFILE
fi

# 检查构建结果
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "构建成功!"
    echo "========================================"
    echo "构建输出位于: dist/目录下"
    echo "- Windows: dist/X-Tool.exe"
    echo "- macOS: dist/X-Tool.app"
    echo "- Linux: dist/X-Tool"
else
    echo ""
    echo "========================================"
    echo "构建失败!"
    echo "========================================"
    exit 1
fi
