"""
主题系统模块

新主题系统（推荐使用）:
    from src.themes.theme import Theme

    # 应用样式
    widget.setStyleSheet(Theme.get_plugin_style())
    widget.setStyleSheet(Theme.get_main_window_style())

    # 获取按钮样式
    button.setStyleSheet(Theme.get_button_style("success"))

    # 获取颜色
    color = Theme.COLOR_PRIMARY

主题管理器:
    from src.themes.simple_theme_manager import get_theme_manager

    # 获取主题管理器
    theme_manager = get_theme_manager()

    # 注册窗口
    theme_manager.register_widget(window)

    # 刷新主题
    theme_manager.refresh_theme()
"""

# 新主题系统（推荐）
from src.themes.theme import Theme
from src.themes.simple_theme_manager import get_theme_manager, ThemeManager as SimpleThemeManager

__all__ = [
    # 新系统
    'Theme',
    'SimpleThemeManager',
    'get_theme_manager',
]
