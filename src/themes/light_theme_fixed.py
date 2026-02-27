"""
浅色主题实现
完全基于原始代码的样式，不做任何修改
"""
from src.themes.base_theme import BaseTheme


class LightTheme(BaseTheme):
    """浅色主题 - X-Tool 原始样式"""

    THEME_ID = "light"
    THEME_NAME = "浅色主题"
    THEME_DESCRIPTION = "X-Tool 原始样式"

    def get_main_window_style(self) -> str:
        """主窗口样式 - 完全复制原始 main_window.py"""
        return """
            QMainWindow {
                background-color: #f5f6fa;
            }
            QMainWindow::separator {
                background-color: #dcdde1;
                width: 1px;
            }
            QMessageBox {
                background-color: #ffffff;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 13px;
            }
        """

    def get_menubar_style(self) -> str:
        """菜单栏样式 - 完全复制原始"""
        return """
            QMenuBar {
                background-color: #ffffff;
                border-bottom: 1px solid #dcdde1;
                padding: 5px 10px;
                font-family: "Segoe UI", "Microsoft YaHei";
                font-size: 14px;
                color: #2f3640;
            }
            QMenuBar::item {
                background: transparent;
                padding: 4px 10px;
                margin-right: 5px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #f1f2f6;
                color: #3498db;
            }
        """

    def get_menu_style(self) -> str:
        """菜单样式 - 完全复制原始"""
        return """
            QMenu {
                background-color: #ffffff;
                border: 1px solid #dcdde1;
                padding: 5px;
                border-radius: 6px;
            }
            QMenu::item {
                padding: 8px 25px 8px 20px;
                border-radius: 4px;
                margin: 2px;
                font-size: 13px;
                color: #2f3640;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background: #f1f2f6;
                margin: 5px 10px;
            }
        """

    def get_plugin_container_style(self) -> str:
        """插件容器样式 - 完全复制原始 plugin_manager.py"""
        return """
            QWidget {
                background-color: transparent;
                color: #2f3640;
                font-family: "Segoe UI", "Microsoft YaHei";
                font-size: 14px;
            }
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                border: 1px solid #dcdde1;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
            QLabel {
                color: #636e72;
            }
            QLineEdit, QComboBox, QSpinBox, QTextEdit {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                padding: 6px 10px;
                background-color: #ffffff;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {
                border: 1px solid #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1e3799;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(0, 0, 0, 0.05);
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #95a5a6;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #7f8c8d;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                border: none;
                background: rgba(0, 0, 0, 0.05);
                height: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal {
                background: #95a5a6;
                min-width: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #7f8c8d;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """

    def get_tree_widget_style(self) -> str:
        """树形控件样式 - 基础样式"""
        return """
            QTreeWidget {
                background-color: #ffffff;
                border: none;
                outline: none;
                font-size: 14px;
            }
            QTreeWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QTreeWidget::item:hover {
                background-color: #f1f2f6;
            }
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
        """

    def get_stacked_widget_style(self) -> str:
        """堆栈部件样式"""
        return """
            QStackedWidget {
                background-color: #f5f6fa;
                border: none;
            }
        """

    def get_splitter_style(self) -> str:
        """分割器样式 - 完全复制原始"""
        return """
            QSplitter::handle {
                background-color: #dcdde1;
            }
            QSplitter::handle:horizontal {
                width: 1px;
            }
        """

    def get_colors(self) -> dict:
        """获取主题颜色字典"""
        return {}

    # 以下是基类要求的方法，暂时返回空字符串
    def get_button_style(self, style_type: str = "primary") -> str:
        return ""

    def get_input_style(self) -> str:
        return ""

    def get_groupbox_style(self) -> str:
        return ""

    def get_scrollbar_style(self) -> str:
        return ""

    def get_tooltip_style(self) -> str:
        return ""
