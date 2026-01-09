from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton
from src.plugins.base_plugin import BasePlugin

class TestPlugin(BasePlugin):
    def __init__(self):
        super().__init__("测试插件", "这是一个测试插件的描述")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("这是我的测试插件内容")
        layout.addWidget(label)

        button = QPushButton("点击测试")
        button.clicked.connect(self.on_button_clicked)
        layout.addWidget(button)

    def on_button_clicked(self):
        print("测试插件按钮被点击了！")

    def get_widget(self) -> "TestPlugin":
        return self

    def on_activate(self):
        print("测试插件被激活了！")