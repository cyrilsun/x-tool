"""
主题系统基类
定义所有主题必须实现的接口和样式常量
"""
from abc import ABC, abstractmethod
from typing import Dict
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import QObject, pyqtSignal


class ThemeColors:
    """主题颜色常量定义"""

    # 主色调（保持原有值）
    PRIMARY = "#3498db"
    PRIMARY_HOVER = "#2980b9"
    PRIMARY_PRESSED = "#1e3799"

    # 成功色
    SUCCESS = "#2ecc71"
    SUCCESS_HOVER = "#27ae60"

    # 警告色
    WARNING = "#e67e22"
    WARNING_HOVER = "#d35400"

    # 危险色
    DANGER = "#e74c3c"
    DANGER_HOVER = "#c0392b"

    # 中性色
    INFO = "#95a5a6"
    INFO_HOVER = "#7f8c8d"


class BaseTheme(ABC):
    """主题基类 - 所有主题必须继承此类"""

    # 主题元信息
    THEME_ID: str = ""
    THEME_NAME: str = ""
    THEME_DESCRIPTION: str = ""

    def __init__(self):
        self._style_cache: Dict[str, str] = {}

    @abstractmethod
    def get_main_window_style(self) -> str:
        """主窗口样式"""
        pass

    @abstractmethod
    def get_menubar_style(self) -> str:
        """菜单栏样式"""
        pass

    @abstractmethod
    def get_menu_style(self) -> str:
        """菜单样式"""
        pass

    @abstractmethod
    def get_button_style(self, style_type: str = "primary") -> str:
        """
        按钮样式
        :param style_type: 按钮类型 (primary, success, warning, danger, info)
        """
        pass

    @abstractmethod
    def get_input_style(self) -> str:
        """输入框样式 (QLineEdit, QTextEdit, etc.)"""
        pass

    @abstractmethod
    def get_groupbox_style(self) -> str:
        """分组框样式"""
        pass

    @abstractmethod
    def get_scrollbar_style(self) -> str:
        """滚动条样式"""
        pass

    @abstractmethod
    def get_plugin_container_style(self) -> str:
        """插件容器样式"""
        pass

    @abstractmethod
    def get_colors(self) -> Dict[str, str]:
        """获取主题颜色字典"""
        pass

    def get_all_styles(self) -> str:
        """
        获取所有样式的组合（用于全局应用）
        :return: 完整的样式表字符串
        """
        return "\n".join([
            self.get_main_window_style(),
            self.get_menubar_style(),
            self.get_menu_style(),
            self.get_input_style(),
            self.get_groupbox_style(),
            self.get_scrollbar_style(),
            "QPushButton {",
            "}",
            self.get_button_style("primary"),
            self.get_button_style("success"),
            self.get_button_style("warning"),
            self.get_button_style("danger"),
            self.get_button_style("info"),
        ])

    def _cache_style(self, key: str, style: str) -> str:
        """缓存样式以提高性能"""
        self._style_cache[key] = style
        return style