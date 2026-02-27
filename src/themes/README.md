# X-Tool 样式系统

一套完整、灵活、可扩展的 UI 主题系统，为 X-Tool 提供统一的视觉风格和主题切换能力。

---

## 快速开始

### 基本使用

```python
from src.themes import get_theme_manager

# 获取主题管理器（单例）
theme_manager = get_theme_manager()

# 应用主题到控件
theme_manager.apply_theme_to_widget(widget, "plugin")

# 获取按钮样式
button_style = theme_manager.get_button_style("primary")
button.setStyleSheet(button_style)

# 获取主题颜色
primary_color = theme_manager.get_color("primary")
```

### 在插件中使用

```python
from src.themes import get_theme_manager
from src.plugins.base_plugin import BasePlugin

class MyPlugin(BasePlugin):
    def __init__(self):
        super().__init__("我的插件", "描述")
        self.theme_manager = get_theme_manager()
        self._setup_ui()
        self.apply_theme()  # 应用主题

        # 监听主题变更
        self.theme_manager.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, theme_id: str):
        """主题变更时重新应用样式"""
        self.apply_theme()
```

---

## 核心组件

### 1. ThemeManager (主题管理器)

**单例模式**，负责主题的注册、切换和应用。

**主要方法**:

| 方法 | 说明 |
|------|------|
| `set_theme(theme_id)` | 切换主题 |
| `get_current_theme()` | 获取当前主题对象 |
| `get_current_theme_id()` | 获取当前主题ID |
| `apply_theme_to_widget(widget, type)` | 应用主题到控件 |
| `get_button_style(type)` | 获取按钮样式 |
| `get_color(name)` | 获取主题颜色 |
| `get_available_themes()` | 获取所有可用主题 |

**样式类型**:
- `"all"` - 完整样式（主窗口）
- `"main_window"` - 主窗口样式
- `"plugin"` - 插件容器样式
- `"input"` - 输入框样式
- `"menubar"` - 菜单栏样式
- `"menu"` - 菜单样式
- `"scrollbar"` - 滚动条样式
- `"groupbox"` - 分组框样式
- `"tree"` - 树形控件样式
- `"stacked"` - 堆栈部件样式
- `"splitter"` - 分割器样式
- `"tooltip"` - 工具提示样式

**按钮类型**:
- `"primary"` - 主要按钮（蓝色）
- `"success"` - 成功按钮（绿色）
- `"warning"` - 警告按钮（橙色）
- `"danger"` - 危险按钮（红色）
- `"info"` - 信息按钮（灰色）

### 2. BaseTheme (主题基类)

所有主题必须继承的抽象基类。

**必须实现的方法**:
- `get_main_window_style()` - 主窗口样式
- `get_menubar_style()` - 菜单栏样式
- `get_menu_style()` - 菜单样式
- `get_button_style(type)` - 按钮样式
- `get_input_style()` - 输入框样式
- `get_groupbox_style()` - 分组框样式
- `get_scrollbar_style()` - 滚动条样式
- `get_plugin_container_style()` - 插件容器样式
- `get_colors()` - 获取颜色字典

### 3. LightTheme (浅色主题)

默认主题，清爽简洁的白色系界面风格。

**主题ID**: `"light"`

---

## 主题颜色

### LightTheme 色彩体系

**背景色**:
- `bg_main` - 主背景 (#f5f6fa)
- `bg_widget` - 控件背景 (#ffffff)
- `bg_sidebar` - 侧边栏背景 (#ffffff)
- `bg_input` - 输入框背景 (#ffffff)
- `bg_disabled` - 禁用背景 (#f1f2f6)

**文字色**:
- `text_primary` - 主要文字 (#2f3640)
- `text_secondary` - 次要文字 (#636e72)
- `text_disabled` - 禁用文字 (#b2bec3)
- `text_inverse` - 反色文字 (#ffffff)

**边框色**:
- `border_default` - 默认边框 (#dcdde1)
- `border_focus` - 聚焦边框 (#3498db)
- `border_hover` - 悬停边框 (#bdc3c7)

**功能色**:
- `primary` - 主色调 (#3498db)
- `success` - 成功色 (#2ecc71)
- `warning` - 警告色 (#e67e22)
- `danger` - 危险色 (#e74c3c)
- `info` - 信息色 (#95a5a6)

---

## 扩展主题

### 创建自定义主题

```python
from src.themes.base_theme import BaseTheme

class MyCustomTheme(BaseTheme):
    THEME_ID = "my_custom"
    THEME_NAME = "我的自定义主题"
    THEME_DESCRIPTION = "这是一个自定义主题"

    # 定义颜色
    COLORS = {
        "bg_main": "#f0f0f0",
        "bg_widget": "#ffffff",
        # ... 更多颜色定义
    }

    # 实现所有抽象方法
    def get_main_window_style(self) -> str:
        return f"QMainWindow {{ background-color: {self.COLORS['bg_main']}; }}"

    def get_button_style(self, style_type: str = "primary") -> str:
        # ... 实现按钮样式
        pass

    # ... 实现其他必需方法
```

### 注册主题

```python
from src.themes import get_theme_manager

theme_manager = get_theme_manager()
theme_manager.register_theme(MyCustomTheme)
```

---

## 信号

ThemeManager 提供以下信号：

| 信号 | 参数 | 说明 |
|------|------|------|
| `theme_changed` | `theme_id: str` | 主题变更时发射 |

**监听主题变更**:
```python
theme_manager.theme_changed.connect(self._on_theme_changed)

def _on_theme_changed(self, theme_id: str):
    """主题变更时重新应用样式"""
    self.theme_manager.apply_theme_to_widget(self, "plugin")
```

---

## 文件结构

```
src/themes/
├── __init__.py           # 模块导出
├── base_theme.py         # 主题基类
├── light_theme.py        # 浅色主题
├── dark_theme.py         # 深色主题（预留）
└── theme_manager.py      # 主题管理器
```

---

## 相关文档

- [样式系统设计方案总结](../../docs/样式系统设计方案总结.md)
- [样式系统架构图](../../docs/样式系统架构图.md)
- [主题系统迁移指南](../../docs/主题系统迁移指南.md)
- [示例代码](../../examples/plugin_style_example.py)

---

## API 参考

### get_theme_manager()

获取 ThemeManager 单例实例。

```python
from src.themes import get_theme_manager
theme_manager = get_theme_manager()
```

---

## 常见问题

**Q: 如何切换主题？**

A: 调用 `theme_manager.set_theme(theme_id)`

**Q: 如何获取主题颜色？**

A: 调用 `theme_manager.get_color(color_name)`

**Q: 如何在插件中使用主题？**

A: 参考 [主题系统迁移指南](../../docs/主题系统迁移指南.md)

**Q: 如何添加新主题？**

A: 继承 BaseTheme 并注册到 ThemeManager

---

*最后更新: 2024-02-27*
