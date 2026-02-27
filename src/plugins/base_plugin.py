"""
X-Tool 插件基类模块

提供标准化的插件基类，定义插件接口规范。
所有插件必须继承 BasePlugin 并实现其抽象方法。
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QGroupBox, QScrollArea, QFrame, QTextEdit, QPlainTextEdit
)

from src.themes.theme import Theme
from src.utils.logger import logger


class _BasePluginMeta(type(QWidget), type(ABC)):
    """元类，解决多继承冲突"""
    pass


class BasePlugin(QWidget, ABC, metaclass=_BasePluginMeta):
    """
    插件基类

    所有插件必须继承此类并实现抽象方法。

    插件元数据 (PLUGIN_INFO):
        - name: 插件名称
        - description: 插件描述
        - version: 版本号 (默认: "1.0.0")
        - author: 作者 (可选)
        - category: 分类 (可选)
        - icon: 图标名 (可选)

    生命周期:
        __init__ -> _setup_ui -> on_init -> on_activate -> [运行] -> on_deactivate
    """

    # ========== 插件元数据 ==========
    # 子类可以覆盖这些类属性，或在 __init__ 中提供
    PLUGIN_INFO: Dict[str, Any] = {
        "name": "",
        "description": "",
        "version": "1.0.0",
        "author": "",
        "category": "",
        "icon": "",
    }

    def __init__(self, name: str = "", description: str = ""):
        """
        初始化插件

        Args:
            name: 插件名称（优先级高于 PLUGIN_INFO）
            description: 插件描述（优先级高于 PLUGIN_INFO）
        """
        super().__init__()

        # 合并元数据：构造函数参数 > 类属性
        plugin_info = self.PLUGIN_INFO.copy()
        self._name = name or plugin_info.get("name", "")
        self._description = description or plugin_info.get("description", "")
        self._version = plugin_info.get("version", "1.0.0")
        self._author = plugin_info.get("author", "")
        self._category = plugin_info.get("category", "")
        self._icon = plugin_info.get("icon", "")

        # 工作目录（用于文件对话框等）
        self.last_dir = ""

        # 主布局引用
        self._main_layout = None
        self._scroll_area = None
        self._content_widget = None
        self._content_layout = None

        # 跟踪状态
        self._is_activated = False
        self._finalized = False  # 标记是否已执行UI后处理

        # 自动设置统一的滚动条布局结构
        self._setup_default_layout()

        # 延迟执行：在所有UI组件创建完成后自动禁用内部滚动条
        # 使用单次定时器确保在子类_setup_ui()完成后执行
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, self._auto_disable_inner_scrollbars)

    # ========== 元数据属性 ==========
    @property
    def name(self) -> str:
        """插件名称"""
        return self._name

    @property
    def description(self) -> str:
        """插件描述"""
        return self._description

    @property
    def version(self) -> str:
        """插件版本"""
        return self._version

    @property
    def author(self) -> str:
        """插件作者"""
        return self._author

    @property
    def category(self) -> str:
        """插件分类"""
        return self._category

    @property
    def icon(self) -> str:
        """插件图标名"""
        return self._icon

    # ========== 抽象方法（必须实现）==========
    @abstractmethod
    def get_widget(self) -> QWidget:
        """
        返回插件的主 Widget

        Returns:
            插件的主界面 QWidget 实例
        """
        pass

    # ========== 可选生命周期方法 ==========

    def _auto_disable_inner_scrollbars(self):
        """
        自动禁用所有 QTextEdit 和 QPlainTextEdit 的内部滚动条

        使用外层插件滚动条，避免出现双滚动条。
        在插件初始化完成后通过定时器自动调用。
        """
        if self._finalized:
            return  # 避免重复执行

        # 递归查找所有 QTextEdit 和 QPlainTextEdit 并禁用滚动条
        def disable_scrollbars_in_widget(widget):
            if widget is None:
                return

            # 检查当前 widget
            if isinstance(widget, (QTextEdit, QPlainTextEdit)):
                widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

            # 递归处理子组件
            for child in widget.findChildren(QWidget):
                if isinstance(child, (QTextEdit, QPlainTextEdit)):
                    child.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                    child.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # 从 self 开始处理
        disable_scrollbars_in_widget(self)

        self._finalized = True

    def on_init(self):
        """
        插件初始化回调（在 _setup_ui 之后调用）
        可以在这里进行额外的初始化操作
        """
        pass

    def on_activate(self):
        """
        插件激活回调（用户点击打开插件时调用）
        """
        self._is_activated = True
        logger.info(f"插件 '{self.name}' 被激活")

    def on_deactivate(self):
        """
        插件停用回调（用户切换到其他插件时调用）
        """
        self._is_activated = False
        logger.info(f"插件 '{self.name}' 被停用")

    def on_theme_changed(self, is_dark: bool):
        """
        主题切换回调

        Args:
            is_dark: 是否为深色主题
        """
        # 默认实现：重新应用样式
        # 子类可以覆盖此方法实现自定义主题处理
        pass

    # ========== UI 辅助方法 ==========

    def _setup_default_layout(self):
        """
        自动设置默认的统一布局结构（带滚动条）

        在插件初始化时自动调用，确保所有插件都有统一的滚动条样式。
        """
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        # 创建滚动区域
        self._scroll_area = QScrollArea(self)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # 创建内容容器
        self._content_widget = QWidget()
        self._content_widget.setObjectName("pluginContainer")

        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(20, 20, 20, 20)
        self._content_layout.setSpacing(20)

        self._scroll_area.setWidget(self._content_widget)
        self._main_layout.addWidget(self._scroll_area)

    def get_content_layout(self) -> QVBoxLayout:
        """
        获取内容区域的布局

        插件可以直接使用此布局添加组件，无需手动创建滚动条结构。

        Returns:
            内容区域的 QVBoxLayout

        Example:
            def _setup_ui(self):
                layout = self.get_content_layout()
                layout.addWidget(QLabel("Hello"))
        """
        return self._content_layout

    def setup_standard_layout(self):
        """
        设置标准布局结构

        已在 __init__ 中自动创建，此方法为了向后兼容保留。
        推荐直接使用 get_content_layout() 获取布局。

        Returns:
            content_layout: 内容区域的 QVBoxLayout
        """
        return self._content_layout

    def create_group_box(self, title: str) -> QGroupBox:
        """
        创建标准样式的分组框

        Args:
            title: 分组框标题

        Returns:
            QGroupBox 实例（已应用主题样式）
        """
        group = QGroupBox(title)
        # 不设置内联样式，由主题系统统一管理
        return group

    def create_text_edit(self, placeholder: str = "", read_only: bool = False) -> QTextEdit:
        """
        创建标准样式的文本编辑器（无内部滚动条）

        内部滚动条已禁用，使用外层插件滚动条。

        Args:
            placeholder: 占位符文本
            read_only: 是否只读

        Returns:
            QTextEdit 实例
        """
        text_edit = QTextEdit()
        if placeholder:
            text_edit.setPlaceholderText(placeholder)
        text_edit.setReadOnly(read_only)

        # 禁用垂直和水平滚动条，使用外层滚动
        text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        return text_edit

    def create_plain_text_edit(self, placeholder: str = "", read_only: bool = False) -> QPlainTextEdit:
        """
        创建标准样式的纯文本编辑器（无内部滚动条）

        内部滚动条已禁用，使用外层插件滚动条。

        Args:
            placeholder: 占位符文本
            read_only: 是否只读

        Returns:
            QPlainTextEdit 实例
        """
        text_edit = QPlainTextEdit()
        if placeholder:
            text_edit.setPlaceholderText(placeholder)
        text_edit.setReadOnly(read_only)

        # 禁用垂直和水平滚动条，使用外层滚动
        text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        return text_edit

    def create_button(self, text: str, style_type: str = "primary") -> QPushButton:
        """
        创建标准样式的按钮

        Args:
            text: 按钮文本
            style_type: 按钮样式类型 (primary/success/warning/danger/info/secondary)

        Returns:
            QPushButton 实例（已应用主题样式）
        """
        btn = QPushButton(text)
        # 样式由主题系统统一管理
        btn.setProperty("styleType", style_type)
        return btn

    def create_description_section(self, html_content: str) -> tuple:
        """
        创建可折叠的插件说明区域（自动包含元数据）

        Args:
            html_content: 说明内容的 HTML 文本

        Returns:
            (header_layout, content_text, toggle_btn, scroll_area)
        """
        # 标题行
        header_layout = QHBoxLayout()
        title_label = QLabel("<h3 style='margin: 0;'>插件说明</h3>")

        toggle_btn = QPushButton("▼ 展开")
        toggle_btn.setProperty("styleType", "secondary")

        toggle_btn.clicked.connect(lambda: self._toggle_description(
            scroll_area, toggle_btn, expanded_height=180
        ))

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(toggle_btn)

        # 构建完整内容（元数据 + 说明）
        full_content = self._build_description_content(html_content)

        # 内容区域
        content_text = QTextEdit()
        content_text.setReadOnly(True)
        content_text.setHtml(full_content)

        scroll_area = QScrollArea()
        scroll_area.setWidget(content_text)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setFixedHeight(50)  # 默认收起状态

        return header_layout, content_text, toggle_btn, scroll_area

    def _build_description_content(self, html_content: str) -> str:
        """
        构建包含元数据的完整说明内容

        Args:
            html_content: 原始说明内容

        Returns:
            完整的 HTML 内容（包含元数据）
        """
        # 构建元数据 HTML
        metadata_parts = []
        if self.version:
            metadata_parts.append(f"<strong>版本:</strong> {self.version}")
        if self.author:
            metadata_parts.append(f"<strong>作者:</strong> {self.author}")
        if self.category:
            metadata_parts.append(f"<strong>分类:</strong> {self.category}")

        # 检查当前是否为深色主题
        from src.themes.simple_theme_manager import get_theme_manager
        is_dark = get_theme_manager().is_dark_mode()

        # 根据主题选择背景色
        bg_color = "#4e5254" if is_dark else "#f1f2f6"
        text_color = "#a9b7c6" if is_dark else "#2c3e50"

        metadata_html = ""
        if metadata_parts:
            metadata_html = f"""
                <div style='background-color: {bg_color}; padding: 8px 12px; border-radius: 4px; margin-bottom: 12px; font-size: 13px; color: {text_color};'>
                    {" | ".join(metadata_parts)}
                </div>
            """

        # 组合元数据和说明内容
        return f"{metadata_html}{html_content}"

    def _toggle_description(self, scroll_area: QScrollArea, btn: QPushButton,
                           expanded_height: int = 180):
        """切换说明区域的展开/收起状态"""
        if scroll_area.height() > 60:  # 当前是展开状态
            scroll_area.setFixedHeight(50)
            btn.setText("▼ 展开")
        else:  # 当前是收起状态
            scroll_area.setFixedHeight(expanded_height)
            btn.setText("▲ 收起")

    def apply_theme(self, is_dark: bool = False):
        """
        应用主题样式到插件

        Args:
            is_dark: 是否为深色主题
        """
        # 获取当前主题样式
        style = Theme.get_plugin_style()
        self.setStyleSheet(style)

        # 触发主题切换回调
        self.on_theme_changed(is_dark)

    # ========== 工具方法 ==========

    def show_info(self, message: str, title: str = "提示"):
        """显示信息提示框"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, title, message)

    def show_warning(self, message: str, title: str = "警告"):
        """显示警告提示框"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(self, title, message)

    def show_error(self, message: str, title: str = "错误"):
        """显示错误提示框"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(self, title, message)

    def log_debug(self, message: str):
        """记录调试日志"""
        logger.debug(f"[{self.name}] {message}")

    def log_info(self, message: str):
        """记录信息日志"""
        logger.info(f"[{self.name}] {message}")

    def log_error(self, message: str):
        """记录错误日志"""
        logger.error(f"[{self.name}] {message}")
