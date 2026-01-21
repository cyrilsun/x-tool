#!/bin/bash
# X-Tool 插件依赖安装脚本
# 用途：将插件所需的第三方库安装到 lib 目录，确保打包后可用

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="${SCRIPT_DIR}/lib"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  X-Tool 插件依赖安装工具${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 创建 lib 目录
if [ ! -d "$LIB_DIR" ]; then
    mkdir -p "$LIB_DIR"
    echo -e "${GREEN}✅ 创建 lib 目录: $LIB_DIR${NC}"
else
    echo -e "${YELLOW}ℹ️  lib 目录已存在: $LIB_DIR${NC}"
fi

# 定义插件依赖列表
declare -A PLUGIN_DEPS=(
    ["speech_draft_plugin"]="openai requests python-docx"
    # 如果有其他插件，可以继续添加
    # ["other_plugin"]="dependency1 dependency2"
)

# 询问是否安装特定插件的依赖
echo ""
echo -e "${YELLOW}可用插件及其依赖：${NC}"
for plugin in "${!PLUGIN_DEPS[@]}"; do
    echo -e "  ${GREEN}${plugin}${NC}: ${PLUGIN_DEPS[$plugin]}"
done
echo ""

# 安装函数
install_dependencies() {
    local deps=$1
    echo -e "${BLUE}开始安装依赖...${NC}"
    
    for dep in $deps; do
        echo ""
        echo -e "${YELLOW}正在安装: $dep${NC}"
        
        # 使用 pip install -t 安装到 lib 目录
        if pip install -t "$LIB_DIR" "$dep" --upgrade; then
            echo -e "${GREEN}✅ $dep 安装成功${NC}"
        else
            echo -e "${RED}❌ $dep 安装失败${NC}"
            return 1
        fi
    done
    
    return 0
}

# 询问用户选择
echo -e "${YELLOW}请选择操作：${NC}"
echo "  1) 安装所有插件依赖（推荐）"
echo "  2) 仅安装 speech_draft_plugin 依赖"
echo "  3) 清理 lib 目录"
echo "  0) 退出"
echo ""
read -p "请输入选项 [1]: " choice
choice=${choice:-1}

case $choice in
    1)
        echo ""
        echo -e "${BLUE}========================================${NC}"
        echo -e "${BLUE}  安装所有插件依赖${NC}"
        echo -e "${BLUE}========================================${NC}"
        
        all_deps=""
        for deps in "${PLUGIN_DEPS[@]}"; do
            all_deps="$all_deps $deps"
        done
        
        # 去重
        all_deps=$(echo $all_deps | tr ' ' '\n' | sort -u | tr '\n' ' ')
        
        if install_dependencies "$all_deps"; then
            echo ""
            echo -e "${GREEN}========================================${NC}"
            echo -e "${GREEN}  ✅ 所有依赖安装完成！${NC}"
            echo -e "${GREEN}========================================${NC}"
        else
            echo ""
            echo -e "${RED}========================================${NC}"
            echo -e "${RED}  ❌ 部分依赖安装失败${NC}"
            echo -e "${RED}========================================${NC}"
            exit 1
        fi
        ;;
        
    2)
        echo ""
        echo -e "${BLUE}========================================${NC}"
        echo -e "${BLUE}  安装 speech_draft_plugin 依赖${NC}"
        echo -e "${BLUE}========================================${NC}"
        
        if install_dependencies "${PLUGIN_DEPS[speech_draft_plugin]}"; then
            echo ""
            echo -e "${GREEN}========================================${NC}"
            echo -e "${GREEN}  ✅ speech_draft_plugin 依赖安装完成！${NC}"
            echo -e "${GREEN}========================================${NC}"
        else
            echo ""
            echo -e "${RED}========================================${NC}"
            echo -e "${RED}  ❌ 部分依赖安装失败${NC}"
            echo -e "${RED}========================================${NC}"
            exit 1
        fi
        ;;
        
    3)
        echo ""
        echo -e "${YELLOW}确定要清理 lib 目录吗？此操作不可恢复。${NC}"
        read -p "输入 'yes' 确认: " confirm
        
        if [ "$confirm" = "yes" ]; then
            rm -rf "$LIB_DIR"/*
            echo -e "${GREEN}✅ lib 目录已清理${NC}"
        else
            echo -e "${YELLOW}已取消操作${NC}"
        fi
        ;;
        
    0)
        echo -e "${YELLOW}已退出${NC}"
        exit 0
        ;;
        
    *)
        echo -e "${RED}❌ 无效选项${NC}"
        exit 1
        ;;
esac

# 显示安装结果
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  lib 目录内容${NC}"
echo -e "${BLUE}========================================${NC}"
ls -1 "$LIB_DIR" | head -20
echo ""
echo -e "${GREEN}💡 提示：${NC}"
echo -e "  1. 现在可以运行 ${YELLOW}./build.sh${NC} 进行打包"
echo -e "  2. 打包后的应用会自动包含这些依赖"
echo -e "  3. 如需验证，可运行: ${YELLOW}python -c 'import sys; sys.path.insert(0, \"lib\"); import openai; print(\"OK\")'${NC}"
echo ""
