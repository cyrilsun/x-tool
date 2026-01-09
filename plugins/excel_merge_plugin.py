import os
import pandas as pd
import glob
from typing import List, Optional
from datetime import datetime
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QGroupBox, QMessageBox, QLineEdit, QComboBox, QDialog, QTextEdit, QScrollArea, QCheckBox, QSpinBox, QWidget

from src.plugins.base_plugin import BasePlugin


class ExcelMerger:
    """
    Excel合并工具类
    用于将doc文件夹下的所有Excel文件合并成一个新的Excel文件
    """
    
    def __init__(self, source_dir: str = "doc", output_dir: str = "merged", selected_files: Optional[List[str]] = None):
        """
        初始化Excel合并器
        
        Args:
            source_dir: 源Excel文件文件夹
            output_dir: 合并后文件输出文件夹
            selected_files: 用户选择的文件列表，如果提供则优先使用
        """
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.selected_files = selected_files
        
        # 确保输出文件夹存在
        self._ensure_output_directory()
    
    def _ensure_output_directory(self):
        """确保输出文件夹存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"创建输出文件夹: {self.output_dir}")
    
    def get_excel_files(self) -> List[str]:
        """
        获取Excel文件列表
        如果提供了selected_files，则直接返回该列表
        否则从源文件夹下查找所有Excel文件
        
        Returns:
            List[str]: Excel文件路径列表
        """
        # 如果提供了选择的文件列表，直接返回
        if self.selected_files:
            print(f"使用用户选择的 {len(self.selected_files)} 个Excel文件")
            return self.selected_files
        
        # 否则从源文件夹下查找所有Excel文件
        if not os.path.exists(self.source_dir):
            print(f"警告: 源文件夹 {self.source_dir} 不存在")
            return []
        
        # 查找所有Excel文件
        excel_patterns = ["*.xlsx", "*.xls"]
        excel_files = []
        
        for pattern in excel_patterns:
            files = glob.glob(os.path.join(self.source_dir, pattern))
            excel_files.extend(files)
        
        # 按文件名排序
        excel_files.sort()
        
        print(f"在源文件夹中找到 {len(excel_files)} 个Excel文件")
        return excel_files
    
    def read_excel_file(self, file_path: str, header=0, merge_header_rows=False, header_rows=1, dtype=str) -> List[dict]:
        """
        读取单个Excel文件中的所有sheet
        
        Args:
            file_path: Excel文件路径
            header: 表头行位置，0表示第一行，None表示无表头
            merge_header_rows: 是否合并多行表头
            header_rows: 表头行数，仅当merge_header_rows为True时有效
            dtype: 数据类型，默认为str
            
        Returns:
            List[dict]: 包含sheet名称、数据框和表头信息的字典列表
        """
        try:
            # 获取文件中的所有sheet
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            file_name = os.path.basename(file_path)
            
            result = []
            
            for sheet_name in sheet_names:
                try:
                    if merge_header_rows and header_rows > 1:
                        # 读取多行表头
                        df_raw = pd.read_excel(excel_file, sheet_name=sheet_name, header=None, dtype=str)  # 强制使用str类型
                        
                        # 合并多行表头
                        header_data = df_raw.iloc[:header_rows].fillna('')
                        merged_headers = []
                        for col_idx in range(header_data.shape[1]):
                            header_parts = []
                            for row_idx in range(header_rows):
                                header_val = header_data.iloc[row_idx, col_idx]
                                if header_val.strip():
                                    header_parts.append(str(header_val))
                            
                            if header_parts:
                                merged_header = ' '.join(header_parts)
                            else:
                                merged_header = f'Column_{col_idx}'
                            merged_headers.append(merged_header)
                        
                        # 设置新的表头并跳过表头行
                        df = df_raw.iloc[header_rows:].copy()
                        df.columns = merged_headers
                        
                        # 确保所有列都是字符串类型
                        df = df.astype(str)
                    else:
                        # 正常读取单个表头
                        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=header, dtype=dtype)
                    
                    print(f"✓ 成功读取: {file_name} - {sheet_name} ({len(df)} 行)")
                    result.append({
                        "sheet_name": sheet_name,
                        "dataframe": df,
                        "header_rows": header_rows if merge_header_rows else 1 if header is not None else 0,
                        "headers": list(df.columns)
                    })
                except Exception as e:
                    print(f"✗ 读取sheet失败: {file_name} - {sheet_name}, 错误: {str(e)}")
            
            return result
        except Exception as e:
            print(f"✗ 读取文件失败: {os.path.basename(file_path)}, 错误: {str(e)}")
            return []
    
    def merge_excel_files(self, output_filename: Optional[str] = None, header=0, merge_header_rows=False, header_rows=1, header_mode="auto") -> dict:
        """
        合并所有Excel文件，将所有文件的所有sheet合并到同一个sheet
        
        Args:
            output_filename: 输出文件名，如果为None则自动生成
            header: 表头行位置，0表示第一行，None表示无表头
            merge_header_rows: 是否合并多行表头
            header_rows: 表头行数，仅当merge_header_rows为True时有效
            header_mode: 表头处理模式，可选值：
                        "auto": 自动合并相同表头
                        "first": 使用第一个sheet的表头
                        "union": 使用所有表头的并集
                        "intersection": 使用所有表头的交集
            
        Returns:
            dict: 包含合并结果的详细信息
        """
        # 获取所有Excel文件
        excel_files = self.get_excel_files()
        
        if not excel_files:
            print("没有找到Excel文件，无法进行合并")
            return {
                "success": False,
                "message": "没有找到Excel文件，无法进行合并"
            }
        
        # 生成输出文件名
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"merged_excel_{timestamp}.xlsx"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        print(f"开始合并 {len(excel_files)} 个Excel文件的所有sheet...")
        print("=" * 60)
        
        # 存储所有数据框
        all_dataframes = []
        successful_files = 0
        failed_files = 0
        total_sheets = 0
        headers_info = []
        
        # 读取所有Excel文件
        for i, file_path in enumerate(excel_files, 1):
            file_name = os.path.basename(file_path)
            print(f"[{i}/{len(excel_files)}] 处理: {file_name}")
            
            sheets_data = self.read_excel_file(file_path, header=header, merge_header_rows=merge_header_rows, header_rows=header_rows)
            if sheets_data:
                successful_files += 1
                total_sheets += len(sheets_data)
                
                # 处理每个sheet
                for sheet_data in sheets_data:
                    df = sheet_data["dataframe"]
                    sheet_name = sheet_data["sheet_name"]
                    
                    # 记录表头信息
                    headers_info.append({
                        "file": file_name,
                        "sheet": sheet_name,
                        "headers": sheet_data["headers"]
                    })
                    
                    # 添加来源文件和sheet信息列
                    df['来源文件'] = file_name
                    df['来源Sheet'] = sheet_name
                    
                    all_dataframes.append(df)
            else:
                failed_files += 1
        
        if not all_dataframes:
            print("没有成功读取任何Excel文件或sheet，无法进行合并")
            return {
                "success": False,
                "message": "没有成功读取任何Excel文件或sheet，无法进行合并"
            }
        
        try:
            # 合并所有数据框
            print(f"\n正在合并 {len(all_dataframes)} 个数据框（来自 {total_sheets} 个sheet）...")
            
            # 根据表头模式处理数据框合并
            if header_mode == "first":
                # 使用第一个sheet的表头
                first_columns = all_dataframes[0].columns
                merged_df = pd.concat(
                    [df.reindex(columns=first_columns) for df in all_dataframes], 
                    ignore_index=True
                )
            elif header_mode == "intersection":
                # 使用所有表头的交集
                common_columns = set(all_dataframes[0].columns)
                for df in all_dataframes[1:]:
                    common_columns.intersection_update(df.columns)
                common_columns = sorted(list(common_columns))
                merged_df = pd.concat(
                    [df[common_columns].reindex(columns=common_columns) for df in all_dataframes], 
                    ignore_index=True
                )
            elif header_mode == "union":
                # 使用所有表头的并集
                all_columns = set()
                for df in all_dataframes:
                    all_columns.update(df.columns)
                all_columns = sorted(list(all_columns))
                merged_df = pd.concat(
                    [df.reindex(columns=all_columns) for df in all_dataframes], 
                    ignore_index=True
                )
            else:  # "auto" 模式
                # 自动合并，使用默认的pd.concat行为（基于列名匹配）
                merged_df = pd.concat(all_dataframes, ignore_index=True)
            
            # 保存合并后的文件
            merged_df.to_excel(output_path, index=False, engine='openpyxl')
            
            # print("=" * 60)
            # print(f"✓ 合并完成!")
            # print(f"输出文件: {output_path}")
            # print(f"总行数: {len(merged_df)}")
            # print(f"总列数: {len(merged_df.columns)}")
            # print(f"成功读取: {successful_files} 个文件")
            # print(f"读取失败: {failed_files} 个文件")
            # print(f"总处理sheet数: {total_sheets}")
            
            # 显示列信息
            print(f"\n列信息:")
            for i, col in enumerate(merged_df.columns, 1):
                print(f"  {i}. {col}")
            
            return {
                "success": True,
                "output_path": output_path,
                "total_files": len(excel_files),
                "successful_files": successful_files,
                "failed_files": failed_files,
                "total_sheets": total_sheets,
                "total_rows": len(merged_df),
                "total_columns": len(merged_df.columns),
                "message": f"成功合并 {successful_files} 个Excel文件到 {output_path}"
            }
            
        except Exception as e:
            error_msg = f"✗ 合并失败: {str(e)}"
            print(error_msg)
            return {
                "success": False,
                "message": error_msg
            }
    
    def merge_with_sheet_separation(self, output_filename: Optional[str] = None, header=0, merge_header_rows=False, header_rows=1) -> dict:
        """
        合并Excel文件，每个源文件的每个sheet作为一个单独的工作表
        
        Args:
            output_filename: 输出文件名，如果为None则自动生成
            header: 表头行位置，0表示第一行，None表示无表头
            merge_header_rows: 是否合并多行表头
            header_rows: 表头行数，仅当merge_header_rows为True时有效
            
        Returns:
            dict: 包含合并结果的详细信息
        """
        # 获取所有Excel文件
        excel_files = self.get_excel_files()
        
        if not excel_files:
            print("没有找到Excel文件，无法进行合并")
            return {
                "success": False,
                "message": "没有找到Excel文件，无法进行合并"
            }
        
        # 生成输出文件名
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"merged_excel_sheets_{timestamp}.xlsx"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        print(f"开始合并 {len(excel_files)} 个Excel文件到不同工作表...")
        print("=" * 60)
        
        try:
            # 创建ExcelWriter对象
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                successful_files = 0
                failed_files = 0
                total_sheets = 0
                
                for i, file_path in enumerate(excel_files, 1):
                    file_name = os.path.basename(file_path)
                    print(f"[{i}/{len(excel_files)}] 处理: {file_name}")
                    
                    sheets_data = self.read_excel_file(file_path, header=header, merge_header_rows=merge_header_rows, header_rows=header_rows)
                    if sheets_data:
                        successful_files += 1
                        
                        # 处理每个sheet
                        for sheet_data in sheets_data:
                            df = sheet_data["dataframe"]
                            sheet_name = sheet_data["sheet_name"]
                            
                            # 生成工作表名称（文件名 + sheet名）
                            base_file_name = os.path.splitext(file_name)[0]
                            full_sheet_name = f"{base_file_name}_{sheet_name}"
                            
                            # 如果工作表名称过长，截断它
                            if len(full_sheet_name) > 31:  # Excel工作表名称最大31个字符
                                full_sheet_name = full_sheet_name[:31]
                            
                            # 写入工作表
                            df.to_excel(writer, sheet_name=full_sheet_name, index=False)
                            total_sheets += 1
                    else:
                        failed_files += 1
            
            print("=" * 60)
            print(f"✓ 合并完成!")
            print(f"输出文件: {output_path}")
            print(f"成功处理: {successful_files} 个文件")
            print(f"处理失败: {failed_files} 个文件")
            print(f"总处理sheet数: {total_sheets}")
            
            return {
                "success": True,
                "output_path": output_path,
                "total_files": len(excel_files),
                "successful_files": successful_files,
                "failed_files": failed_files,
                "total_sheets": total_sheets,
                "message": f"成功合并 {successful_files} 个Excel文件到 {output_path}"
            }
            
        except Exception as e:
            error_msg = f"✗ 合并失败: {str(e)}"
            print(error_msg)
            return {
                "success": False,
                "message": error_msg
            }
    
    def merge_single_file_sheets(self, header=0, merge_header_rows=False, header_rows=1, header_mode="auto") -> dict:
        """
        合并同一Excel文件中的多个sheet到一个新的Excel文件
        每个源文件生成一个对应的合并文件
        
        Args:
            header: 表头行位置，0表示第一行，None表示无表头
            merge_header_rows: 是否合并多行表头
            header_rows: 表头行数，仅当merge_header_rows为True时有效
            header_mode: 表头处理模式，可选值：
                        "auto": 自动合并相同表头
                        "first": 使用第一个sheet的表头
                        "union": 使用所有表头的并集
                        "intersection": 使用所有表头的交集
        
        Returns:
            dict: 包含合并结果的详细信息
        """
        # 获取所有Excel文件
        excel_files = self.get_excel_files()
        
        if not excel_files:
            print("没有找到Excel文件，无法进行合并")
            return {
                "success": False,
                "message": "没有找到Excel文件，无法进行合并"
            }
        
        print(f"开始合并 {len(excel_files)} 个Excel文件中的多个sheet...")
        print("=" * 60)
        
        successful_files = 0
        failed_files = 0
        total_sheets = 0
        output_files = []
        
        for i, file_path in enumerate(excel_files, 1):
            file_name = os.path.basename(file_path)
            print(f"[{i}/{len(excel_files)}] 处理: {file_name}")
            
            try:
                # 读取文件中的所有sheet
                sheets_data = self.read_excel_file(file_path, header=header, merge_header_rows=merge_header_rows, header_rows=header_rows)
                if not sheets_data:
                    print(f"✗ 无法读取文件 {file_name} 中的任何sheet")
                    failed_files += 1
                    continue
                
                # 合并同一文件的所有sheet
                all_dataframes = []
                file_sheets = 0
                file_rows = 0
                file_columns = 0
                
                for sheet_data in sheets_data:
                    df = sheet_data["dataframe"]
                    sheet_name = sheet_data["sheet_name"]
                    file_sheets += 1
                    file_rows += len(df)
                    
                    # 添加来源sheet信息列
                    df['来源Sheet'] = sheet_name
                    all_dataframes.append(df)
                
                if not all_dataframes:
                    print(f"✗ 文件 {file_name} 中没有可合并的数据")
                    failed_files += 1
                    continue
                
                # 根据表头模式处理数据框合并
                if header_mode == "first":
                    # 使用第一个sheet的表头
                    first_columns = all_dataframes[0].columns
                    merged_df = pd.concat(
                        [df.reindex(columns=first_columns) for df in all_dataframes], 
                        ignore_index=True
                    )
                elif header_mode == "intersection":
                    # 使用所有表头的交集
                    common_columns = set(all_dataframes[0].columns)
                    for df in all_dataframes[1:]:
                        common_columns.intersection_update(df.columns)
                    common_columns = sorted(list(common_columns))
                    merged_df = pd.concat(
                        [df[common_columns].reindex(columns=common_columns) for df in all_dataframes], 
                        ignore_index=True
                    )
                elif header_mode == "union":
                    # 使用所有表头的并集
                    all_columns = set()
                    for df in all_dataframes:
                        all_columns.update(df.columns)
                    all_columns = sorted(list(all_columns))
                    merged_df = pd.concat(
                        [df.reindex(columns=all_columns) for df in all_dataframes], 
                        ignore_index=True
                    )
                else:  # "auto" 模式
                    # 自动合并，使用默认的pd.concat行为（基于列名匹配）
                    merged_df = pd.concat(all_dataframes, ignore_index=True)
                
                file_columns = len(merged_df.columns)
                
                # 生成输出文件名
                base_file_name = os.path.splitext(file_name)[0]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"{base_file_name}_merged_{timestamp}.xlsx"
                output_path = os.path.join(self.output_dir, output_filename)
                
                # 保存合并后的文件
                merged_df.to_excel(output_path, index=False, engine='openpyxl')
                
                print(f"✓ 成功合并 {len(sheets_data)} 个sheet到文件: {output_path}")
                print(f"  总行数: {len(merged_df)}")
                print(f"  总列数: {len(merged_df.columns)}")
                
                successful_files += 1
                total_sheets += file_sheets
                output_files.append(output_path)
                
            except Exception as e:
                print(f"✗ 合并文件 {file_name} 失败: {str(e)}")
                failed_files += 1
        
        print("=" * 60)
        print(f"合并完成!")
        print(f"成功处理: {successful_files} 个文件")
        print(f"处理失败: {failed_files} 个文件")
        
        return {
            "success": successful_files > 0,
            "total_files": len(excel_files),
            "successful_files": successful_files,
            "failed_files": failed_files,
            "total_sheets": total_sheets,
            "output_files": output_files,
            "message": f"成功处理 {successful_files} 个文件，生成 {len(output_files)} 个输出文件"
        }
    
    def get_merge_statistics(self) -> dict:
        """
        获取合并统计信息
        
        Returns:
            dict: 统计信息
        """
        excel_files = self.get_excel_files()
        
        if not excel_files:
            return {
                "total_files": 0,
                "file_list": [],
                "total_size_mb": 0
            }
        
        # 计算文件大小
        total_size = 0
        for file_path in excel_files:
            total_size += os.path.getsize(file_path)
        
        total_size_mb = total_size / (1024 * 1024)
        
        return {
            "total_files": len(excel_files),
            "file_list": [os.path.basename(f) for f in excel_files],
            "total_size_mb": round(total_size_mb, 2)
        }


class ExcelMergePlugin(BasePlugin):
    def __init__(self):
        super().__init__("表格合并", "合并多个Excel文件到一个文件或合并多个Sheet到一个Sheet")

        self.source_path = ""  # 可以是文件路径或文件夹路径
        self.selected_files = None  # 保存用户选择的文件列表
        self.output_dir = ""
        self.merge_option = "single_sheet"  # "single_sheet", "multiple_sheets", 或 "single_file_sheets"
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        source_group = QGroupBox("选择源文件")
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

        self.source_edit = QLineEdit()
        self.source_edit.setPlaceholderText("请选择Excel文件")
        self.source_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        source_layout.addWidget(self.source_edit)

        self.select_source_btn = QPushButton("选择源文件")
        self.select_source_btn.setStyleSheet("""
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
        self.select_source_btn.clicked.connect(self.select_source)
        source_layout.addWidget(self.select_source_btn)

        source_group.setLayout(source_layout)
        layout.addWidget(source_group)

        output_group = QGroupBox("选择输出文件夹")
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
        self.output_edit.setPlaceholderText("请选择输出文件夹")
        self.output_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        output_layout.addWidget(self.output_edit)

        self.select_output_btn = QPushButton("选择输出文件夹")
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

        option_group = QGroupBox("合并选项")
        option_group.setStyleSheet("""
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

        option_layout = QVBoxLayout()

        option_label = QLabel("合并方式:")
        option_label.setStyleSheet("font-size: 14px;")
        option_layout.addWidget(option_label)

        self.merge_combo = QComboBox()
        self.merge_combo.addItem("合并多个文件到同一sheet")
        self.merge_combo.addItem("合并多个文件到多个sheet")
        self.merge_combo.addItem("合并1个文件的多个sheet")
        self.merge_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        self.merge_combo.setMinimumWidth(200)  # 增加最小宽度，确保选项完整显示
        option_layout.addWidget(self.merge_combo)

        # 表头处理选项
        header_group = QGroupBox("表头处理")
        header_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: normal;
                color: #34495e;
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                font-weight: bold;
            }
        """)

        header_layout = QVBoxLayout()

        # 多行表头合并选项
        self.merge_header_check = QCheckBox("合并多行表头")
        self.merge_header_check.setStyleSheet("font-size: 13px;")
        self.merge_header_check.stateChanged.connect(self.on_merge_header_changed)
        header_layout.addWidget(self.merge_header_check)

        # 表头行数选择
        header_rows_layout = QHBoxLayout()
        header_rows_label = QLabel("表头行数:")
        header_rows_label.setStyleSheet("font-size: 13px;")
        self.header_rows_spin = QSpinBox()
        self.header_rows_spin.setRange(1, 5)
        self.header_rows_spin.setValue(1)
        self.header_rows_spin.setStyleSheet("font-size: 13px;")
        self.header_rows_spin.setEnabled(False)  # 默认禁用，只有在合并多行表头时启用
        header_rows_layout.addWidget(header_rows_label)
        header_rows_layout.addWidget(self.header_rows_spin)
        header_rows_layout.addStretch()
        header_layout.addLayout(header_rows_layout)

        # 表头处理模式
        header_mode_layout = QHBoxLayout()
        header_mode_label = QLabel("表头合并模式:")
        header_mode_label.setStyleSheet("font-size: 13px;")
        self.header_mode_combo = QComboBox()
        self.header_mode_combo.addItem("自动合并", "auto")
        self.header_mode_combo.addItem("使用第一个文件表头", "first")
        self.header_mode_combo.addItem("合并所有表头", "union")
        self.header_mode_combo.addItem("仅保留共同表头", "intersection")
        self.header_mode_combo.setStyleSheet("font-size: 13px;")
        self.header_mode_combo.setMinimumWidth(180)  # 增加最小宽度，确保选项完整显示
        header_mode_layout.addWidget(header_mode_label)
        header_mode_layout.addWidget(self.header_mode_combo)
        header_mode_layout.addStretch()
        header_layout.addLayout(header_mode_layout)

        header_group.setLayout(header_layout)
        option_layout.addWidget(header_group)

        option_group.setLayout(option_layout)
        layout.addWidget(option_group)

        merge_layout = QHBoxLayout()
        merge_layout.addStretch()

        # 预览按钮
        self.preview_btn = QPushButton("预览表头")
        self.preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.preview_btn.clicked.connect(self.preview_headers)
        merge_layout.addWidget(self.preview_btn)
        
        # 合并按钮
        self.merge_btn = QPushButton("开始合并")
        self.merge_btn.setStyleSheet("""
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
        self.merge_btn.clicked.connect(self.merge_files)
        merge_layout.addWidget(self.merge_btn)

        layout.addLayout(merge_layout)

        # 添加插件说明
        self.description_expanded = False  # 展开状态标记
        
        # 创建说明标题和展开/收起按钮
        description_header_layout = QHBoxLayout()
        
        description_title = QLabel("<h3 style='margin: 0;'>插件说明</h3>")
        
        self.toggle_description_btn = QPushButton("▼ 展开")
        self.toggle_description_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                color: #343a40;
                border: 1px solid #dee2e6;
                padding: 4px 8px;
                font-size: 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        self.toggle_description_btn.clicked.connect(self.toggle_description)
        
        description_header_layout.addWidget(description_title)
        description_header_layout.addStretch()
        description_header_layout.addWidget(self.toggle_description_btn)
        
        # 创建说明内容区域
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setStyleSheet("font-size: 13px; padding: 10px;")
        self.description_text.setHtml("""
            <h3>Excel合并插件功能介绍</h3>
            <ul>
                <li><strong>多文件合并</strong>：支持将多个Excel文件合并为一个文件</li>
                <li><strong>多工作表合并</strong>：合并单个文件中的所有工作表</li>
                <li><strong>表头处理</strong>：提供多种表头合并策略
                    <ul>
                        <li>自动合并：智能检测并合并相似表头</li>
                        <li>使用第一个文件表头：以第一个文件的表头为准</li>
                        <li>合并所有表头：保留所有文件的表头</li>
                        <li>仅保留共同表头：只保留所有文件都存在的表头</li>
                    </ul>
                </li>
                <li><strong>自定义表头行数</strong>：支持设置表头的行数</li>
                <li><strong>来源文件</strong>：为每行数据添加来源文件名标识</li>
                <li><strong>表头预览</strong>：合并前可以预览最终的表头结构</li>
            </ul>
        """)
        
        self.description_scroll = QScrollArea()
        self.description_scroll.setWidget(self.description_text)
        self.description_scroll.setWidgetResizable(True)
        self.description_scroll.setMaximumHeight(300)
        self.description_scroll.setFixedHeight(100)  # 默认高度
        
        # 添加到主布局
        layout.addLayout(description_header_layout)
        layout.addWidget(self.description_scroll)

    def toggle_description(self):
        """
        切换插件说明的展开/收起状态
        """
        if self.description_expanded:
            self.description_scroll.setFixedHeight(50)  # 收起高度
            self.toggle_description_btn.setText("▼ 展开")
            self.description_expanded = False
        else:
            self.description_scroll.setFixedHeight(300)  # 展开高度
            self.toggle_description_btn.setText("▲ 收起")
            self.description_expanded = True

    def select_source(self):
        # 打开文件对话框，支持选择多个Excel文件
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择Excel文件",
            "",
            "Excel文件 (*.xlsx *.xls);;所有文件 (*)"
        )
        
        if file_paths:
            # 如果选择了多个文件，使用第一个文件的文件夹作为源文件夹
            # 并将所有选择的文件保存下来
            self.source_path = os.path.dirname(file_paths[0])
            self.selected_files = file_paths
            
            # 在编辑框中显示选择的文件数
            if len(file_paths) == 1:
                self.source_edit.setText(file_paths[0])
            else:
                self.source_edit.setText(f"已选择 {len(file_paths)} 个Excel文件")
            return
            
        # 如果没有选择文件，尝试选择文件夹
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择源文件夹",
            ""
        )
        
        if dir_path:
            self.source_path = dir_path
            self.selected_files = None  # 重置选择的文件列表
            self.source_edit.setText(dir_path)

    def select_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择输出文件夹",
            ""
        )
        if dir_path:
            self.output_dir = dir_path
            self.output_edit.setText(dir_path)
    
    def on_merge_header_changed(self, state):
        """
        处理合并多行表头复选框状态变化
        """
        self.header_rows_spin.setEnabled(state == 2)  # 2表示选中状态

    def merge_files(self):
        if not self.source_path:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("警告")
            msg_box.setText("请先选择源Excel文件")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
            msg_box.exec()
            return

        if not self.output_dir:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("警告")
            msg_box.setText("请先选择输出文件夹")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
            msg_box.exec()
            return

        merge_option_text = self.merge_combo.currentText()
        if merge_option_text == "合并多个文件到同一sheet":
            self.merge_option = "single_sheet"
        elif merge_option_text == "合并多个文件到多个sheet":
            self.merge_option = "multiple_sheets"
        else:
            self.merge_option = "single_file_sheets"

        try:
            # 确定源文件夹
            source_dir = self.source_path
            if self.selected_files:
                # 如果选择了文件，使用第一个文件的文件夹
                source_dir = os.path.dirname(self.selected_files[0])
            elif os.path.isfile(self.source_path):
                # 如果源路径是单个文件，使用其文件夹
                source_dir = os.path.dirname(self.source_path)
                # 将单个文件添加到选择列表
                self.selected_files = [self.source_path]
            
            # 创建合并器实例
            merger = ExcelMerger(source_dir, self.output_dir, self.selected_files)
            
            # 显示统计信息
            stats = merger.get_merge_statistics()
            if stats["total_files"] == 0:
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setWindowTitle("警告")
                msg_box.setText("没有找到Excel文件")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
                msg_box.exec()
                return

            # 获取表头处理选项
            merge_header = self.merge_header_check.isChecked()
            header_rows = self.header_rows_spin.value()
            header_mode = self.header_mode_combo.currentData()

            result = None
            if self.merge_option == "single_sheet":
                result = merger.merge_excel_files(
                    merge_header_rows=merge_header,
                    header_rows=header_rows,
                    header_mode=header_mode
                )
            elif self.merge_option == "multiple_sheets":
                result = merger.merge_with_sheet_separation(
                    merge_header_rows=merge_header,
                    header_rows=header_rows
                )
            else:
                result = merger.merge_single_file_sheets(
                    merge_header_rows=merge_header,
                    header_rows=header_rows,
                    header_mode=header_mode
                )

            if result["success"]:
                # 根据不同的合并选项生成不同的详细信息
                if self.merge_option == "single_sheet":
                    message = f"合并完成！\n"\
                              f"\n"\
                              f"源文件总数: {result['total_files']} 个\n"\
                              f"成功读取: {result['successful_files']} 个文件\n"\
                              f"读取失败: {result['failed_files']} 个文件\n"\
                              f"总处理Sheet数: {result['total_sheets']} 个\n"\
                              f"\n"\
                              f"合并结果:\n"\
                              f"总行数: {result['total_rows']} 行\n"\
                              f"总列数: {result['total_columns']} 列\n"\
                              f"\n"\
                              f"输出文件: {os.path.basename(result['output_path'])} \n"\
                              f"输出文件夹: {self.output_dir}"
                elif self.merge_option == "multiple_sheets":
                    message = f"合并完成！\n"\
                              f"\n"\
                              f"源文件总数: {result['total_files']} 个\n"\
                              f"成功读取: {result['successful_files']} 个文件\n"\
                              f"读取失败: {result['failed_files']} 个文件\n"\
                              f"总处理Sheet数: {result['total_sheets']} 个\n"\
                              f"\n"\
                              f"合并结果:\n"\
                              f"生成工作表数: {result['total_sheets']} 个\n"\
                              f"\n"\
                              f"输出文件: {os.path.basename(result['output_path'])} \n"\
                              f"输出文件夹: {self.output_dir}"
                else:
                    message = f"合并完成！\n"\
                              f"\n"\
                              f"源文件总数: {result['total_files']} 个\n"\
                              f"成功处理: {result['successful_files']} 个文件\n"\
                              f"处理失败: {result['failed_files']} 个文件\n"\
                              f"总处理Sheet数: {result['total_sheets']} 个\n"\
                              f"\n"\
                              f"合并结果:\n"\
                              f"生成文件数: {len(result['output_files'])} 个\n"\
                              f"\n"\
                              f"输出文件夹: {self.output_dir}"
                
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.setWindowTitle("合并完成")
                msg_box.setText(message)
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
                msg_box.exec()
            else:
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Icon.Critical)
                msg_box.setWindowTitle("合并失败")
                msg_box.setText(result["message"])
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
                msg_box.exec()

        except Exception as e:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("错误")
            msg_box.setText(f"合并过程中发生错误: {str(e)}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
            msg_box.exec()

    def get_widget(self) -> "ExcelMergePlugin":
        return self

    def on_activate(self):
        pass

    def preview_headers(self):
        """
        预览合并后的表头效果
        """
        if not self.source_path:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("警告")
            msg_box.setText("请先选择源Excel文件")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
            msg_box.exec()
            return

        try:
            # 确定源文件夹和选择的文件
            source_dir = self.source_path
            selected_files = self.selected_files
            if selected_files:
                source_dir = os.path.dirname(selected_files[0])
            elif os.path.isfile(self.source_path):
                source_dir = os.path.dirname(self.source_path)
                selected_files = [self.source_path]

            # 创建合并器实例
            merger = ExcelMerger(source_dir, self.output_dir, selected_files)

            # 获取统计信息
            stats = merger.get_merge_statistics()
            if stats["total_files"] == 0:
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setWindowTitle("警告")
                msg_box.setText("没有找到Excel文件")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
                msg_box.exec()
                return

            # 获取当前的表头处理设置
            merge_header = self.merge_header_check.isChecked()
            header_rows = self.header_rows_spin.value()
            header_mode = self.header_mode_combo.currentData()

            # 读取所有文件的表头信息
            excel_files = merger.get_excel_files()
            all_sheets_data_with_files = []
            all_headers_info = []

            for file_path in excel_files:
                file_name = os.path.basename(file_path)
                sheets_data = merger.read_excel_file(
                    file_path, 
                    header=0, 
                    merge_header_rows=merge_header, 
                    header_rows=header_rows
                )
                
                for sheet_data in sheets_data:
                    # 保存工作表数据及其所属文件路径
                    all_sheets_data_with_files.append((sheet_data, file_path))
                    all_headers_info.append({
                        "file": file_name,
                        "sheet": sheet_data["sheet_name"],
                        "headers": sheet_data["headers"]
                    })

            if not all_sheets_data_with_files:
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setWindowTitle("警告")
                msg_box.setText("没有成功读取任何Excel文件或sheet")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
                msg_box.exec()
                return

            # 模拟表头合并逻辑，与merge_excel_files方法中的逻辑保持一致
            all_dataframes = []
            for sheet_data, file_path in all_sheets_data_with_files:
                df = sheet_data["dataframe"]
                # 添加来源信息列，与实际合并逻辑保持一致
                df = df.copy()  # 创建副本以避免修改原始数据
                df['来源文件'] = os.path.basename(file_path)
                df['来源Sheet'] = sheet_data["sheet_name"]
                all_dataframes.append(df)

            # 根据表头模式处理合并预览
            if header_mode == "first":
                # 使用第一个sheet的表头
                preview_columns = all_dataframes[0].columns
            elif header_mode == "intersection":
                # 使用所有表头的交集
                common_columns = set(all_dataframes[0].columns)
                for df in all_dataframes[1:]:
                    common_columns.intersection_update(df.columns)
                preview_columns = sorted(list(common_columns))
            elif header_mode == "union":
                # 使用所有表头的并集
                all_columns = set()
                for df in all_dataframes:
                    all_columns.update(df.columns)
                preview_columns = sorted(list(all_columns))
            else:  # "auto" 模式
                # 自动合并，使用默认的pd.concat行为（基于列名匹配）
                # 这里我们只需要获取所有列的并集
                all_columns = set()
                for df in all_dataframes:
                    all_columns.update(df.columns)
                preview_columns = sorted(list(all_columns))

            # 准备预览信息
            preview_info = {
                "header_mode": header_mode,
                "merge_header": merge_header,
                "header_rows": header_rows,
                "total_files": stats["total_files"],
                "total_sheets": len(all_sheets_data_with_files),
                "original_headers": all_headers_info,
                "merged_headers": preview_columns
            }

            # 显示预览对话框
            self.show_header_preview_dialog(preview_info)

        except Exception as e:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("错误")
            msg_box.setText(f"预览过程中发生错误: {str(e)}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
            msg_box.exec()

    def show_header_preview_dialog(self, preview_info):
        """
        显示表头预览对话框
        
        Args:
            preview_info: 包含预览信息的字典
        """
        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("表头预览")
        dialog.setMinimumSize(600, 500)
        
        # 创建主布局
        main_layout = QVBoxLayout(dialog)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # 创建内容小部件
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # 预览设置信息
        settings_group = QGroupBox("预览设置")
        settings_layout = QVBoxLayout(settings_group)
        
        settings_text = QTextEdit()
        settings_text.setReadOnly(True)
        settings_text.setStyleSheet("font-family: monospace;")
        
        settings_content = f"""预览设置信息：
- 表头合并模式: {self.header_mode_combo.currentText()}
- 合并多行表头: {'是' if preview_info['merge_header'] else '否'}
- 表头行数: {preview_info['header_rows']}
- 源文件总数: {preview_info['total_files']} 个
- 总Sheet数: {preview_info['total_sheets']} 个
"""
        
        settings_text.setText(settings_content)
        settings_layout.addWidget(settings_text)
        content_layout.addWidget(settings_group)
        
        # 原始表头信息
        original_group = QGroupBox("原始表头信息")
        original_layout = QVBoxLayout(original_group)
        
        original_text = QTextEdit()
        original_text.setReadOnly(True)
        original_text.setStyleSheet("font-family: monospace;")
        
        original_content = ""
        for idx, header_info in enumerate(preview_info['original_headers'], 1):
            original_content += f"\n{idx}. 文件: {header_info['file']} | Sheet: {header_info['sheet']}\n"
            original_content += f"   表头: {', '.join(header_info['headers'][:10])}{'...' if len(header_info['headers']) > 10 else ''}\n"
        
        original_text.setText(original_content)
        original_layout.addWidget(original_text)
        content_layout.addWidget(original_group)
        
        # 合并后的表头
        merged_group = QGroupBox("合并后的表头效果")
        merged_layout = QVBoxLayout(merged_group)
        
        merged_text = QTextEdit()
        merged_text.setReadOnly(True)
        merged_text.setStyleSheet("font-family: monospace;")
        
        merged_content = "合并后的表头: "
        merged_content += ", ".join(preview_info['merged_headers'])
        
        merged_text.setText(merged_content)
        merged_layout.addWidget(merged_text)
        content_layout.addWidget(merged_group)
        
        # 添加内容到滚动区域
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # 添加关闭按钮
        button_box = QHBoxLayout()
        button_box.addStretch()
        
        close_button = QPushButton("关闭")
        close_button.clicked.connect(dialog.accept)
        button_box.addWidget(close_button)
        
        main_layout.addLayout(button_box)
        
        # 显示对话框
        dialog.exec()

    def on_deactivate(self):
        pass
