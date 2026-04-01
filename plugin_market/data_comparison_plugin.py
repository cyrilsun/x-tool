import os
from datetime import datetime
from typing import List

import pandas as pd
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog,
    QGroupBox, QMessageBox, QLineEdit, QComboBox, QTextEdit,
    QScrollArea, QCheckBox, QWidget, QListWidget, QGridLayout, QFrame
)

from src.plugins.base_plugin import BasePlugin
from src.utils.logger import logger


class DataComparator:
    """
    数据对比工具类
    用于标记/提取重复数据和唯一数据
    """

    def _get_excel_engine(self, file_path: str) -> str:
        """
        根据文件扩展名获取合适的Excel引擎

        Args:
            file_path: Excel文件路径

        Returns:
            str: 引擎名称 ('openpyxl')
        """
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.xls':
            raise Exception(f"不支持 .xls 格式文件，请将文件另存为 .xlsx 格式后重试。\n文件: {os.path.basename(file_path)}")
        return 'openpyxl'  # 使用openpyxl处理.xlsx文件

    def __init__(self, file_path: str, sheet_name: str = None):
        """
        初始化数据对比器
        
        Args:
            file_path: Excel文件路径
            sheet_name: sheet名称，如果为None则使用第一个sheet
        """
        self.file_path = file_path
        self.sheet_name = sheet_name
        
        # 读取Excel文件
        self.df = self._read_excel(file_path, sheet_name)
        
        # 对比结果
        self.result = {
            "original_data": self.df.copy(),
            "duplicate_data": None,      # 重复数据
            "unique_data": None,         # 唯一数据
            "marked_duplicates": None,   # 标记重复数据
            "marked_uniques": None       # 标记唯一数据
        }
    
    def _read_excel(self, file_path: str, sheet_name: str = None) -> pd.DataFrame:
        """
        读取Excel文件

        Args:
            file_path: Excel文件路径
            sheet_name: sheet名称，如果为None则使用第一个sheet

        Returns:
            pd.DataFrame: 读取的数据
        """
        try:
            # 使用dtype=str读取所有列，避免科学计数法
            engine = self._get_excel_engine(file_path)
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str, engine=engine)
            else:
                # 当sheet_name为None时，read_excel会返回字典，需要获取第一个sheet
                df_dict = pd.read_excel(file_path, sheet_name=None, dtype=str, engine=engine)
                if not df_dict:
                    raise Exception("Excel文件中没有找到任何sheet")
                # 获取第一个sheet的数据
                df = list(df_dict.values())[0]

            return df
        except Exception as e:
            raise Exception(f"读取Excel文件失败: {str(e)}")

    def get_sheet_names(self, file_path: str) -> List[str]:
        """
        获取Excel文件的所有sheet名称

        Args:
            file_path: Excel文件路径

        Returns:
            List[str]: sheet名称列表
        """
        try:
            engine = self._get_excel_engine(file_path)
            excel_file = pd.ExcelFile(file_path, engine=engine)
            return excel_file.sheet_names
        except Exception as e:
            raise Exception(f"获取sheet名称失败: {str(e)}")
    
    def find_duplicates(self, key_columns: List[str] = None) -> pd.DataFrame:
        """
        查找重复数据
        
        Args:
            key_columns: 用于判断重复的列列表，如果为None则使用所有列
            
        Returns:
            pd.DataFrame: 重复的数据
        """
        if key_columns is None:
            # 使用所有列判断重复
            duplicates = self.df[self.df.duplicated(keep=False)]
        else:
            # 使用指定列判断重复
            duplicates = self.df[self.df.duplicated(subset=key_columns, keep=False)]
        
        self.result["duplicate_data"] = duplicates
        return duplicates
    
    def find_uniques(self, key_columns: List[str] = None) -> pd.DataFrame:
        """
        查找唯一数据
        
        Args:
            key_columns: 用于判断唯一的列列表，如果为None则使用所有列
            
        Returns:
            pd.DataFrame: 唯一的数据
        """
        if key_columns is None:
            # 使用所有列判断唯一
            uniques = self.df[~self.df.duplicated(keep=False)]
        else:
            # 使用指定列判断唯一
            uniques = self.df[~self.df.duplicated(subset=key_columns, keep=False)]
        
        self.result["unique_data"] = uniques
        return uniques
    
    def mark_duplicates(self, key_columns: List[str] = None, mark_column: str = "是否重复") -> pd.DataFrame:
        """
        标记重复数据
        
        Args:
            key_columns: 用于判断重复的列列表，如果为None则使用所有列
            mark_column: 标记列的名称
            
        Returns:
            pd.DataFrame: 标记了重复数据的原数据
        """
        df = self.df.copy()
        
        if key_columns is None:
            # 使用所有列判断重复
            df[mark_column] = df.duplicated(keep=False)
        else:
            # 使用指定列判断重复
            df[mark_column] = df.duplicated(subset=key_columns, keep=False)
        
        # 将布尔值转换为中文标识
        df[mark_column] = df[mark_column].map({True: "是", False: "否"})
        
        self.result["marked_duplicates"] = df
        return df
    
    def mark_uniques(self, key_columns: List[str] = None, mark_column: str = "是否唯一") -> pd.DataFrame:
        """
        标记唯一数据
        
        Args:
            key_columns: 用于判断唯一的列列表，如果为None则使用所有列
            mark_column: 标记列的名称
            
        Returns:
            pd.DataFrame: 标记了唯一数据的原数据
        """
        df = self.df.copy()
        
        if key_columns is None:
            # 使用所有列判断唯一
            df[mark_column] = ~df.duplicated(keep=False)
        else:
            # 使用指定列判断唯一
            df[mark_column] = ~df.duplicated(subset=key_columns, keep=False)
        
        # 将布尔值转换为中文标识
        df[mark_column] = df[mark_column].map({True: "是", False: "否"})
        
        self.result["marked_uniques"] = df
        return df
    
    def export_results(self, output_dir: str, export_items: List[str]) -> str:
        """
        导出对比结果
        
        Args:
            output_dir: 输出目录
            export_items: 要导出的项目列表，可以包含["duplicate_data", "unique_data", "marked_duplicates", "marked_uniques"]
            
        Returns:
            str: 导出文件路径
        """
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 生成导出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"data_comparison_result_{timestamp}.xlsx"
        output_path = os.path.join(output_dir, output_filename)
        
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # 写入原始数据
                self.result["original_data"].to_excel(writer, sheet_name='原始数据', index=False)
                
                # 写入选择的结果
                if "duplicate_data" in export_items and self.result["duplicate_data"] is not None:
                    self.result["duplicate_data"].to_excel(writer, sheet_name='重复数据', index=False)
                
                if "unique_data" in export_items and self.result["unique_data"] is not None:
                    self.result["unique_data"].to_excel(writer, sheet_name='唯一数据', index=False)
                
                if "marked_duplicates" in export_items and self.result["marked_duplicates"] is not None:
                    self.result["marked_duplicates"].to_excel(writer, sheet_name='标记重复数据', index=False)
                
                if "marked_uniques" in export_items and self.result["marked_uniques"] is not None:
                    self.result["marked_uniques"].to_excel(writer, sheet_name='标记唯一数据', index=False)
            
            return output_path
        except Exception as e:
            raise Exception(f"导出失败: {str(e)}")


class DataComparisonPlugin(BasePlugin):
    """
    表格数据对比插件
    支持标记重复数据、提取重复数据、标记唯一数据、提取唯一数据
    """

    # 插件元数据
    PLUGIN_INFO = {
        "name": "数据对比",
        "description": "标记/提取重复数据和唯一数据",
        "version": "1.0.0",
        "category": "数据处理",
    }

    def _get_excel_engine(self, file_path: str) -> str:
        """
        根据文件扩展名获取合适的Excel引擎

        Args:
            file_path: Excel文件路径

        Returns:
            str: 引擎名称 ('openpyxl')
        """
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.xls':
            raise Exception(f"不支持 .xls 格式文件，请将文件另存为 .xlsx 格式后重试。\n文件: {os.path.basename(file_path)}")
        return 'openpyxl'  # 使用openpyxl处理.xlsx文件

    def __init__(self):
        super().__init__()

        self.file_path = ""
        self.sheet_name = None
        self.key_columns = []

        self.comparator = None
        self.result = None

        self._setup_ui()
    
    def on_activate(self):
        """
        插件被激活时调用
        """
        logger.info("数据对比插件被激活")
    
    def get_widget(self) -> QWidget:
        return self
    
    def _setup_ui(self):
        """
        设置UI界面
        """
        # 使用基类提供的内容布局
        layout = self.get_content_layout()
        
        # 1. 文件上传与工作表选择区域
        file_group = QGroupBox("1. 上传文件、选择工作表")
        file_group.setStyleSheet("""
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
        
        file_layout = QVBoxLayout()
        
        # 文件选择说明
        file_instruction = QLabel("请选择要处理的Excel文件，支持.xlsx格式")
        file_instruction.setStyleSheet("font-size: 13px; color: #7f8c8d; margin-bottom: 10px;")
        file_layout.addWidget(file_instruction)
        
        # 文件选择
        file_select_layout = QHBoxLayout()
        file_label = QLabel("Excel文件:")
        file_label.setStyleSheet("font-size: 14px; min-width: 80px;")
        self.file_edit = QLineEdit()
        self.file_edit.setPlaceholderText("请选择Excel文件")
        self.file_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                color: #2c3e50;
            }
        """)
        self.select_file_btn = QPushButton("浏览")
        self.select_file_btn.setStyleSheet("""
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
        self.select_file_btn.clicked.connect(self.select_file)
        
        file_select_layout.addWidget(file_label)
        file_select_layout.addWidget(self.file_edit, 1)
        file_select_layout.addWidget(self.select_file_btn)
        
        # Sheet选择说明
        sheet_instruction = QLabel("选择Excel文件中要处理的工作表")
        sheet_instruction.setStyleSheet("font-size: 13px; color: #7f8c8d; margin-top: 10px; margin-bottom: 8px;")
        file_layout.addWidget(sheet_instruction)
        
        # Sheet选择
        sheet_layout = QHBoxLayout()
        sheet_label = QLabel("工作表:")
        sheet_label.setStyleSheet("font-size: 14px; min-width: 80px;")
        self.sheet_combo = QComboBox()
        self.sheet_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        sheet_layout.addWidget(sheet_label)
        sheet_layout.addWidget(self.sheet_combo, 1)
        
        file_layout.addLayout(file_select_layout)
        file_layout.addLayout(sheet_layout)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 2. 设置对比列
        key_group = QGroupBox("2. 设置对比列")
        key_group.setStyleSheet("""
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
        
        key_layout = QVBoxLayout()
        
        # 对比列说明
        key_instruction = QLabel("请指定用于判断重复/唯一的列，可以选择多个列组合判断")
        key_instruction.setStyleSheet("font-size: 13px; color: #7f8c8d; margin-bottom: 10px;")
        key_layout.addWidget(key_instruction)
        
        # 关键字列选择
        key_select_layout = QHBoxLayout()
        key_label = QLabel("对比列:")
        key_label.setStyleSheet("font-size: 14px; min-width: 80px;")
        self.key_list = QListWidget()
        self.key_list.setStyleSheet("""
            QListWidget {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        self.key_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.key_list.setFixedHeight(100)
        
        key_select_layout.addWidget(key_label)
        key_select_layout.addWidget(self.key_list, 1)
        key_layout.addLayout(key_select_layout)
        key_group.setLayout(key_layout)
        layout.addWidget(key_group)
        
        # 3. 选择操作
        operation_group = QGroupBox("3. 选择操作")
        operation_group.setStyleSheet("""
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
        
        operation_layout = QVBoxLayout()
        
        # 操作说明
        operation_instruction = QLabel("请勾选您想要执行的操作，可以选择多项同时执行")
        operation_instruction.setStyleSheet("font-size: 13px; color: #7f8c8d; margin-bottom: 10px;")
        operation_layout.addWidget(operation_instruction)
        
        # 操作复选框
        operation_grid = QGridLayout()
        operation_grid.setSpacing(15)
        
        self.mark_duplicates_checkbox = QCheckBox("标记重复数据")
        self.mark_duplicates_checkbox.setStyleSheet("font-size: 14px;")
        self.mark_duplicates_checkbox.setEnabled(False)
        
        self.extract_duplicates_checkbox = QCheckBox("提取重复数据")
        self.extract_duplicates_checkbox.setStyleSheet("font-size: 14px;")
        self.extract_duplicates_checkbox.setEnabled(False)
        
        self.mark_uniques_checkbox = QCheckBox("标记唯一数据")
        self.mark_uniques_checkbox.setStyleSheet("font-size: 14px;")
        self.mark_uniques_checkbox.setEnabled(False)
        
        self.extract_uniques_checkbox = QCheckBox("提取唯一数据")
        self.extract_uniques_checkbox.setStyleSheet("font-size: 14px;")
        self.extract_uniques_checkbox.setEnabled(False)
        
        operation_grid.addWidget(self.mark_duplicates_checkbox, 0, 0)
        operation_grid.addWidget(self.extract_duplicates_checkbox, 0, 1)
        operation_grid.addWidget(self.mark_uniques_checkbox, 1, 0)
        operation_grid.addWidget(self.extract_uniques_checkbox, 1, 1)
        
        # 执行按钮
        self.execute_btn = QPushButton("执行所选操作")
        self.execute_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.execute_btn.clicked.connect(self.execute_selected_operations)
        self.execute_btn.setEnabled(False)
        
        operation_layout.addLayout(operation_grid)
        
        # 执行按钮居中
        button_center_layout = QHBoxLayout()
        button_center_layout.addStretch()
        button_center_layout.addWidget(self.execute_btn)
        button_center_layout.addStretch()
        operation_layout.addLayout(button_center_layout)
        
        operation_group.setLayout(operation_layout)
        layout.addWidget(operation_group)
        
        # 4. 导出结果
        export_group = QGroupBox("4. 导出结果")
        export_group.setStyleSheet("""
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
        
        export_layout = QVBoxLayout()
        
        # 导出说明
        export_instruction = QLabel("根据执行的操作，选择要导出的结果内容")
        export_instruction.setStyleSheet("font-size: 13px; color: #7f8c8d; margin-bottom: 10px;")
        export_layout.addWidget(export_instruction)
        
        # 导出内容选择
        export_content_layout = QVBoxLayout()
        export_content_label = QLabel("选择要导出的内容:")
        export_content_label.setStyleSheet("font-size: 14px;")
        
        self.export_duplicate_checkbox = QCheckBox("提取的重复数据")
        self.export_duplicate_checkbox.setStyleSheet("font-size: 14px;")
        
        self.export_unique_checkbox = QCheckBox("提取的唯一数据")
        self.export_unique_checkbox.setStyleSheet("font-size: 14px;")
        
        self.export_marked_duplicates_checkbox = QCheckBox("标记重复的数据")
        self.export_marked_duplicates_checkbox.setStyleSheet("font-size: 14px;")
        
        self.export_marked_uniques_checkbox = QCheckBox("标记唯一的数据")
        self.export_marked_uniques_checkbox.setStyleSheet("font-size: 14px;")
        
        export_content_layout.addWidget(export_content_label)
        export_content_layout.addWidget(self.export_duplicate_checkbox)
        export_content_layout.addWidget(self.export_unique_checkbox)
        export_content_layout.addWidget(self.export_marked_duplicates_checkbox)
        export_content_layout.addWidget(self.export_marked_uniques_checkbox)
        
        # 导出按钮
        self.export_btn = QPushButton("导出结果")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.export_btn.clicked.connect(self.export_results)
        self.export_btn.setEnabled(False)
        
        export_layout.addLayout(export_content_layout)
        
        # 创建一个水平布局来放置导出按钮并使其右对齐
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.export_btn)
        export_layout.addLayout(button_layout)
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # 结果显示
        self.result_widget = QWidget()
        self.result_layout = QVBoxLayout(self.result_widget)
        self.result_layout.setContentsMargins(0, 0, 0, 0)
        
        # 摘要信息
        self.summary_label = QLabel("请先选择Excel文件并执行对比操作")
        self.summary_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 10px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                margin-top: 10px;
            }
        """)
        self.result_layout.addWidget(self.summary_label)
        
        layout.addWidget(self.result_widget)
        
        # 添加插件说明（使用基类方法，自动包含元数据）
        html_content = """
            <h3>数据对比插件功能介绍</h3>
            <p><strong>使用流程：</strong></p>
            <ol>
                <li><strong>上传文件、选择工作表</strong>：选择要处理的Excel文件，并从下拉列表中选择要操作的工作表</li>
                <li><strong>设置对比列</strong>：选择用于判断重复/唯一的关键字列，支持多选组合判断</li>
                <li><strong>选择操作</strong>：勾选需要执行的操作（可多选）：
                    <ul>
                        <li>标记重复数据：在原始数据中添加一列，标记每行是否为重复数据</li>
                        <li>提取重复数据：将所有重复的数据单独提取出来</li>
                        <li>标记唯一数据：在原始数据中添加一列，标记每行是否为唯一数据</li>
                        <li>提取唯一数据：将所有唯一的数据单独提取出来</li>
                    </ul>
                </li>
                <li><strong>导出结果</strong>：选择要导出的结果内容，点击导出按钮保存到本地</li>
            </ol>
            <p><strong>功能特点：</strong></p>
            <ul>
                <li>支持.xlsx格式的Excel文件</li>
                <li>支持基于多列组合判断数据重复/唯一</li>
                <li>支持同时执行多项操作，提高工作效率</li>
                <li>自动勾选已执行操作对应的导出选项</li>
                <li>导出包含原始数据和处理结果的Excel报告</li>
            </ul>
        """

        description_header, description_text, toggle_btn, description_scroll = self.create_description_section(html_content)

        # 添加到主布局
        layout.addLayout(description_header)
        layout.addWidget(description_scroll)

    def select_file(self):
        """
        选择Excel文件
        """
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "选择Excel文件",
            self.last_dir,
            "Excel文件 (*.xlsx *.xls);;所有文件 (*)"
        )
        
        if file_path:
            self.last_dir = os.path.dirname(file_path)
            self.file_path = file_path
            self.file_edit.setText(file_path)
            
            # 加载Sheet列表
            try:
                self.comparator = DataComparator(file_path, None)  # 临时创建
                sheet_names = self.comparator.get_sheet_names(file_path)
                self.sheet_combo.clear()
                self.sheet_combo.addItems(sheet_names)
                self.sheet_name = sheet_names[0]
                
                # 加载列名并过滤掉Unnamed列
                engine = self._get_excel_engine(file_path)
                df = pd.read_excel(file_path, sheet_name=sheet_names[0], engine=engine)
                columns = [col for col in df.columns.tolist() if not col.startswith('Unnamed:')]
                self.key_list.clear()
                self.key_list.addItems(columns)
                
                # 默认选择第一列作为关键字列
                if columns:
                    item = self.key_list.item(0)
                    if item:
                        item.setSelected(True)
                
                # 启用操作复选框和执行按钮
                self.mark_duplicates_checkbox.setEnabled(True)
                self.extract_duplicates_checkbox.setEnabled(True)
                self.mark_uniques_checkbox.setEnabled(True)
                self.extract_uniques_checkbox.setEnabled(True)
                self.execute_btn.setEnabled(True)
                self.export_btn.setEnabled(True)
                
            except Exception as e:
                QMessageBox.warning(self, "加载失败", f"加载文件信息失败: {str(e)}")
    
    def _get_selected_key_columns(self) -> List[str]:
        """
        获取选中的关键字列
        """
        return [item.text() for item in self.key_list.selectedItems()]
    
    def mark_duplicates(self):
        """
        标记重复数据
        """
        if not self.file_path:
            QMessageBox.warning(self, "警告", "请先选择Excel文件")
            return
        
        key_columns = self._get_selected_key_columns()
        if not key_columns:
            # 如果没有选择关键字列，则使用所有列
            key_columns = None
        
        try:
            # 创建对比器
            self.comparator = DataComparator(self.file_path, self.sheet_name)
            
            # 标记重复数据
            result = self.comparator.mark_duplicates(key_columns)
            
            # 更新结果显示
            self._update_result_display()
            
            QMessageBox.information(self, "完成", "重复数据标记完成")
            
            # 勾选对应的导出选项
            self.export_marked_duplicates_checkbox.setChecked(True)
            
        except Exception as e:
            QMessageBox.critical(self, "失败", f"标记重复数据时发生错误: {str(e)}")
            logger.info(f"标记重复数据错误: {str(e)}")
    
    def extract_duplicates(self):
        """
        提取重复数据
        """
        if not self.file_path:
            QMessageBox.warning(self, "警告", "请先选择Excel文件")
            return
        
        key_columns = self._get_selected_key_columns()
        if not key_columns:
            # 如果没有选择关键字列，则使用所有列
            key_columns = None
        
        try:
            # 创建对比器
            self.comparator = DataComparator(self.file_path, self.sheet_name)
            
            # 提取重复数据
            result = self.comparator.find_duplicates(key_columns)
            
            # 更新结果显示
            self._update_result_display()
            
            QMessageBox.information(self, "完成", f"成功提取 {len(result)} 条重复数据")
            
            # 勾选对应的导出选项
            self.export_duplicate_checkbox.setChecked(True)
            
        except Exception as e:
            QMessageBox.critical(self, "失败", f"提取重复数据时发生错误: {str(e)}")
            logger.info(f"提取重复数据错误: {str(e)}")
    
    def mark_uniques(self):
        """
        标记唯一数据
        """
        if not self.file_path:
            QMessageBox.warning(self, "警告", "请先选择Excel文件")
            return
        
        key_columns = self._get_selected_key_columns()
        if not key_columns:
            # 如果没有选择关键字列，则使用所有列
            key_columns = None
        
        try:
            # 创建对比器
            self.comparator = DataComparator(self.file_path, self.sheet_name)
            
            # 标记唯一数据
            result = self.comparator.mark_uniques(key_columns)
            
            # 更新结果显示
            self._update_result_display()
            
            QMessageBox.information(self, "完成", "唯一数据标记完成")
            
            # 勾选对应的导出选项
            self.export_marked_uniques_checkbox.setChecked(True)
            
        except Exception as e:
            QMessageBox.critical(self, "失败", f"标记唯一数据时发生错误: {str(e)}")
            logger.info(f"标记唯一数据错误: {str(e)}")
    
    def extract_uniques(self):
        """
        提取唯一数据
        """
        if not self.file_path:
            QMessageBox.warning(self, "警告", "请先选择Excel文件")
            return
        
        key_columns = self._get_selected_key_columns()
        if not key_columns:
            # 如果没有选择关键字列，则使用所有列
            key_columns = None
        
        try:
            # 创建对比器
            self.comparator = DataComparator(self.file_path, self.sheet_name)
            
            # 提取唯一数据
            result = self.comparator.find_uniques(key_columns)
            
            # 更新结果显示
            self._update_result_display()
            
            QMessageBox.information(self, "完成", f"成功提取 {len(result)} 条唯一数据")
            
            # 勾选对应的导出选项
            self.export_unique_checkbox.setChecked(True)
            
        except Exception as e:
            QMessageBox.critical(self, "失败", f"提取唯一数据时发生错误: {str(e)}")
            logger.info(f"提取唯一数据错误: {str(e)}")
    
    def execute_selected_operations(self):
        """
        执行选中的操作
        """
        if not self.file_path:
            QMessageBox.warning(self, "警告", "请先选择Excel文件")
            return
        
        # 检查是否有选中的操作
        has_selected = (
            self.mark_duplicates_checkbox.isChecked() or
            self.extract_duplicates_checkbox.isChecked() or
            self.mark_uniques_checkbox.isChecked() or
            self.extract_uniques_checkbox.isChecked()
        )
        
        if not has_selected:
            QMessageBox.warning(self, "警告", "请至少选择一项操作")
            return
        
        key_columns = self._get_selected_key_columns()
        if not key_columns:
            # 如果没有选择关键字列，则使用所有列
            key_columns = None
        
        try:
            # 创建对比器
            self.comparator = DataComparator(self.file_path, self.sheet_name)
            
            # 执行选中的操作
            executed_operations = []
            
            if self.mark_duplicates_checkbox.isChecked():
                self.comparator.mark_duplicates(key_columns)
                executed_operations.append("标记重复数据")
                self.export_marked_duplicates_checkbox.setChecked(True)
            
            if self.extract_duplicates_checkbox.isChecked():
                self.comparator.find_duplicates(key_columns)
                executed_operations.append("提取重复数据")
                self.export_duplicate_checkbox.setChecked(True)
            
            if self.mark_uniques_checkbox.isChecked():
                self.comparator.mark_uniques(key_columns)
                executed_operations.append("标记唯一数据")
                self.export_marked_uniques_checkbox.setChecked(True)
            
            if self.extract_uniques_checkbox.isChecked():
                self.comparator.find_uniques(key_columns)
                executed_operations.append("提取唯一数据")
                self.export_unique_checkbox.setChecked(True)
            
            # 更新结果显示
            self._update_result_display()
            
            # 显示完成信息
            QMessageBox.information(
                self, 
                "完成", 
                f"已成功执行以下操作：\n{chr(10).join(executed_operations)}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "失败", f"执行操作时发生错误: {str(e)}")
            logger.info(f"执行操作错误: {str(e)}")
    
    def _update_result_display(self):
        """
        更新结果显示
        """
        if not self.comparator:
            return
        
        # 获取原始数据行数
        original_count = len(self.comparator.result["original_data"])
        
        # 获取重复数据行数
        duplicate_count = len(self.comparator.result["duplicate_data"]) if self.comparator.result["duplicate_data"] is not None else 0
        
        # 获取唯一数据行数
        unique_count = len(self.comparator.result["unique_data"]) if self.comparator.result["unique_data"] is not None else 0
        
        # 构建摘要信息
        summary_text = f"""
数据对比摘要：
文件: {os.path.basename(self.file_path)} (Sheet: {self.sheet_name})
原始数据行数: {original_count}

处理结果：
重复数据行数: {duplicate_count}
唯一数据行数: {unique_count}

关键字列: {', '.join(self._get_selected_key_columns()) or '所有列'}
        """.strip()
        
        self.summary_label.setText(summary_text)
    
    def export_results(self):
        """
        导出结果
        """
        if not self.comparator:
            QMessageBox.warning(self, "警告", "请先执行对比操作")
            return
        
        # 选择报告保存目录
        output_dir = QFileDialog.getExistingDirectory(
            None,
            "选择报告保存目录",
            self.last_dir
        )
        
        if not output_dir:
            return
            
        self.last_dir = output_dir
        
        try:
            # 获取要导出的内容
            export_items = []
            if self.export_duplicate_checkbox.isChecked():
                export_items.append("duplicate_data")
            if self.export_unique_checkbox.isChecked():
                export_items.append("unique_data")
            if self.export_marked_duplicates_checkbox.isChecked():
                export_items.append("marked_duplicates")
            if self.export_marked_uniques_checkbox.isChecked():
                export_items.append("marked_uniques")
            
            if not export_items:
                QMessageBox.warning(self, "警告", "请至少选择一项要导出的内容")
                return
            
            # 生成报告
            report_path = self.comparator.export_results(output_dir, export_items)
            
            QMessageBox.information(
                self,
                "结果导出成功",
                f"数据对比结果已导出：\n{report_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出结果时发生错误: {str(e)}")
            logger.info(f"导出错误: {str(e)}")
