from src.plugins.base_plugin import BasePlugin
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton


class TestPlugin(BasePlugin):
    def __init__(self):
        super().__init__("测试插件", "这是一个测试插件")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("这是一个测试插件")
        layout.addWidget(label)
        
        button = QPushButton("测试按钮")
        button.clicked.connect(self.on_button_clicked)
        layout.addWidget(button)

    def on_button_clicked(self):
        print("测试按钮被点击了！")

    def get_widget(self):
        return self

    def on_activate(self):
        print("测试插件被激活了！")

    def on_deactivate(self):
        print("测试插件被停用了！")
