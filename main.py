import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

from src.plugins.plugin_loader import PluginLoader, get_plugin_directory
from src.ui.main_window import MainWindow

VERSION = "1.0.0"
VERSION_INFO = """
技术支持：如有问题请联系管理员
"""


def show_about_dialog(parent):
    """显示关于对话框"""
    dialog = QDialog(parent)
    dialog.setWindowTitle("关于 X-Tool")
    dialog.setFixedSize(400, 300)

    layout = QVBoxLayout(dialog)

    title_label = QLabel("X-Tool")
    title_label.setFont(QFont("Microsoft YaHei", 24, QFont.Weight.Bold))
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title_label)

    version_label = QLabel(f"版本: {VERSION}")
    version_label.setFont(QFont("Microsoft YaHei", 14))
    version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(version_label)

    info_label = QLabel(VERSION_INFO)
    info_label.setFont(QFont("Microsoft YaHei", 12))
    info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    info_label.setStyleSheet("color: #666;")
    layout.addWidget(info_label)

    close_btn = QPushButton("确定")
    close_btn.setFont(QFont("Microsoft YaHei", 12))
    close_btn.setFixedWidth(100)
    close_btn.clicked.connect(dialog.accept)

    btn_layout = QHBoxLayout()
    btn_layout.addStretch()
    btn_layout.addWidget(close_btn)
    btn_layout.addStretch()
    layout.addLayout(btn_layout)

    dialog.exec()


def check_update(parent):
    """检查更新"""
    QMessageBox.information(parent, "检查更新", f"当前版本: {VERSION}\n\n已是最新版本，无需更新。")


def load_plugins(window: MainWindow):
    """加载并注册所有插件"""
    plugin_dir = get_plugin_directory()
    loader = PluginLoader(plugin_dir)
    plugins = loader.load_all_plugins()

    for plugin in plugins:
        window.add_tool(plugin.name, plugin)

        plugin.setStyleSheet("""
            QWidget {
                font-size: 16px;
            }
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
            }
            QLabel {
                font-size: 16px;
            }
            QComboBox {
                font-size: 16px;
                padding: 8px;
            }
            QTextEdit {
                font-size: 16px;
            }
            QPushButton {
                font-size: 16px;
                font-weight: bold;
            }
        """)

        plugin.on_activate()

    # 默认显示欢迎页面
    window.on_tool_selected(-1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setApplicationName("X-Tool")
    app.setApplicationDisplayName("X-Tool")
    app.setDesktopFileName("com.xtool.app")
    
    window = MainWindow()
    window.setWindowTitle(f"X-Tool v{VERSION}")

    menubar = window.menuBar()
    help_menu = menubar.addMenu("帮助")

    about_action = help_menu.addAction("关于")
    about_action.triggered.connect(lambda: show_about_dialog(window))

    load_plugins(window)

    # 默认选中首页
    window.tool_list_widget.setCurrentRow(0)

    window.show()

    sys.exit(app.exec())
