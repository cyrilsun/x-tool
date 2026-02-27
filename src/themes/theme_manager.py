"""
主题管理器（单例模式）
负责主题的注册、切换和应用
"""
from typing import Dict, Type, Optional
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal
from src.themes.base_theme import BaseTheme
from src.themes.light_theme import LightTheme
from src.utils.logger import logger


class ThemeManager(QObject):
    """
    主题管理器 - 单例模式
    """

    # 主题变更信号
    theme_changed = pyqtSignal(str)  # 参数为新主题ID

    _instance: Optional['ThemeManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        super().__init__()

        # 注册的主题
        self._themes: Dict[str, Type[BaseTheme]] = {}

        # 当前激活的主题实例
        self._current_theme: Optional[BaseTheme] = None

        # 自动注册内置主题
        self.register_theme(LightTheme)

        # 从配置加载默认主题
        self._load_default_theme()

        self._initialized = True

    def register_theme(self, theme_class: Type[BaseTheme]) -> None:
        """
        注册主题
        :param theme_class: 主题类（非实例）
        """
        theme_id = theme_class.THEME_ID
        if theme_id in self._themes:
            logger.warning(f"主题 {theme_id} 已存在，将被覆盖")
        self._themes[theme_id] = theme_class
        logger.info(f"已注册主题: {theme_class.THEME_NAME} ({theme_id})")

    def get_available_themes(self) -> Dict[str, str]:
        """
        获取所有可用主题
        :return: {theme_id: theme_name}
        """
        return {
            theme_id: theme_class.THEME_NAME
            for theme_id, theme_class in self._themes.items()
        }

    def set_theme(self, theme_id: str, save_to_config: bool = True) -> bool:
        """
        设置当前主题
        :param theme_id: 主题ID
        :param save_to_config: 是否保存到配置
        :return: 是否成功设置
        """
        if theme_id not in self._themes:
            logger.error(f"主题 {theme_id} 不存在")
            return False

        try:
            # 创建主题实例
            theme_class = self._themes[theme_id]
            self._current_theme = theme_class()

            logger.info(f"已切换到主题: {self._current_theme.THEME_NAME}")

            # 保存到配置
            if save_to_config:
                self._save_theme_to_config(theme_id)

            # 发射主题变更信号
            self.theme_changed.emit(theme_id)

            return True
        except Exception as e:
            logger.error(f"设置主题失败: {e}")
            return False

    def get_current_theme(self) -> Optional[BaseTheme]:
        """
        获取当前主题实例
        :return: 当前主题对象
        """
        return self._current_theme

    def get_current_theme_id(self) -> Optional[str]:
        """
        获取当前主题ID
        :return: 主题ID
        """
        if self._current_theme:
            return self._current_theme.THEME_ID
        return None

    def apply_theme_to_widget(self, widget, style_type: str = "all") -> None:
        """
        应用主题到指定控件
        :param widget: Qt控件对象
        :param style_type: 样式类型 (all, main_window, plugin, input, etc.)
        """
        if not self._current_theme:
            logger.warning("未设置主题，无法应用样式")
            return

        style_map = {
            "all": lambda t: t.get_all_styles(),
            "main_window": lambda t: t.get_main_window_style(),
            "plugin": lambda t: t.get_plugin_container_style(),
            "input": lambda t: t.get_input_style(),
            "menubar": lambda t: t.get_menubar_style(),
            "menu": lambda t: t.get_menu_style(),
            "scrollbar": lambda t: t.get_scrollbar_style(),
            "groupbox": lambda t: t.get_groupbox_style(),
            "tree": lambda t: t.get_tree_widget_style(),
            "stacked": lambda t: t.get_stacked_widget_style(),
            "splitter": lambda t: t.get_splitter_style(),
            "tooltip": lambda t: t.get_tooltip_style(),
        }

        if style_type not in style_map:
            logger.error(f"未知样式类型: {style_type}")
            return

        try:
            style = style_map[style_type](self._current_theme)
            widget.setStyleSheet(style)
        except Exception as e:
            logger.error(f"应用样式失败: {e}")

    def get_button_style(self, button_type: str = "primary") -> str:
        """
        获取指定类型的按钮样式
        :param button_type: 按钮类型
        :return: 样式字符串
        """
        if not self._current_theme:
            return ""

        try:
            return self._current_theme.get_button_style(button_type)
        except Exception as e:
            logger.error(f"获取按钮样式失败: {e}")
            return ""

    def get_color(self, color_name: str) -> str:
        """
        获取主题颜色
        :param color_name: 颜色名称
        :return: 颜色值（如 #3498db）
        """
        if not self._current_theme:
            return "#000000"

        colors = self._current_theme.get_colors()
        return colors.get(color_name, "#000000")

    def _load_default_theme(self) -> None:
        """从配置加载默认主题"""
        try:
            from src.db.database import Database
            with Database() as db:
                theme_id = db.config_manager.get_current_theme()
                if not theme_id or theme_id not in self._themes:
                    theme_id = LightTheme.THEME_ID  # 默认使用浅色主题

                self.set_theme(theme_id, save_to_config=False)
                logger.info(f"从配置加载主题: {theme_id}")
        except Exception as e:
            logger.warning(f"加载默认主题失败，使用浅色主题: {e}")
            self.set_theme(LightTheme.THEME_ID, save_to_config=False)

    def _save_theme_to_config(self, theme_id: str) -> None:
        """保存主题到配置"""
        try:
            from src.db.database import Database
            with Database() as db:
                db.config_manager.set_current_theme(theme_id)
            logger.info(f"已保存主题配置: {theme_id}")
        except Exception as e:
            logger.error(f"保存主题配置失败: {e}")


# 全局访问点
def get_theme_manager() -> ThemeManager:
    """
    获取主题管理器实例
    :return: ThemeManager 单例
    """
    return ThemeManager()