#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试插件"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

from src.plugins.base_plugin import BasePlugin


class TestPlugin(BasePlugin):
    def __init__(self):
        super().__init__("测试插件", "这是一个测试插件的描述")
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI界面"""
        # 创建主窗口部件
        self.main_widget = QWidget()
        self.main_widget.setWindowTitle(self.plugin_name)
        self.main_widget.setMinimumSize(300, 200)
        
        # 创建垂直布局
        layout = QVBoxLayout(self.main_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 添加测试标签
        self.label = QLabel(f"欢迎使用 {self.plugin_name}！")
        font = self.label.font()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        # 添加测试按钮
        self.button = QPushButton("点击测试")
        self.button.clicked.connect(self.on_button_clicked)
        layout.addWidget(self.button)
    
    def on_button_clicked(self):
        """按钮点击事件处理"""
        self.label.setText("按钮已点击！")
    
    def show_ui(self):
        """显示UI界面"""
        return self.main_widget


# 插件导出
export = TestPlugin
