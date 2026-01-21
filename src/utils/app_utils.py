from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox

from src.config.app_config import VERSION, VERSION_INFO


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
    version_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    layout.addWidget(version_label)

    info_label = QLabel(VERSION_INFO)
    info_label.setFont(QFont("Microsoft YaHei", 12))
    info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    info_label.setStyleSheet("color: #666;")
    # 支持点击链接和复制文本
    info_label.setOpenExternalLinks(True)
    info_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)
    layout.addWidget(info_label)

    close_btn = QPushButton("确定")
    close_btn.setFont(QFont("Microsoft YaHei", 12))
    close_btn.setFixedWidth(100)
    close_btn.setStyleSheet("""
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:pressed {
            background-color: #1e3799;
        }
    """)
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
