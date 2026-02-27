"""
主题管理器 - 支持浅色/深色主题切换
"""
from typing import List, Callable
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget, QApplication
from src.utils.logger import logger
from src.themes.theme import Theme as LightTheme
from src.themes.dark_theme import DarkTheme


class ThemeManager(QObject):
    """
    主题管理器 - 单例模式
    管理浅色/深色主题切换并通知所有窗口更新样式
    """

    # 主题变更信号
    theme_changed = pyqtSignal(str)  # 参数为主题ID ("light" 或 "dark")

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        super().__init__()

        # 主题模式: "light" 或 "dark"
        self._theme_mode = "light"

        # 注册的样式更新回调
        self._style_callbacks: List[Callable] = []

        # 需要应用主题的窗口列表
        self._themed_widgets: List[QWidget] = []

        # 从配置加载主题设置
        self._load_theme_from_config()

        self._initialized = True
        logger.info("主题管理器已初始化")

    def _load_theme_from_config(self) -> None:
        """从配置加载主题设置"""
        try:
            from src.db.database import Database
            with Database() as db:
                theme_mode = db.config_manager.get_config("theme_mode", "light")
                self._theme_mode = theme_mode if theme_mode in ["light", "dark"] else "light"
                logger.info(f"从配置加载主题: {self._theme_mode}")
        except Exception as e:
            logger.warning(f"加载主题配置失败，使用浅色主题: {e}")
            self._theme_mode = "light"

    def _save_theme_to_config(self) -> None:
        """保存主题设置到配置"""
        try:
            from src.db.database import Database
            with Database() as db:
                db.config_manager.set_config("theme_mode", self._theme_mode)
                logger.info(f"已保存主题配置: {self._theme_mode}")
        except Exception as e:
            logger.error(f"保存主题配置失败: {e}")

    def get_current_theme(self):
        """
        获取当前主题类

        Returns:
            LightTheme 或 DarkTheme 类
        """
        if self._theme_mode == "dark":
            return DarkTheme
        return LightTheme

    def register_widget(self, widget: QWidget) -> None:
        """
        注册需要应用主题的窗口
        当主题切换时，这些窗口会自动更新样式

        Args:
            widget: Qt 窗口或控件
        """
        if widget not in self._themed_widgets:
            self._themed_widgets.append(widget)
            logger.debug(f"已注册窗口: {widget.__class__.__name__}")

    def unregister_widget(self, widget: QWidget) -> None:
        """
        注销窗口

        Args:
            widget: Qt 窗口或控件
        """
        if widget in self._themed_widgets:
            self._themed_widgets.remove(widget)
            logger.debug(f"已注销窗口: {widget.__class__.__name__}")

    def register_style_callback(self, callback: Callable) -> None:
        """
        注册样式更新回调函数
        主题切换时，所有回调都会被调用

        Args:
            callback: 回调函数，签名为 callback() -> None
        """
        if callback not in self._style_callbacks:
            self._style_callbacks.append(callback)
            logger.debug("已注册样式回调函数")

    def unregister_style_callback(self, callback: Callable) -> None:
        """
        注销样式回调函数

        Args:
            callback: 回调函数
        """
        if callback in self._style_callbacks:
            self._style_callbacks.remove(callback)
            logger.debug("已注销样式回调函数")

    def refresh_theme(self) -> None:
        """
        刷新主题 - 重新应用样式到所有注册的窗口
        用于主题切换后更新UI
        """
        logger.info(f"正在刷新主题 ({self._theme_mode})...")

        # 调用所有样式回调
        for callback in self._style_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"样式回调执行失败: {e}")

        # 重新应用样式到所有注册的窗口
        for widget in self._themed_widgets:
            try:
                if hasattr(widget, '_apply_theme'):
                    widget._apply_theme()
            except Exception as e:
                logger.error(f"窗口 {widget.__class__.__name__} 样式更新失败: {e}")

        # 发射主题变更信号
        self.theme_changed.emit(self._theme_mode)

        logger.info(f"主题刷新完成，更新了 {len(self._themed_widgets)} 个窗口")

    def set_light_theme(self) -> None:
        """切换到浅色主题"""
        if self._theme_mode != "light":
            self._theme_mode = "light"
            self._save_theme_to_config()
            logger.info("切换到浅色主题")
            self.refresh_theme()

    def set_dark_theme(self) -> None:
        """切换到深色主题"""
        if self._theme_mode != "dark":
            self._theme_mode = "dark"
            self._save_theme_to_config()
            logger.info("切换到深色主题")
            self.refresh_theme()

    def get_theme_mode(self) -> str:
        """
        获取当前主题模式

        Returns:
            "light" 或 "dark"
        """
        return self._theme_mode

    def is_dark_mode(self) -> bool:
        """
        是否为深色模式

        Returns:
            True 如果当前是深色模式
        """
        return self._theme_mode == "dark"

    def get_current_theme_id(self) -> str:
        """
        获取当前主题ID（兼容旧代码）

        Returns:
            主题ID
        """
        return self._theme_mode

    def get_registered_widgets_count(self) -> int:
        """
        获取已注册窗口数量

        Returns:
            窗口数量
        """
        return len(self._themed_widgets)

    def clear_widgets(self) -> None:
        """清空所有已注册的窗口"""
        self._themed_widgets.clear()
        logger.debug("已清空所有注册窗口")


# 全局访问点
_theme_manager_instance = None


def get_theme_manager() -> ThemeManager:
    """
    获取主题管理器单例

    Returns:
        ThemeManager 实例
    """
    global _theme_manager_instance
    if _theme_manager_instance is None:
        _theme_manager_instance = ThemeManager()
    return _theme_manager_instance
