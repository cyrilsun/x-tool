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
    
    def __init__(self, source_dir: str = "doc", output_dir: str = "merged"):
        """
        初始化Excel合并器
        
        Args:
            source_dir: 源Excel文件目录
            output_dir: 合并后文件输出目录
        """
        self.source_dir = source_dir
        self.output_dir = output_dir
        
        # 确保输出目录存在
        self._ensure_output_directory()
    
    def _ensure_output_directory(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"创建输出目录: {self.output_dir}")
    
    def get_excel_files(self) -> List[str]:
        """
        获取源目录下的所有Excel文件
        
        Returns:
            List[str]: Excel文件路径列表
        """
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
        
        print(f"找到 {len(excel_files)} 个Excel文件")
        return excel_files
    
    def read_excel_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        读取单个Excel文件
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            Optional[pd.DataFrame]: 读取的数据框，失败时返回None
        """
        try:
            # 尝试读取Excel文件
            df = pd.read_excel(file_path)
            print(f"✓ 成功读取: {os.path.basename(file_path)} ({len(df)} 行)")
            return df
        except Exception as e:
            print(f"✗ 读取失败: {os.path.basename(file_path)}, 错误: {str(e)}")
            return None
    
    def merge_excel_files(self, output_filename: Optional[str] = None) -> bool:
        """
        合并所有Excel文件
        
        Args:
            output_filename: 输出文件名，如果为None则自动生成
            
        Returns:
            bool: 合并是否成功
        """
        # 获取所有Excel文件
        excel_files = self.get_excel_files()
        
        if not excel_files:
            print("没有找到Excel文件，无法进行合并")
            return False
        
        # 生成输出文件名
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"merged_excel_{timestamp}.xlsx"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        print(f"开始合并 {len(excel_files)} 个Excel文件...")
        print("=" * 60)
        
        # 存储所有数据框
        all_dataframes = []
        successful_files = 0
        failed_files = 0
        
        # 读取所有Excel文件
        for i, file_path in enumerate(excel_files, 1):
            print(f"[{i}/{len(excel_files)}] 处理: {os.path.basename(file_path)}")
            
            df = self.read_excel_file(file_path)
            if df is not None:
                # 添加来源文件信息列
                df['来源文件'] = os.path.basename(file_path)
                all_dataframes.append(df)
                successful_files += 1
            else:
                failed_files += 1
        
        if not all_dataframes:
            print("没有成功读取任何Excel文件，无法进行合并")
            return False
        
        try:
            # 合并所有数据框
            print(f"\n正在合并 {len(all_dataframes)} 个数据框...")
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
            
            # 显示列信息
            print(f"\n列信息:")
            for i, col in enumerate(merged_df.columns, 1):
                print(f"  {i}. {col}")
            
            return True
            
        except Exception as e:
            print(f"✗ 合并失败: {str(e)}")
            return False
    
    def merge_with_sheet_separation(self, output_filename: Optional[str] = None) -> bool:
        """
        合并Excel文件，每个源文件作为一个单独的工作表
        
        Args:
            output_filename: 输出文件名，如果为None则自动生成
            
        Returns:
            bool: 合并是否成功
        """
        # 获取所有Excel文件
        excel_files = self.get_excel_files()
        
        if not excel_files:
            print("没有找到Excel文件，无法进行合并")
            return False
        
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
                
                for i, file_path in enumerate(excel_files, 1):
                    print(f"[{i}/{len(excel_files)}] 处理: {os.path.basename(file_path)}")
                    
                    df = self.read_excel_file(file_path)
                    if df is not None:
                        # 生成工作表名称（去除文件扩展名）
                        sheet_name = os.path.splitext(os.path.basename(file_path))[0]
                        
                        # 如果工作表名称过长，截断它
                        if len(sheet_name) > 31:  # Excel工作表名称最大31个字符
                            sheet_name = sheet_name[:31]
                        
                        # 写入工作表
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        successful_files += 1
                    else:
                        failed_files += 1
            
            print("=" * 60)
            print(f"✓ 合并完成!")
            print(f"输出文件: {output_path}")
            print(f"成功处理: {successful_files} 个文件")
            print(f"处理失败: {failed_files} 个文件")
            
            return True
            
        except Exception as e:
            print(f"✗ 合并失败: {str(e)}")
            return False
    
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
        super().__init__("多表合并", "合并多个Excel文件到一个文件")

        self.source_dir = ""
        self.output_dir = ""
        self.merge_option = "single_sheet"  # "single_sheet" 或 "multiple_sheets"
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        source_group = QGroupBox("目标文件夹")
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
        self.source_edit.setPlaceholderText("请选择包含Excel文件的目标文件夹")
        self.source_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        source_layout.addWidget(self.source_edit)

        self.select_source_btn = QPushButton("选择目标文件夹")
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
        self.select_source_btn.clicked.connect(self.select_source_dir)
        source_layout.addWidget(self.select_source_btn)

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
        self.merge_combo.addItem("合并到同一sheet")
        self.merge_combo.addItem("合并到多sheet")
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

    def select_source_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择目标文件夹",
            ""
        )
        if dir_path:
            self.source_dir = dir_path
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
        if not self.source_dir:
            QMessageBox.warning(self, "警告", "请先选择目标文件夹")
            return

        if not self.output_dir:
            QMessageBox.warning(self, "警告", "请先选择输出目录")
            return

        merge_option_text = self.merge_combo.currentText()
        if merge_option_text == "合并到同一sheet":
            self.merge_option = "single_sheet"
        else:
            self.merge_option = "multiple_sheets"

        try:
            # 创建合并器实例
            merger = ExcelMerger(self.source_dir, self.output_dir)
            
            # 显示统计信息
            stats = merger.get_merge_statistics()
            if stats["total_files"] == 0:
                QMessageBox.warning(self, "警告", "在目标文件夹中没有找到Excel文件")
                return

            result = False
            if self.merge_option == "single_sheet":
                result = merger.merge_excel_files()
            else:
                result = merger.merge_with_sheet_separation()

            if result:
                QMessageBox.information(
                    self,
                    "合并完成",
                    f"成功合并 {stats['total_files']} 个Excel文件到 {self.output_dir} 目录"
                )
            else:
                QMessageBox.critical(self, "合并失败", "合并过程中发生错误，请检查控制台输出")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"合并过程中发生错误: {str(e)}")

    def get_widget(self) -> "ExcelMergePlugin":
        return self

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass
