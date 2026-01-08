import py_compile
import os
import shutil
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QListWidget, QGroupBox, QMessageBox, QLineEdit

from src.plugins.base_plugin import BasePlugin


class PycCompilerPlugin(BasePlugin):
    def __init__(self):
        super().__init__("Py转Pyc", "将Python文件编译为字节码文件")

        self.py_files = []
        self.output_dir = ""
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        source_group = QGroupBox("源文件")
        source_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        source_layout = QVBoxLayout()

        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                padding: 10px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #ffffff;
                min-height: 150px;
            }
        """)
        source_layout.addWidget(self.file_list)

        btn_layout = QHBoxLayout()

        self.select_btn = QPushButton("选择文件")
        self.select_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.select_btn.clicked.connect(self.select_files)
        btn_layout.addWidget(self.select_btn)

        self.clear_btn = QPushButton("清空")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_files)
        btn_layout.addWidget(self.clear_btn)

        btn_layout.addStretch()
        source_layout.addLayout(btn_layout)
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)

        output_group = QGroupBox("输出目录")
        output_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        output_layout = QVBoxLayout()

        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("留空则表示源文件所在目录")
        self.output_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        output_layout.addWidget(self.output_edit)

        self.select_output_btn = QPushButton("选择输出目录")
        self.select_output_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        self.select_output_btn.clicked.connect(self.select_output_dir)
        output_layout.addWidget(self.select_output_btn)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        compile_layout = QHBoxLayout()
        compile_layout.addStretch()

        self.compile_btn = QPushButton("开始编译")
        self.compile_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.compile_btn.clicked.connect(self.compile_files)
        compile_layout.addWidget(self.compile_btn)

        layout.addLayout(compile_layout)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择Python文件",
            "",
            "Python Files (*.py);;All Files (*)"
        )
        if files:
            for f in files:
                if f not in self.py_files:
                    self.py_files.append(f)
                    self.file_list.addItem(os.path.basename(f))

    def clear_files(self):
        self.py_files.clear()
        self.file_list.clear()

    def select_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择输出目录",
            ""
        )
        if dir_path:
            self.output_edit.setText(dir_path)

    def compile_files(self):
        if not self.py_files:
            QMessageBox.warning(self, "警告", "请先选择要编译的Python文件")
            return

        output_dir = self.output_edit.text().strip()
        if not output_dir:
            output_dir = None

        success_count = 0
        fail_count = 0

        for py_file in self.py_files:
            try:
                if output_dir:
                    pyc_dir = output_dir
                else:
                    pyc_dir = os.path.dirname(py_file)

                pyc_file = py_compile.compile(
                    py_file,
                    cfile=os.path.join(pyc_dir, os.path.basename(py_file) + "c"),
                    doraise=True
                )
                success_count += 1
            except py_compile.PyCompileError as e:
                print(f"编译失败 {py_file}: {e}")
                fail_count += 1
            except Exception as e:
                print(f"处理失败 {py_file}: {e}")
                fail_count += 1

        if success_count > 0:
            QMessageBox.information(
                self,
                "编译完成",
                f"成功: {success_count} 个文件\n失败: {fail_count} 个文件"
            )
        else:
            QMessageBox.critical(self, "编译失败", f"所有文件编译失败，请检查控制台输出")

    def get_widget(self) -> "PycCompilerPlugin":
        return self

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass
