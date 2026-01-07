import sys

from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMenuBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.tools.work_order_tool import WorkOrderTool
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

    # check_update_action = help_menu.addAction("检查更新")
    # check_update_action.triggered.connect(lambda: check_update(window))

    work_order_tool = WorkOrderTool()
    work_order_tool.setStyleSheet("""
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
    window.add_tool("回头看工单", work_order_tool)

    window.show()

    sys.exit(app.exec())
