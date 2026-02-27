"""
最简单的主题系统
只复制原始样式，不做任何修改
"""


class SimpleTheme:
    """简单主题 - 完全复制原始代码中的样式"""

    @staticmethod
    def get_plugin_style():
        """
        插件样式 - 完全复制自 plugin_manager.py
        一字不改，确保100%一致
        """
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

    @staticmethod
    def get_main_window_style():
        """
        主窗口样式 - 完全复制自 main_window.py
        """
        return """
            QMainWindow {
                background-color: #f5f6fa;
            }
            QMainWindow::separator {
                background-color: #dcdde1;
                width: 1px;
            }
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
            QSplitter::handle {
                background-color: #dcdde1;
            }
            QSplitter::handle:horizontal {
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
