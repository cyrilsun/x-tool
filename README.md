### 插件开发
plugins目录下开发插件，每个插件为一个独立的.py文件。基础结构如下：
```python
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton
from src.plugins.base_plugin import BasePlugin

class MyNewPlugin(BasePlugin):
    def __init__(self):
        super().__init__("我的新插件", "这是一个新插件的描述")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("这是我的新插件内容")
        layout.addWidget(label)

        button = QPushButton("点击测试")
        button.clicked.connect(self.on_button_clicked)
        layout.addWidget(button)

    def on_button_clicked(self):
        print("插件按钮被点击了！")

    def get_widget(self) -> "MyNewPlugin":
        return self

    def on_activate(self):
        print("我的新插件被激活了！")
```
