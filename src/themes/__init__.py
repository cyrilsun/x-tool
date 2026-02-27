"""
主题系统模块

使用示例:
    from src.themes import get_theme_manager

    # 获取主题管理器
    theme_manager = get_theme_manager()

    # 应用主题到控件
    theme_manager.apply_theme_to_widget(widget, "plugin")

    # 获取按钮样式
    button_style = theme_manager.get_button_style("primary")
    button.setStyleSheet(button_style)

    # 切换主题
    theme_manager.set_theme("dark")

    # 获取主题颜色
    primary_color = theme_manager.get_color("primary")
"""

from src.themes.base_theme import BaseTheme, ThemeColors
from src.themes.light_theme import LightTheme
from src.themes.theme_manager import ThemeManager, get_theme_manager

__all__ = [
    'BaseTheme',
    'ThemeColors',
    'LightTheme',
    'ThemeManager',
    'get_theme_manager',
]