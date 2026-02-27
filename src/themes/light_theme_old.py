"""
浅色主题实现
基于当前 X-Tool 的默认视觉风格
"""
from src.themes.base_theme import BaseTheme, ThemeColors


class LightTheme(BaseTheme):
    """浅色主题 - X-Tool 默认主题"""

    THEME_ID = "light"
    THEME_NAME = "浅色主题"
    THEME_DESCRIPTION = "清爽简洁的浅色界面风格"

    # 颜色定义
    COLORS = {
        # 背景色
        "bg_main": "#f5f6fa",           # 主背景
        "bg_widget": "#ffffff",         # 控件背景
        "bg_sidebar": "#ffffff",        # 侧边栏背景
        "bg_input": "#ffffff",          # 输入框背景
        "bg_disabled": "#f1f2f6",       # 禁用状态背景

        # 文本色
        "text_primary": "#2f3640",      # 主要文字
        "text_secondary": "#636e72",    # 次要文字
        "text_disabled": "#b2bec3",     # 禁用文字
        "text_inverse": "#ffffff",      # 反色文字（白字）

        # 边框色
        "border_default": "#dcdde1",    # 默认边框
        "border_focus": "#3498db",      # 聚焦边框
        "border_hover": "#bdc3c7",      # 悬停边框

        # 功能色
        "primary": ThemeColors.PRIMARY,
        "primary_hover": ThemeColors.PRIMARY_HOVER,
        "primary_pressed": ThemeColors.PRIMARY_PRESSED,
        "success": ThemeColors.SUCCESS,
        "success_hover": ThemeColors.SUCCESS_HOVER,
        "warning": ThemeColors.WARNING,
        "warning_hover": ThemeColors.WARNING_HOVER,
        "danger": ThemeColors.DANGER,
        "danger_hover": ThemeColors.DANGER_HOVER,
        "info": ThemeColors.INFO,
        "info_hover": ThemeColors.INFO_HOVER,
    }

    def get_colors(self) -> dict:
        """获取主题颜色字典"""
        return self.COLORS.copy()

    def get_main_window_style(self) -> str:
        """主窗口样式"""
        return f"""
            QMainWindow {{
                background-color: {self.COLORS['bg_main']};
            }}
            QMainWindow::separator {{
                background-color: {self.COLORS['border_default']};
                width: 1px;
            }}
            QMessageBox {{
                background-color: {self.COLORS['bg_widget']};
            }}
        """

    def get_menubar_style(self) -> str:
        """菜单栏样式"""
        return f"""
            QMenuBar {{
                background-color: {self.COLORS['bg_widget']};
                border-bottom: 1px solid {self.COLORS['border_default']};
                padding: 5px 10px;
                font-family: "Segoe UI", "Microsoft YaHei";
                font-size: 14px;
                color: {self.COLORS['text_primary']};
            }}
            QMenuBar::item {{
                background: transparent;
                padding: 4px 10px;
                margin-right: 5px;
                border-radius: 4px;
            }}
            QMenuBar::item:selected {{
                background-color: #f1f2f6;
                color: {self.COLORS['primary']};
            }}
        """

    def get_menu_style(self) -> str:
        """下拉菜单样式"""
        return f"""
            QMenu {{
                background-color: {self.COLORS['bg_widget']};
                border: 1px solid {self.COLORS['border_default']};
                padding: 5px;
                border-radius: 6px;
            }}
            QMenu::item {{
                padding: 8px 25px 8px 20px;
                border-radius: 4px;
                margin: 2px;
                font-size: 13px;
                color: {self.COLORS['text_primary']};
            }}
            QMenu::item:selected {{
                background-color: {self.COLORS['primary']};
                color: {self.COLORS['text_inverse']};
            }}
            QMenu::separator {{
                height: 1px;
                background: #f1f2f6;
                margin: 5px 10px;
            }}
        """

    def get_button_style(self, style_type: str = "primary") -> str:
        """
        按钮样式
        :param style_type: 按钮类型
        """
        color_map = {
            "primary": (self.COLORS['primary'], self.COLORS['primary_hover'], self.COLORS['primary_pressed']),
            "success": (self.COLORS['success'], self.COLORS['success_hover'], "#229954"),
            "warning": (self.COLORS['warning'], self.COLORS['warning_hover'], "#d35400"),
            "danger": (self.COLORS['danger'], self.COLORS['danger_hover'], "#c0392b"),
            "info": (self.COLORS['info'], self.COLORS['info_hover'], "#636e72"),
        }

        if style_type not in color_map:
            style_type = "primary"

        normal, hover, pressed = color_map[style_type]

        return f"""
            QPushButton[buttonType="{style_type}"] {{
                background-color: {normal};
                color: {self.COLORS['text_inverse']};
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }}
            QPushButton[buttonType="{style_type}"]:hover {{
                background-color: {hover};
            }}
            QPushButton[buttonType="{style_type}"]:pressed {{
                background-color: {pressed};
            }}
        """

    def get_input_style(self) -> str:
        """输入框样式"""
        return f"""
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit {{
                border: 1px solid {self.COLORS['border_default']};
                border-radius: 4px;
                padding: 6px 10px;
                background-color: {self.COLORS['bg_input']};
                color: {self.COLORS['text_primary']};
                font-size: 14px;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
            QDoubleSpinBox:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border: 1px solid {self.COLORS['border_focus']};
            }}
            QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled,
            QDoubleSpinBox:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
                background-color: {self.COLORS['bg_disabled']};
                color: {self.COLORS['text_disabled']};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 5px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {self.COLORS['text_secondary']};
                width: 0;
                height: 0;
            }}
        """

    def get_groupbox_style(self) -> str:
        """分组框样式"""
        return f"""
            QGroupBox {{
                font-size: 16px;
                font-weight: bold;
                color: {self.COLORS['text_primary']};
                border: 2px solid {self.COLORS['border_default']};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """

    def get_scrollbar_style(self) -> str:
        """滚动条样式"""
        return f"""
            QScrollBar:vertical {{
                border: none;
                background: rgba(0, 0, 0, 0.05);
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.COLORS['info']};
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {self.COLORS['info_hover']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::horizontal {{
                border: none;
                background: rgba(0, 0, 0, 0.05);
                height: 8px;
                margin: 0px;
                border-radius: 4px;
            }}
            QScrollBar::handle:horizontal {{
                background: {self.COLORS['info']};
                min-width: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {self.COLORS['info_hover']};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """

    def get_plugin_container_style(self) -> str:
        """插件容器样式 - 完全复制原始样式"""
        return f"""
            QWidget {{
                background-color: transparent;
                color: #2f3640;
                font-family: "Segoe UI", "Microsoft YaHei";
                font-size: 14px;
            }}
            QGroupBox {{
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                border: 1px solid #dcdde1;
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
                color: #636e72;
            }}
            QLineEdit, QComboBox, QSpinBox, QTextEdit {{
                border: 1px solid #dcdde1;
                border-radius: 4px;
                padding: 6px 10px;
                background-color: #ffffff;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {{
                border: 1px solid #3498db;
            }}
            QPushButton {{
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
            QPushButton:pressed {{
                background-color: #1e3799;
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
                background: #95a5a6;
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #7f8c8d;
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
                background: #95a5a6;
                min-width: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: #7f8c8d;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """

    def get_splitter_style(self) -> str:
        """分割器样式"""
        return f"""
            QSplitter::handle {{
                background-color: {self.COLORS['border_default']};
            }}
            QSplitter::handle:horizontal {{
                width: 1px;
            }}
            QSplitter::handle:vertical {{
                height: 1px;
            }}
        """

    def get_stacked_widget_style(self) -> str:
        """堆栈部件样式"""
        return f"""
            QStackedWidget {{
                background-color: {self.COLORS['bg_main']};
                border: none;
            }}
        """

    def get_tree_widget_style(self) -> str:
        """树形控件样式"""
        return f"""
            QTreeWidget {{
                background-color: {self.COLORS['bg_sidebar']};
                border: none;
                outline: none;
                font-size: 14px;
            }}
            QTreeWidget::item {{
                padding: 8px;
                border-radius: 4px;
            }}
            QTreeWidget::item:hover {{
                background-color: #f1f2f6;
            }}
            QTreeWidget::item:selected {{
                background-color: {self.COLORS['primary']};
                color: {self.COLORS['text_inverse']};
            }}
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {{
                image: none;
                border: none;
            }}
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {{
                image: none;
                border: none;
            }}
        """

    def get_tooltip_style(self) -> str:
        """工具提示样式"""
        return f"""
            QToolTip {{
                background-color: #2c3e50;
                color: {self.COLORS['text_inverse']};
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 12px;
            }}
        """