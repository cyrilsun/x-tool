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

    # ========== 样式变体颜色 ==========

    # Success (成功/绿色)
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
    COLOR_INFO = "#95a5a6"              # 信息灰
    COLOR_INFO_HOVER = "#7f8c8d"        # 悬停灰
    COLOR_INFO_PRESSED = "#636e72"      # 按下灰

    # Secondary (次要/浅灰)
    COLOR_SECONDARY = "#bdc3c7"         # 次要灰
    COLOR_SECONDARY_HOVER = "#aab7b8"   # 悬停灰
    COLOR_SECONDARY_PRESSED = "#99a3a5" # 按下灰

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

    # ========== 按钮样式变体 ==========
    @staticmethod
    def get_button_style(style_type: str = "primary"):
        """
        获取按钮样式

        Args:
            style_type: 按钮类型
                - "primary": 主按钮 (蓝色)
                - "success": 成功按钮 (绿色)
                - "warning": 警告按钮 (橙色)
                - "danger": 危险按钮 (红色)
                - "info": 信息按钮 (灰色)
                - "secondary": 次要按钮 (浅灰)

        Returns:
            样式字符串
        """
        # 定义颜色映射
        colors = {
            "primary": (Theme.COLOR_PRIMARY, Theme.COLOR_PRIMARY_HOVER, Theme.COLOR_PRIMARY_PRESSED),
            "success": (Theme.COLOR_SUCCESS, Theme.COLOR_SUCCESS_HOVER, Theme.COLOR_SUCCESS_PRESSED),
            "warning": (Theme.COLOR_WARNING, Theme.COLOR_WARNING_HOVER, Theme.COLOR_WARNING_PRESSED),
            "danger": (Theme.COLOR_DANGER, Theme.COLOR_DANGER_HOVER, Theme.COLOR_DANGER_PRESSED),
            "info": (Theme.COLOR_INFO, Theme.COLOR_INFO_HOVER, Theme.COLOR_INFO_PRESSED),
            "secondary": (Theme.COLOR_SECONDARY, Theme.COLOR_SECONDARY_HOVER, Theme.COLOR_SECONDARY_PRESSED),
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

    # ========== 辅助方法 ==========
    @staticmethod
    def get_color(color_name: str):
        """
        获取颜色值

        Args:
            color_name: 颜色名称
                - 基础: "primary", "border", "bg_main", etc.
                - 样式变体: "success", "warning", "danger", "info", "secondary"
                - 悬停状态: "success_hover", "danger_pressed", etc.

        Returns:
            颜色值字符串
        """
        color_map = {
            # 基础颜色
            "primary": Theme.COLOR_PRIMARY,
            "primary_hover": Theme.COLOR_PRIMARY_HOVER,
            "primary_pressed": Theme.COLOR_PRIMARY_PRESSED,
            "border": Theme.COLOR_BORDER,
            "border_focus": Theme.COLOR_BORDER_FOCUS,
            "bg_main": Theme.COLOR_BG_MAIN,
            "bg_white": Theme.COLOR_BG_WHITE,
            "text_primary": Theme.COLOR_TEXT_PRIMARY,
            "text_secondary": Theme.COLOR_TEXT_SECONDARY,
            "text_title": Theme.COLOR_TEXT_TITLE,
            "text_white": Theme.COLOR_TEXT_WHITE,
            "hover_bg": Theme.COLOR_HOVER_BG,

            # Success 变体
            "success": Theme.COLOR_SUCCESS,
            "success_hover": Theme.COLOR_SUCCESS_HOVER,
            "success_pressed": Theme.COLOR_SUCCESS_PRESSED,

            # Warning 变体
            "warning": Theme.COLOR_WARNING,
            "warning_hover": Theme.COLOR_WARNING_HOVER,
            "warning_pressed": Theme.COLOR_WARNING_PRESSED,

            # Danger 变体
            "danger": Theme.COLOR_DANGER,
            "danger_hover": Theme.COLOR_DANGER_HOVER,
            "danger_pressed": Theme.COLOR_DANGER_PRESSED,

            # Info 变体
            "info": Theme.COLOR_INFO,
            "info_hover": Theme.COLOR_INFO_HOVER,
            "info_pressed": Theme.COLOR_INFO_PRESSED,

            # Secondary 变体
            "secondary": Theme.COLOR_SECONDARY,
            "secondary_hover": Theme.COLOR_SECONDARY_HOVER,
            "secondary_pressed": Theme.COLOR_SECONDARY_PRESSED,
        }
        return color_map.get(color_name, "#000000")
