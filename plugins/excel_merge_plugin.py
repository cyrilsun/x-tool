import os
import pandas as pd
import glob
from typing import List, Optional
from datetime import datetime
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QGroupBox, QMessageBox, QLineEdit, QComboBox

from src.plugins.base_plugin import BasePlugin


class ExcelMerger:
    """
    Excel合并工具类
    用于将doc目录下的所有Excel文件合并成一个新的Excel文件
    """
    
    def __init__(self, source_dir: str = "doc", output_dir: str = "merged", selected_files: Optional[List[str]] = None):
        """
        初始化Excel合并器
        
        Args:
            source_dir: 源Excel文件目录
            output_dir: 合并后文件输出目录
            selected_files: 用户选择的文件列表，如果提供则优先使用
        """
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.selected_files = selected_files
        
        # 确保输出目录存在
        self._ensure_output_directory()
    
    def _ensure_output_directory(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"创建输出目录: {self.output_dir}")
    
    def get_excel_files(self) -> List[str]:
        """
        获取Excel文件列表
        如果提供了selected_files，则直接返回该列表
        否则从源目录下查找所有Excel文件
        
        Returns:
            List[str]: Excel文件路径列表
        """
        # 如果提供了选择的文件列表，直接返回
        if self.selected_files:
            print(f"使用用户选择的 {len(self.selected_files)} 个Excel文件")
            return self.selected_files
        
        # 否则从源目录下查找所有Excel文件
        if not os.path.exists(self.source_dir):
            print(f"警告: 源目录 {self.source_dir} 不存在")
            return []
        
        # 查找所有Excel文件
        excel_patterns = ["*.xlsx", "*.xls"]
        excel_files = []
        
        for pattern in excel_patterns:
            files = glob.glob(os.path.join(self.source_dir, pattern))
            excel_files.extend(files)
        
        # 按文件名排序
        excel_files.sort()
        
        print(f"在源目录中找到 {len(excel_files)} 个Excel文件")
        return excel_files
    
    def read_excel_file(self, file_path: str) -> List[dict]:
        """
        读取单个Excel文件中的所有sheet
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            List[dict]: 包含sheet名称和数据框的字典列表，格式为[{"sheet_name": str, "dataframe": pd.DataFrame}]
        """
        try:
            # 获取文件中的所有sheet
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            file_name = os.path.basename(file_path)
            
            result = []
            
            for sheet_name in sheet_names:
                try:
                    # 读取单个sheet，将所有列解析为字符串以避免长数字的科学计数法和精度丢失问题
                    df = pd.read_excel(excel_file, sheet_name=sheet_name, dtype=str)
                    print(f"✓ 成功读取: {file_name} - {sheet_name} ({len(df)} 行)")
                    result.append({
                        "sheet_name": sheet_name,
                        "dataframe": df
                    })
                except Exception as e:
                    print(f"✗ 读取sheet失败: {file_name} - {sheet_name}, 错误: {str(e)}")
            
            return result
        except Exception as e:
            print(f"✗ 读取文件失败: {os.path.basename(file_path)}, 错误: {str(e)}")
            return []
    
    def merge_excel_files(self, output_filename: Optional[str] = None) -> dict:
        """
        合并所有Excel文件，将所有文件的所有sheet合并到同一个sheet
        
        Args:
            output_filename: 输出文件名，如果为None则自动生成
            
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
        
        # 读取所有Excel文件
        for i, file_path in enumerate(excel_files, 1):
            file_name = os.path.basename(file_path)
            print(f"[{i}/{len(excel_files)}] 处理: {file_name}")
            
            sheets_data = self.read_excel_file(file_path)
            if sheets_data:
                successful_files += 1
                total_sheets += len(sheets_data)
                
                # 处理每个sheet
                for sheet_data in sheets_data:
                    df = sheet_data["dataframe"]
                    sheet_name = sheet_data["sheet_name"]
                    
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
            merged_df = pd.concat(all_dataframes, ignore_index=True)
            
            # 保存合并后的文件
            merged_df.to_excel(output_path, index=False, engine='openpyxl')
            
            print("=" * 60)
            print(f"✓ 合并完成!")
            print(f"输出文件: {output_path}")
            print(f"总行数: {len(merged_df)}")
            print(f"总列数: {len(merged_df.columns)}")
            print(f"成功读取: {successful_files} 个文件")
            print(f"读取失败: {failed_files} 个文件")
            print(f"总处理sheet数: {total_sheets}")
            
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
    
    def merge_with_sheet_separation(self, output_filename: Optional[str] = None) -> dict:
        """
        合并Excel文件，每个源文件的每个sheet作为一个单独的工作表
        
        Args:
            output_filename: 输出文件名，如果为None则自动生成
            
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
                    
                    sheets_data = self.read_excel_file(file_path)
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
    
    def merge_single_file_sheets(self) -> dict:
        """
        合并同一Excel文件中的多个sheet到一个新的Excel文件
        每个源文件生成一个对应的合并文件
        
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
                sheets_data = self.read_excel_file(file_path)
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
                
                # 合并所有数据框
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

        self.source_path = ""  # 可以是文件路径或目录路径
        self.selected_files = None  # 保存用户选择的文件列表
        self.output_dir = ""
        self.merge_option = "single_sheet"  # "single_sheet", "multiple_sheets", 或 "single_file_sheets"
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        source_group = QGroupBox("选择源目录/文件")
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
        self.source_edit.setPlaceholderText("请选择包含Excel文件的目标文件夹或Excel文件")
        self.source_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        source_layout.addWidget(self.source_edit)

        self.select_source_btn = QPushButton("选择目标文件夹/文件")
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

        output_group = QGroupBox("选择输出目录")
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
        self.output_edit.setPlaceholderText("请选择输出目录")
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
        option_layout.addWidget(self.merge_combo)

        option_group.setLayout(option_layout)
        layout.addWidget(option_group)

        merge_layout = QHBoxLayout()
        merge_layout.addStretch()

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

    def select_source(self):
        # 打开文件对话框，支持选择多个Excel文件
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择Excel文件",
            "",
            "Excel文件 (*.xlsx *.xls);;所有文件 (*)"
        )
        
        if file_paths:
            # 如果选择了多个文件，使用第一个文件的目录作为源目录
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
            "选择目标文件夹",
            ""
        )
        
        if dir_path:
            self.source_path = dir_path
            self.selected_files = None  # 重置选择的文件列表
            self.source_edit.setText(dir_path)

    def select_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择输出目录",
            ""
        )
        if dir_path:
            self.output_dir = dir_path
            self.output_edit.setText(dir_path)

    def merge_files(self):
        if not self.source_path:
            QMessageBox.warning(self, "警告", "请先选择目标文件夹或Excel文件")
            return

        if not self.output_dir:
            QMessageBox.warning(self, "警告", "请先选择输出目录")
            return

        merge_option_text = self.merge_combo.currentText()
        if merge_option_text == "合并多个文件到同一sheet":
            self.merge_option = "single_sheet"
        elif merge_option_text == "合并多个文件到多个sheet":
            self.merge_option = "multiple_sheets"
        else:
            self.merge_option = "single_file_sheets"

        try:
            # 确定源目录
            source_dir = self.source_path
            if self.selected_files:
                # 如果选择了文件，使用第一个文件的目录
                source_dir = os.path.dirname(self.selected_files[0])
            elif os.path.isfile(self.source_path):
                # 如果源路径是单个文件，使用其目录
                source_dir = os.path.dirname(self.source_path)
                # 将单个文件添加到选择列表
                self.selected_files = [self.source_path]
            
            # 创建合并器实例
            merger = ExcelMerger(source_dir, self.output_dir, self.selected_files)
            
            # 显示统计信息
            stats = merger.get_merge_statistics()
            if stats["total_files"] == 0:
                QMessageBox.warning(self, "警告", "没有找到Excel文件")
                return

            result = None
            if self.merge_option == "single_sheet":
                result = merger.merge_excel_files()
            elif self.merge_option == "multiple_sheets":
                result = merger.merge_with_sheet_separation()
            else:
                result = merger.merge_single_file_sheets()

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
                              f"输出目录: {self.output_dir}"
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
                              f"输出目录: {self.output_dir}"
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
                              f"输出目录: {self.output_dir}"
                
                QMessageBox.information(
                    self,
                    "合并完成",
                    message
                )
            else:
                QMessageBox.critical(self, "合并失败", result["message"])

        except Exception as e:
            QMessageBox.critical(self, "错误", f"合并过程中发生错误: {str(e)}")

    def get_widget(self) -> "ExcelMergePlugin":
        return self

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass
