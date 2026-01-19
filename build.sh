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
    
    # 检查构建是否成功
    if [ $? -eq 0 ]; then
        echo "正在准备构建输出目录 (dist) 的依赖文件..."
        
        # 1. 创建必要的运行目录
        mkdir -p dist/data dist/log dist/plugins dist/translations
        
        # 2. 拷贝内置插件 (如果不包含在可执行文件中)
        if [ -d "plugins" ]; then
            echo "正在拷贝插件到 dist/plugins..."
            cp -r plugins/* dist/plugins/ 2>/dev/null || true
        fi

        # 3. 处理翻译文件 (特别是 macOS 和通用环境)
        if [[ -d "translations" ]]; then
            echo "正在拷贝本地翻译文件..."
            cp -r translations/* dist/translations/ 2>/dev/null || true
        fi

        # 4. 特殊处理：获取并拷贝 PyQt6 的中文翻译文件 qt_zh_CN.qm
        echo "正在查找并拷贝 PyQt6 基础翻译文件..."
        PYQT_PATH=$(python -c "import PyQt6, os; print(os.path.dirname(PyQt6.__file__))" 2>/dev/null)
        if [ ! -z "$PYQT_PATH" ]; then
            # 不同环境路径可能略有不同，尝试几个常见位置
            QM_FILES=("$PYQT_PATH/Qt6/translations/qt_zh_CN.qm" "$PYQT_PATH/Qt/translations/qt_zh_CN.qm")
            for QM_SRC in "${QM_FILES[@]}"; do
                if [ -f "$QM_SRC" ]; then
                    cp "$QM_SRC" dist/translations/
                    echo "成功拷贝: $QM_SRC -> dist/translations/"
                    break
                fi
            done
        fi
        
        # 5. 如果是 macOS .app 模式，将这些目录同步到 .app 内部的 Resources 目录下 (可选，根据项目加载逻辑)
        if [[ ( "$PLATFORM" == "macos" || "$PLATFORM" == "all" ) && -d "dist/X-Tool.app" ]]; then
            echo "检测到 macOS .app，正在同步资源到 Contents/Resources..."
            RES_DIR="dist/X-Tool.app/Contents/Resources"
            mkdir -p "$RES_DIR/data" "$RES_DIR/log" "$RES_DIR/plugins" "$RES_DIR/translations"
            cp -r dist/translations/* "$RES_DIR/translations/" 2>/dev/null || true
            cp -r dist/plugins/* "$RES_DIR/plugins/" 2>/dev/null || true
        fi
        
        echo "输出目录准备就绪。"
    fi
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
