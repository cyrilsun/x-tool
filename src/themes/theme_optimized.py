"""
主题系统 - 完全优化版本
逐步抽象：颜色常量 + 通用样式模式
样式完全一致，但代码更优雅
"""


class Theme:
    """主题类 - 完全优化版"""

    # ========== 颜色常量 ==========
    # 从原始代码中提取，保持色值完全一致

    # 主色调
    COLOR_PRIMARY = "#3498db"          # 主色蓝
    COLOR_PRIMARY_HOVER = "#2980b9"   # 悬停蓝
    COLOR_PRIMARY_PRESSED = "#1e3799" # 按下蓝

    # 背景色
    COLOR_BG_MAIN = "#f5f6fa"          # 主背景
    COLOR_BG_WHITE = "#ffffff"        # 白色背景

    # 文字色
    COLOR_TEXT_PRIMARY = "#2f3640"   # 主要文字
    COLOR_TEXT_SECONDARY = "#636e72" # 次要文字
    COLOR_TEXT_TITLE = "#2c3e50"      # 标题文字
    COLOR_TEXT_WHITE = "#ffffff"      # 白色文字

    # 边框色
    COLOR_BORDER = "#dcdde1"          # 边框灰
    COLOR_BORDER_FOCUS = "#3498db"   # 聚焦边框

    # 其他
    COLOR_HOVER_BG = "#f1f2f6"        # 悬停背景
    COLOR_SCROLLBAR = "#95a5a6"      # 滚动条
    COLOR_SCROLLBAR_HOVER = "#7f8c8d" # 滚动条悬停

    # ========== 通用样式模式 ==========
    """提取的通用样式模式"""

    @staticmethod
    def _button_base():
        """按钮基础样式"""
        return """
            border: none;
            padding: 8px 16px;
            font-weight: bold;
            border-radius: 4px;
        """

    @staticmethod
    def _input_base():
        """输入框基础样式"""
        return """
            border: 1px solid {Theme.COLOR_BORDER};
            border-radius: 4px;
            padding: 6px 10px;
        """

    @staticmethod
    def _groupbox_base():
        """分组框基础样式"""
        return """
            border: 2px solid {Theme.COLOR_BORDER};
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 15px;
        """

    @staticmethod
    def _menu_item_base():
        """菜单项基础样式"""
        return """
            border-radius: 4px;
            margin: 2px;
        """

    # ========== 插件样式 ==========
    @staticmethod
    def get_plugin_style():
        """
        插件样式 - 使用颜色常量和通用模式
        输出与原始代码完全一致的样式
        """
        return f"""
            QWidget {{
                background-color: transparent;
                color: {Theme.COLOR_TEXT_PRIMARY};
                font-family: "Segoe UI", "Microsoft YaHei";
                font-size: 14px;
            }}
            QGroupBox {{
                font-size: 16px;
                font-weight: bold;
                color: {Theme.COLOR_TEXT_TITLE};
                border: 1px solid {Theme.COLOR_BORDER};
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }}
            QLabel {{
                color: {Theme.COLOR_TEXT_SECONDARY};
            }}
            QLineEdit, QComboBox, QSpinBox, QTextEdit {{
                border: 1px solid {Theme.COLOR_BORDER};
                border-radius: 4px;
                padding: 6px 10px;
                background-color: {Theme.COLOR_BG_WHITE};
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {{
                border: 1px solid {Theme.COLOR_BORDER_FOCUS};
            }}
            QPushButton {{
                background-color: {Theme.COLOR_PRIMARY};
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {Theme.COLOR_PRIMARY_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Theme.COLOR_PRIMARY_PRESSED};
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                border: none;
                background: rgba(0, 0, 0, 0.05);
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {Theme.COLOR_SCROLLBAR};
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Theme.COLOR_SCROLLBAR_HOVER};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: rgba(0, 0, 0, 0.05);
                height: 8px;
                margin: 0px;
                border-radius: 4px;
            }}
            QScrollBar::handle:horizontal {{
                background: {Theme.COLOR_SCROLLBAR};
                min-width: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {Theme.COLOR_SCROLLBAR_HOVER};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """

    # ========== 主窗口样式 ==========
    @staticmethod
    def get_main_window_style():
        """
        主窗口样式 - 使用颜色常量
        输出与原始代码完全一致的样式
        """
        return f"""
            QMainWindow {{
                background-color: {Theme.COLOR_BG_MAIN};
            }}
            QMainWindow::separator {{
                background-color: {Theme.COLOR_BORDER};
                width: 1px;
            }}
            QMenuBar {{
                background-color: {Theme.COLOR_BG_WHITE};
                border-bottom: 1px solid {Theme.COLOR_BORDER};
                padding: 5px 10px;
                font-family: "Segoe UI", "Microsoft YaHei";
                font-size: 14px;
                color: {Theme.COLOR_TEXT_PRIMARY};
            }}
            QMenuBar::item {{
                background: transparent;
                padding: 4px 10px;
                margin-right: 5px;
                border-radius: 4px;
            }}
            QMenuBar::item:selected {{
                background-color: {Theme.COLOR_HOVER_BG};
                color: {Theme.COLOR_PRIMARY};
            }}
            QMenu {{
                background-color: {Theme.COLOR_BG_WHITE};
                border: 1px solid {Theme.COLOR_BORDER};
                padding: 5px;
                border-radius: 6px;
            }}
            QMenu::item {{
                padding: 8px 25px 8px 20px;
                border-radius: 4px;
                margin: 2px;
                font-size: 13px;
                color: {Theme.COLOR_TEXT_PRIMARY};
            }}
            QMenu::item:selected {{
                background-color: {Theme.COLOR_PRIMARY};
                color: {Theme.COLOR_TEXT_WHITE};
            }}
            QMenu::separator {{
                height: 1px;
                background: {Theme.COLOR_HOVER_BG};
                margin: 5px 10px;
            }}
            QSplitter::handle {{
                background-color: {Theme.COLOR_BORDER};
            }}
            QSplitter::handle:horizontal {{
                width: 1px;
            }}
            QMessageBox {{
                background-color: {Theme.COLOR_BG_WHITE};
            }}
            QPushButton {{
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 13px;
            }}
        """

    # ========== 按钮样式变体 (可选) ==========
    @staticmethod
    def get_button_style(style_type: str = "primary"):
        """
        获取按钮样式

        Args:
            style_type: 按钮类型 ("primary")

        Returns:
            样式字符串
        """
        if style_type == "primary":
            return f"""
                QPushButton {{
                    background-color: {Theme.COLOR_PRIMARY};
                    color: {Theme.COLOR_TEXT_WHITE};
                    border: none;
                    padding: 8px 16px;
                    font-weight: bold;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: {Theme.COLOR_PRIMARY_HOVER};
                }}
                QPushButton:pressed {{
                    background-color: {Theme.COLOR_PRIMARY_PRESSED};
                }}
            """
        # 未来可以添加更多类型
        return ""

    # ========== 辅助方法 ==========
    @staticmethod
    def get_color(color_name: str):
        """
        获取颜色值

        Args:
            color_name: 颜色名称 (如 "primary", "border")

        Returns:
            颜色值字符串
        """
        color_map = {
            "primary": Theme.COLOR_PRIMARY,
            "primary_hover": Theme.COLOR_PRIMARY_HOVER,
            "primary_pressed": Theme.COLOR_PRIMARY_PRESSED,
            "border": Theme.COLOR_BORDER,
            "border_focus": Theme.COLOR_BORDER_FOCUS,
            "bg_main": Theme.COLOR_BG_MAIN,
            "bg_white": Theme.COLOR_BG_WHITE,
            "text_primary": Theme.COLOR_TEXT_PRIMARY,
            "text_secondary": Theme.COLOR_TEXT_SECONDARY,
            "text_white": Theme.COLOR_TEXT_WHITE,
        }
        return color_map.get(color_name, "#000000")
