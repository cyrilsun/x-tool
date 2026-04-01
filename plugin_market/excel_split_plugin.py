import os
from typing import List, Optional, Dict, Any

import pandas as pd
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QGroupBox, QMessageBox, \
    QLineEdit, QComboBox, QSpinBox, QCheckBox, QWidget, QScrollArea, QTextEdit, QFrame

from src.plugins.base_plugin import BasePlugin
from src.utils.logger import logger


class ExcelSplitter:
    """
    Excel拆分工具类
    用于将Excel文件按不同方式拆分为多个文件
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

    def __init__(self, source_file: str, output_dir: str = "split"):
        """
        初始化Excel拆分器

        Args:
            source_file: 源Excel文件路径
            output_dir: 拆分后文件输出目录
        """
        self.source_file = source_file
        self.output_dir = output_dir

    def _ensure_output_directory(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"创建输出目录: {self.output_dir}")
    
    def read_excel_file(self, sheet_name: Optional[str] = None, header=0) -> Dict[str, Any]:
        """
        读取Excel文件

        Args:
            sheet_name: 工作表名称，None表示读取第一个工作表
            header: 表头行位置，0表示第一行

        Returns:
            Dict[str, Any]: 包含数据框、工作表名称、表头信息的字典
        """
        try:
            # 获取文件中的所有工作表
            engine = self._get_excel_engine(self.source_file)
            excel_file = pd.ExcelFile(self.source_file, engine=engine)

            if sheet_name is None:
                sheet_name = excel_file.sheet_names[0]

            # 读取指定工作表，将所有列作为字符串类型读取以避免科学计数和精度损失
            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=header, dtype=str)

            logger.info(f"✓ 成功读取: {os.path.basename(self.source_file)} - {sheet_name} ({len(df)} 行)")
            return {
                "sheet_name": sheet_name,
                "dataframe": df,
                "headers": list(df.columns),
                "total_rows": len(df)
            }
        except Exception as e:
            logger.info(f"✗ 读取文件失败: {os.path.basename(self.source_file)}, 错误: {str(e)}")
            raise
    
    def split_by_rows(self, df: pd.DataFrame, rows_per_file: int, preserve_header: bool = True) -> List[str]:
        """
        按行数拆分Excel文件

        Args:
            df: 要拆分的数据框
            rows_per_file: 每个文件包含的行数
            preserve_header: 是否保留表头

        Returns:
            List[str]: 生成的文件路径列表
        """
        if rows_per_file <= 0:
            raise ValueError("每个文件的行数必须大于0")

        total_rows = len(df)
        if total_rows == 0:
            return []

        # 确保输出目录存在
        self._ensure_output_directory()

        # 计算拆分数量
        num_splits = (total_rows + rows_per_file - 1) // rows_per_file

        output_files = []
        base_filename = os.path.splitext(os.path.basename(self.source_file))[0]
        
        logger.info(f"开始按行数拆分，总共 {total_rows} 行，每个文件 {rows_per_file} 行，将生成 {num_splits} 个文件...")
        
        for i in range(num_splits):
            # 计算当前拆分的起始和结束行
            start_row = i * rows_per_file
            end_row = min((i + 1) * rows_per_file, total_rows)
            
            # 获取当前拆分的数据
            split_df = df.iloc[start_row:end_row].copy()
            
            # 生成输出文件名
            output_filename = f"{base_filename}_split_{i+1}.xlsx"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # 保存到文件，使用openpyxl引擎并确保所有数据为字符串格式
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # 将DataFrame中的所有数据转换为字符串，先将NaN值替换为空字符串
                string_df = split_df.fillna('').astype(str)
                string_df.to_excel(writer, index=False, header=preserve_header)
            output_files.append(output_path)
            
            logger.info(f"✓ 生成文件: {output_filename} ({len(split_df)} 行)")
        
        return output_files
    
    def split_by_columns(self, df: pd.DataFrame, columns_per_file: int, preserve_header: bool = True) -> List[str]:
        """
        按列数拆分Excel文件

        Args:
            df: 要拆分的数据框
            columns_per_file: 每个文件包含的列数
            preserve_header: 是否保留表头

        Returns:
            List[str]: 生成的文件路径列表
        """
        if columns_per_file <= 0:
            raise ValueError("每个文件的列数必须大于0")

        total_columns = len(df.columns)
        if total_columns == 0:
            return []

        # 确保输出目录存在
        self._ensure_output_directory()

        # 计算拆分数量
        num_splits = (total_columns + columns_per_file - 1) // columns_per_file
        
        output_files = []
        base_filename = os.path.splitext(os.path.basename(self.source_file))[0]
        
        logger.info(f"开始按列数拆分，总共 {total_columns} 列，每个文件 {columns_per_file} 列，将生成 {num_splits} 个文件...")
        
        for i in range(num_splits):
            # 计算当前拆分的起始和结束列
            start_col = i * columns_per_file
            end_col = min((i + 1) * columns_per_file, total_columns)
            
            # 获取当前拆分的数据
            split_df = df.iloc[:, start_col:end_col].copy()
            
            # 生成输出文件名
            output_filename = f"{base_filename}_split_cols_{i+1}.xlsx"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # 保存到文件，使用openpyxl引擎并确保所有数据为字符串格式
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # 将DataFrame中的所有数据转换为字符串，先将NaN值替换为空字符串
                string_df = split_df.fillna('').astype(str)
                string_df.to_excel(writer, index=False, header=preserve_header)
            output_files.append(output_path)
            
            logger.info(f"✓ 生成文件: {output_filename} ({len(split_df.columns)} 列)")
        
        return output_files
    
    def split_by_field_value(self, df: pd.DataFrame, field_name: str, preserve_header: bool = True) -> List[str]:
        """
        按字段值拆分Excel文件

        Args:
            df: 要拆分的数据框
            field_name: 用于拆分的字段名称
            preserve_header: 是否保留表头

        Returns:
            List[str]: 生成的文件路径列表
        """
        if field_name not in df.columns:
            raise ValueError(f"字段 '{field_name}' 不存在于数据框中")

        # 确保输出目录存在
        self._ensure_output_directory()

        output_files = []
        base_filename = os.path.splitext(os.path.basename(self.source_file))[0]

        # 获取字段的唯一值
        unique_values = df[field_name].unique()
        
        logger.info(f"开始按字段值拆分，字段 '{field_name}' 有 {len(unique_values)} 个唯一值，将生成 {len(unique_values)} 个文件...")
        
        for value in unique_values:
            # 获取当前值的数据，特殊处理NaN值
            if pd.isna(value):
                # 当值为NaN时，使用isna()进行过滤
                split_df = df[pd.isna(df[field_name])].copy()
            else:
                # 当值不是NaN时，使用普通的等于比较
                split_df = df[df[field_name] == value].copy()
            
            # 生成输出文件名（处理特殊字符和空值）
            # 当值为NaN或空字符串时，使用'empty'代替
            if pd.isna(value) or str(value).strip() == '':
                value_str = '空值'
            else:
                value_str = str(value).replace(' ', '_').replace('/', '_').replace('\\', '_').replace(':', '_')
            output_filename = f"{base_filename}_{field_name}_{value_str}.xlsx"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # 保存到文件，使用openpyxl引擎并确保所有数据为字符串格式
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # 将DataFrame中的所有数据转换为字符串，先将NaN值替换为空字符串
                string_df = split_df.fillna('').astype(str)
                string_df.to_excel(writer, index=False, header=preserve_header)
            output_files.append(output_path)
            
            logger.info(f"✓ 生成文件: {output_filename} ({len(split_df)} 行)")
        
        return output_files


class ExcelSplitPlugin(BasePlugin):
    """
    Excel拆分插件
    提供多种Excel文件拆分方式
    """
    PLUGIN_INFO = {
        "name": "表格拆分",
        "description": "将Excel文件按行、按列或按字段值拆分为多个文件",
        "version": "1.0.0",
        "category": "表格工具"
    }

    def __init__(self):
        super().__init__()

        self.source_file = ""  # 源文件路径
        self.output_dir = ""    # 输出目录
        self.split_method = "rows"  # 拆分方式："rows", "columns", "field"
        self.rows_per_file = 1000  # 每行文件的行数
        self.columns_per_file = 10  # 每个文件的列数
        self.split_field = ""    # 用于拆分的字段名
        self.preserve_header = True  # 是否保留表头
        self.available_fields = []  # 可用字段列表

        self._setup_ui()
    
    def _setup_ui(self):
        """
        设置插件UI界面
        """
        # 使用基类提供的内容布局
        layout = self.get_content_layout()

        # 源文件选择
        source_group = QGroupBox("选择源文件")
        source_layout = QVBoxLayout()
        
        self.source_edit = QLineEdit()
        self.source_edit.setPlaceholderText("请选择要拆分的Excel文件")
        self.source_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                color: #2c3e50;
            }
        """)
        source_layout.addWidget(self.source_edit)
        
        self.select_source_btn = QPushButton("选择Excel文件")
        self.select_source_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.select_source_btn.clicked.connect(self.select_source_file)
        source_layout.addWidget(self.select_source_btn)
        
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)
        
        # 输出目录选择
        output_group = QGroupBox("选择输出目录")
        output_layout = QVBoxLayout()
        
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("请选择输出目录")
        self.output_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                color: #2c3e50;
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
                font-weight: bold;
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
        
        # 拆分选项
        option_group = QGroupBox("拆分选项")
        option_layout = QVBoxLayout()
        
        # 拆分方式
        method_layout = QHBoxLayout()
        method_label = QLabel("拆分方式:")
        self.method_combo = QComboBox()
        self.method_combo.addItem("按行数拆分", "rows")
        self.method_combo.addItem("按列数拆分", "columns")
        self.method_combo.addItem("按字段值拆分", "field")
        self.method_combo.setMinimumWidth(180)
        self.method_combo.currentIndexChanged.connect(self.on_split_method_changed)
        method_layout.addWidget(method_label)
        method_layout.addWidget(self.method_combo)
        method_layout.addStretch()
        option_layout.addLayout(method_layout)
        
        # 行数拆分选项
        self.rows_group = QGroupBox("按行数拆分")
        rows_layout = QHBoxLayout()
        rows_label = QLabel("每个文件行数:")
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, 100000)
        self.rows_spin.setValue(1000)
        rows_layout.addWidget(rows_label)
        rows_layout.addWidget(self.rows_spin)
        rows_layout.addStretch()
        self.rows_group.setLayout(rows_layout)
        option_layout.addWidget(self.rows_group)
        
        # 列数拆分选项
        self.columns_group = QGroupBox("按列数拆分")
        columns_layout = QHBoxLayout()
        columns_label = QLabel("每个文件列数:")
        self.columns_spin = QSpinBox()
        self.columns_spin.setRange(1, 1000)
        self.columns_spin.setValue(10)
        columns_layout.addWidget(columns_label)
        columns_layout.addWidget(self.columns_spin)
        columns_layout.addStretch()
        self.columns_group.setLayout(columns_layout)
        self.columns_group.hide()  # 默认隐藏
        option_layout.addWidget(self.columns_group)
        
        # 字段值拆分选项
        self.field_group = QGroupBox("按字段值拆分")
        field_layout = QHBoxLayout()
        field_label = QLabel("拆分字段:")
        self.field_combo = QComboBox()
        self.field_combo.setMinimumWidth(180)
        field_layout.addWidget(field_label)
        field_layout.addWidget(self.field_combo)
        field_layout.addStretch()
        self.field_group.setLayout(field_layout)
        self.field_group.hide()  # 默认隐藏
        option_layout.addWidget(self.field_group)
        
        # 保留表头选项
        header_layout = QHBoxLayout()
        self.preserve_header_check = QCheckBox("保留表头")
        self.preserve_header_check.setChecked(True)
        header_layout.addWidget(self.preserve_header_check)
        header_layout.addStretch()
        option_layout.addLayout(header_layout)
        
        option_group.setLayout(option_layout)
        layout.addWidget(option_group)
        
        # 拆分按钮
        split_layout = QHBoxLayout()
        split_layout.addStretch()
        
        self.split_btn = QPushButton("开始拆分")
        self.split_btn.setStyleSheet("""
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
        self.split_btn.clicked.connect(self.split_files)
        split_layout.addWidget(self.split_btn)
        
        layout.addLayout(split_layout)

        # 添加插件说明（使用基类的标准方法）
        html_content = """
            <h3>Excel拆分插件功能介绍</h3>
            <ul>
                <li><strong>按行数拆分</strong>：将Excel文件按指定行数拆分为多个文件</li>
                <li><strong>按列数拆分</strong>：将Excel文件按指定列数拆分为多个文件</li>
                <li><strong>按字段值拆分</strong>：根据指定字段的不同值将Excel文件拆分为多个文件</li>
                <li><strong>保留表头</strong>：可选择是否在每个拆分后的文件中保留表头</li>
                <li><strong>自定义输出目录</strong>：可选择拆分后文件的保存位置</li>
            </ul>
        """

        description_header, description_text, toggle_btn, description_scroll = self.create_description_section(html_content)
        layout.addLayout(description_header)
        layout.addWidget(description_scroll)
    
    def select_source_file(self):
        """
        选择源Excel文件
        """
        # 打开文件对话框，支持选择单个Excel文件
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "选择要拆分的Excel文件",
            self.last_dir,
            "Excel文件 (*.xlsx *.xls);;所有文件 (*)"
        )
        
        if file_path:
            self.last_dir = os.path.dirname(file_path)
            self.source_edit.setText(file_path)
            self.source_file = file_path
            # 读取文件获取字段列表
            self._load_fields()
        else:
            # 如果没选文件，尝试选择文件夹（以防用户习惯）
            dir_path = QFileDialog.getExistingDirectory(
                None,
                "选择源文件夹",
                self.last_dir
            )
            if dir_path:
                self.last_dir = dir_path
                self.source_edit.setText(dir_path)
                self.source_file = dir_path
                # 如果是文件夹，可能需要处理第一个文件或报错，这里保持原逻辑
                self._load_fields()
    
    def select_output_dir(self):
        """
        选择输出目录
        """
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择输出目录",
            self.last_dir
        )
        
        if dir_path:
            self.last_dir = dir_path
            self.output_edit.setText(dir_path)
            self.output_dir = dir_path
    
    def on_split_method_changed(self, index):
        """
        当拆分方式改变时的处理
        """
        method = self.method_combo.currentData()
        
        # 隐藏所有拆分选项组
        self.rows_group.hide()
        self.columns_group.hide()
        self.field_group.hide()
        
        # 显示选中的拆分选项组
        if method == "rows":
            self.rows_group.show()
        elif method == "columns":
            self.columns_group.show()
        elif method == "field":
            self.field_group.show()
    
    def _load_fields(self):
        """
        加载Excel文件中的字段列表
        """
        if not self.source_file:
            return
        
        try:
            # 读取文件
            splitter = ExcelSplitter(self.source_file)
            result = splitter.read_excel_file()
            
            # 更新字段下拉框
            self.field_combo.clear()
            self.available_fields = result["headers"]
            
            for field in self.available_fields:
                self.field_combo.addItem(field)
                
            if self.available_fields:
                logger.info(f"成功加载 {len(self.available_fields)} 个字段")
        except Exception as e:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("警告")
            msg_box.setText(f"读取文件字段失败: {str(e)}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
            msg_box.exec()
    
    def split_files(self):
        """
        执行文件拆分操作
        """
        # 检查源文件
        if not self.source_file:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("警告")
            msg_box.setText("请先选择要拆分的Excel文件")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
            msg_box.exec()
            return
        
        # 检查输出目录
        if not self.output_dir:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("警告")
            msg_box.setText("请先选择输出目录")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
            msg_box.exec()
            return
        
        try:
            # 创建拆分器实例
            splitter = ExcelSplitter(self.source_file, self.output_dir)
            
            # 读取文件
            result = splitter.read_excel_file()
            df = result["dataframe"]
            
            if df is None or len(df) == 0:
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setWindowTitle("警告")
                msg_box.setText("读取的Excel文件为空或格式不正确")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
                msg_box.exec()
                return
            
            # 获取拆分参数
            method = self.method_combo.currentData()
            preserve_header = self.preserve_header_check.isChecked()
            
            output_files = []
            
            # 执行拆分
            if method == "rows":
                rows_per_file = self.rows_spin.value()
                output_files = splitter.split_by_rows(df, rows_per_file, preserve_header)
            elif method == "columns":
                columns_per_file = self.columns_spin.value()
                output_files = splitter.split_by_columns(df, columns_per_file, preserve_header)
            elif method == "field":
                if not self.field_combo.currentText():
                    msg_box = QMessageBox(self)
                    msg_box.setIcon(QMessageBox.Icon.Warning)
                    msg_box.setWindowTitle("警告")
                    msg_box.setText("请选择拆分字段")
                    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
                    msg_box.exec()
                    return
                field_name = self.field_combo.currentText()
                output_files = splitter.split_by_field_value(df, field_name, preserve_header)
            
            # 显示拆分结果
            if output_files:
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.setWindowTitle("拆分成功")
                msg_box.setText(f"成功生成 {len(output_files)} 个文件\n输出目录: {self.output_dir}")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
                msg_box.exec()
            else:
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.setWindowTitle("拆分完成")
                msg_box.setText("没有生成任何文件")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
                msg_box.exec()
                
        except Exception as e:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("错误")
            msg_box.setText(f"拆分过程中出现错误: {str(e)}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
            msg_box.exec()

    def get_widget(self) -> QWidget:
        """
        获取插件的UI组件
        """
        return self
    
    def on_activate(self):
        """
        插件激活时的处理
        """
        logger.info("Excel拆分插件被激活")
    
    def on_deactivate(self):
        """
        插件停用当的处理
        """
        logger.info("Excel拆分插件被停用")