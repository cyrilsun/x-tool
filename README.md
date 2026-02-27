# X-Tool 桌面工具箱

一个基于 **PyQt6** 的高性能、插件化桌面软件框架。支持插件动态加载、热插拔及完整的依赖管理，旨在为开发者提供一个极致简洁且功能强大的工具集成平台。

---

## 🌟 核心特性

- 🧩 **插件化架构**：支持 Python 插件动态加载与热插拔，无需重启软件。
- 📦 **依赖隔离**：完整的 `.xpkg` 插件包方案，支持 lib 依赖与插件数据同步导入导出。
- 📂 **灵活管理**：支持自定义文件夹分类，左侧工具栏支持模糊搜索与即时定位。
- 🔄 **备份恢复**：提供一键备份/恢复功能，保障插件与配置数据的安全迁移。
- 🎨 **主题系统**：内置浅色/深色主题，支持运行时切换。

## 🛠️ 技术栈

- **核心语言**: Python 3.9+
- **界面框架**: PyQt6
- **数据存储**: SQLite3
- **构建工具**: PyInstaller

## 🚀 快速启动

### 1. 环境准备
```bash
# 克隆项目
git clone https://github.com/cyrilsun/x-tool.git
cd x-tool

# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 安装插件依赖
如果需要运行包含第三方库（如 `openai`, `requests`）的插件，请执行：
```bash
chmod +x install_plugin_deps.sh
./install_plugin_deps.sh
```

### 4. 运行项目
```bash
python main.py
```

---

## 🔌 插件开发

在 `plugins` 目录下创建独立的 `.py` 文件即可扩展功能。所有插件必须继承 `BasePlugin` 基类。

**滚动条已自动统一**：`BasePlugin` 自动设置统一的滚动条布局，无需手动创建。

### 快速开始

```python
from PyQt6.QtWidgets import QLabel
from src.plugins.base_plugin import BasePlugin

class MyPlugin(BasePlugin):
    PLUGIN_INFO = {
        "name": "我的插件",
        "description": "插件描述",
    }

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def get_widget(self):
        return self

    def _setup_ui(self):
        # 直接获取已创建的内容布局，滚动条已自动设置
        layout = self.get_content_layout()
        layout.addWidget(QLabel("Hello, World!"))
```

### 核心 API

| 类别 | 方法 | 说明 |
|------|------|------|
| **必须** | `get_widget()` | 返回插件主 Widget |
| **布局** | `get_content_layout()` | 获取内容布局（滚动条已自动设置） |
| **UI** | `create_group_box(title)` | 创建分组框 |
| **UI** | `create_button(text, type)` | 创建按钮 |
| **UI** | `create_description_section(html)` | 创建可折叠说明区（**自动显示元数据**） |
| **工具** | `show_info/warning/error(msg)` | 显示提示框 |
| **工具** | `log_info/debug/error(msg)` | 记录日志 |

### 插件元数据 (PLUGIN_INFO)

插件元数据会在**插件说明区域顶部**自动显示：

| 字段 | 说明 | 示例 |
|------|------|------|
| `name` | 插件名称（必需） | `"UUID生成"` |
| `description` | 插件描述（必需） | `"批量生成通用唯一识别码"` |
| `version` | 版本号 | `"1.0.0"` → 显示为 "版本: 1.0.0" |
| `author` | 作者 | `"X-Tool"` → 显示为 "作者: X-Tool" |
| `category` | 分类 | `"开发工具"` → 显示为 "分类: 开发工具" |
| `icon` | 图标名（可选） | 预留字段 |

### 按钮样式类型

`create_button()` 支持的样式：`primary`(蓝) / `success`(绿) / `warning`(橙) / `danger`(红) / `info`(灰) / `secondary`(浅灰)

### 完整示例

查看 `plugins/uuid_generator_plugin.py` 或使用 `plugins/_plugin_template.py` 模板。

📖 **详细文档**: [插件开发指南.md](docs/插件开发指南.md)

---
