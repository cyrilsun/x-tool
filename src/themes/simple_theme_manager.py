"""
主题管理器 - 简化版
支持运行时主题切换和样式重新应用
"""
from typing import List, Callable
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget, QApplication
from src.utils.logger import logger


class ThemeManager(QObject):
    """
    主题管理器 - 单例模式
    管理主题切换并通知所有窗口更新样式
    """

    # 主题变更信号
    theme_changed = pyqtSignal()  # 主题切换时发射

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

        # 当前主题
        self._current_theme_id = "default"

        # 注册的样式更新回调
        self._style_callbacks: List[Callable] = []

        # 需要应用主题的窗口列表
        self._themed_widgets: List[QWidget] = []

        self._initialized = True
        logger.info("主题管理器已初始化")

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
        logger.info("正在刷新主题...")

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
        self.theme_changed.emit()

        logger.info(f"主题刷新完成，更新了 {len(self._themed_widgets)} 个窗口")

    def set_theme(self, theme_id: str = "default") -> None:
        """
        设置当前主题
        目前仅支持默认主题，预留接口用于未来扩展

        Args:
            theme_id: 主题ID
        """
        if self._current_theme_id != theme_id:
            self._current_theme_id = theme_id
            logger.info(f"主题已切换: {theme_id}")
            self.refresh_theme()

    def get_current_theme_id(self) -> str:
        """
        获取当前主题ID

        Returns:
            主题ID
        """
        return self._current_theme_id

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
