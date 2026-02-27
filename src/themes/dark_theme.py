"""
深色主题 - 深色配色方案
"""

class DarkTheme:
    """深色主题类"""

    # ========== 颜色常量 - 深色配色 ==========
    # 深色主题使用深色背景和浅色文字

    # 主色调
    COLOR_PRIMARY = "#5dade2"          # 主色蓝（稍亮，适应深色背景）
    COLOR_PRIMARY_HOVER = "#3498db"   # 悬停蓝
    COLOR_PRIMARY_PRESSED = "#2980b9" # 按下蓝

    # 背景色 - 深色
    COLOR_BG_MAIN = "#1e1e1e"          # 主背景（深灰）
    COLOR_BG_WHITE = "#2d2d2d"        # 次背景（稍浅）

    # 文字色 - 浅色
    COLOR_TEXT_PRIMARY = "#e0e0e0"   # 主要文字（浅灰）
    COLOR_TEXT_SECONDARY = "#a0a0a0" # 次要文字（中灰）
    COLOR_TEXT_TITLE = "#ffffff"      # 标题文字（白色）
    COLOR_TEXT_WHITE = "#ffffff"      # 白色文字

    # 边框色
    COLOR_BORDER = "#404040"          # 边框灰（深色）
    COLOR_BORDER_FOCUS = "#5dade2"   # 聚焦边框（主色）

    # 其他
    COLOR_HOVER_BG = "#3d3d3d"        # 悬停背景
    COLOR_SCROLLBAR = "#808080"      # 滚动条（更亮，在深色背景可见）
    COLOR_SCROLLBAR_HOVER = "#909090" # 滚动条悬停

    # ========== 样式变体颜色 ==========

    # Success (成功/绿色) - 深色主题调整
    COLOR_SUCCESS = "#27ae60"           # 成功绿
    COLOR_SUCCESS_HOVER = "#229954"     # 悬停绿
    COLOR_SUCCESS_PRESSED = "#1e8449"   # 按下绿

    # Warning (警告/黄色)
    COLOR_WARNING = "#f39c12"           # 警告橙
    COLOR_WARNING_HOVER = "#e67e22"     # 悬停橙
    COLOR_WARNING_PRESSED = "#d35400"   # 按下橙

    # Danger (危险/红色)
    COLOR_DANGER = "#e74c3c"            # 危险红
    COLOR_DANGER_HOVER = "#c0392b"      # 悬停红
    COLOR_DANGER_PRESSED = "#a93226"    # 按下红

    # Info (信息/灰色)
    COLOR_INFO = "#7f8c8d"              # 信息灰（稍亮）
    COLOR_INFO_HOVER = "#95a5a6"        # 悬停灰
    COLOR_INFO_PRESSED = "#636e72"      # 按下灰

    # Secondary (次要/浅灰)
    COLOR_SECONDARY = "#5d6d7e"         # 次要灰（稍亮）
    COLOR_SECONDARY_HOVER = "#707b7c"   # 悬停灰
    COLOR_SECONDARY_PRESSED = "#566573" # 按下灰

    # ========== 样式方法 ==========

    @staticmethod
    def get_plugin_style():
        """
        插件样式 - 深色版本
        """
        return f"""
            QWidget {{
                background-color: transparent;
                color: {DarkTheme.COLOR_TEXT_PRIMARY};
                font-family: "Segoe UI", "Microsoft YaHei";
                font-size: 14px;
            }}
            QGroupBox {{
                font-size: 16px;
                font-weight: bold;
                color: {DarkTheme.COLOR_TEXT_TITLE};
                border: 1px solid {DarkTheme.COLOR_BORDER};
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
                color: {DarkTheme.COLOR_TEXT_SECONDARY};
            }}
            QLineEdit, QComboBox, QSpinBox, QTextEdit {{
                border: 1px solid {DarkTheme.COLOR_BORDER};
                border-radius: 4px;
                padding: 6px 10px;
                background-color: {DarkTheme.COLOR_BG_WHITE};
                color: {DarkTheme.COLOR_TEXT_PRIMARY};
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {{
                border: 1px solid {DarkTheme.COLOR_BORDER_FOCUS};
            }}
            QPushButton {{
                background-color: {DarkTheme.COLOR_PRIMARY};
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {DarkTheme.COLOR_PRIMARY_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {DarkTheme.COLOR_PRIMARY_PRESSED};
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                border: none;
                background: rgba(255, 255, 255, 0.05);
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {DarkTheme.COLOR_SCROLLBAR};
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {DarkTheme.COLOR_SCROLLBAR_HOVER};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: rgba(255, 255, 255, 0.05);
                height: 8px;
                margin: 0px;
                border-radius: 4px;
            }}
            QScrollBar::handle:horizontal {{
                background: {DarkTheme.COLOR_SCROLLBAR};
                min-width: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {DarkTheme.COLOR_SCROLLBAR_HOVER};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """

    @staticmethod
    def get_main_window_style():
        """
        主窗口样式 - 深色版本
        """
        return f"""
            QMainWindow {{
                background-color: {DarkTheme.COLOR_BG_MAIN};
            }}
            QMainWindow::separator {{
                background-color: {DarkTheme.COLOR_BORDER};
                width: 1px;
            }}
            QMenuBar {{
                background-color: {DarkTheme.COLOR_BG_WHITE};
                border-bottom: 1px solid {DarkTheme.COLOR_BORDER};
                padding: 5px 10px;
                font-family: "Segoe UI", "Microsoft YaHei";
                font-size: 14px;
                color: {DarkTheme.COLOR_TEXT_PRIMARY};
            }}
            QMenuBar::item {{
                background: transparent;
                padding: 4px 10px;
                margin-right: 5px;
                border-radius: 4px;
            }}
            QMenuBar::item:selected {{
                background-color: {DarkTheme.COLOR_HOVER_BG};
                color: {DarkTheme.COLOR_PRIMARY};
            }}
            QMenu {{
                background-color: {DarkTheme.COLOR_BG_WHITE};
                border: 1px solid {DarkTheme.COLOR_BORDER};
                padding: 5px;
                border-radius: 6px;
            }}
            QMenu::item {{
                padding: 8px 25px 8px 20px;
                border-radius: 4px;
                margin: 2px;
                font-size: 13px;
                color: {DarkTheme.COLOR_TEXT_PRIMARY};
            }}
            QMenu::item:selected {{
                background-color: {DarkTheme.COLOR_PRIMARY};
                color: white;
            }}
            QMenu::separator {{
                height: 1px;
                background: {DarkTheme.COLOR_HOVER_BG};
                margin: 5px 10px;
            }}
            QSplitter::handle {{
                background-color: {DarkTheme.COLOR_BORDER};
            }}
            QSplitter::handle:horizontal {{
                width: 1px;
            }}
            QMessageBox {{
                background-color: {DarkTheme.COLOR_BG_WHITE};
            }}
            QPushButton {{
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 13px;
            }}
        """

    @staticmethod
    def get_button_style(style_type: str = "primary"):
        """
        获取按钮样式

        Args:
            style_type: 按钮类型

        Returns:
            样式字符串
        """
        # 定义颜色映射
        colors = {
            "primary": (DarkTheme.COLOR_PRIMARY, DarkTheme.COLOR_PRIMARY_HOVER, DarkTheme.COLOR_PRIMARY_PRESSED),
            "success": (DarkTheme.COLOR_SUCCESS, DarkTheme.COLOR_SUCCESS_HOVER, DarkTheme.COLOR_SUCCESS_PRESSED),
            "warning": (DarkTheme.COLOR_WARNING, DarkTheme.COLOR_WARNING_HOVER, DarkTheme.COLOR_WARNING_PRESSED),
            "danger": (DarkTheme.COLOR_DANGER, DarkTheme.COLOR_DANGER_HOVER, DarkTheme.COLOR_DANGER_PRESSED),
            "info": (DarkTheme.COLOR_INFO, DarkTheme.COLOR_INFO_HOVER, DarkTheme.COLOR_INFO_PRESSED),
            "secondary": (DarkTheme.COLOR_SECONDARY, DarkTheme.COLOR_SECONDARY_HOVER, DarkTheme.COLOR_SECONDARY_PRESSED),
        }

        if style_type not in colors:
            style_type = "primary"

        bg_color, hover_color, pressed_color = colors[style_type]

        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
        """
