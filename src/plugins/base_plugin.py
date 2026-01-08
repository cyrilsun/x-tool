from abc import ABC, abstractmethod

from PyQt6.QtWidgets import QWidget


class _BasePluginMeta(type(QWidget), type(ABC)):
    pass


class BasePlugin(QWidget, ABC, metaclass=_BasePluginMeta):
    def __init__(self, name: str, description: str = ""):
        super().__init__()
        self._name = name
        self._description = description

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @abstractmethod
    def get_widget(self) -> QWidget:
        pass

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass
