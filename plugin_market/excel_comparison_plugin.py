from datetime import datetime
from typing import List, Dict, Any

import pandas as pd
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QGroupBox, QMessageBox, \
    QLineEdit, QComboBox, QTextEdit, QCheckBox, QWidget, QFrame, QListWidget

from src.plugins.base_plugin import BasePlugin
from src.utils.logger import logger


class ExcelComparator:
    """
    Excel对比工具类
    用于对比两个Excel文件或同一文件的两个sheet
    支持行级、列级对比，识别新增、删除、修改的数据
    """
    
    # 长数字列关键词列表，用于识别需要特殊处理的列
    LONG_NUMBER_KEYWORDS = ['手机号', '电话', '身份证', 'ID']
    
    def __init__(self, file1_path: str, file2_path: str, sheet1_name: str = None, sheet2_name: str = None):
        """
        初始化Excel对比器
        
        Args:
            file1_path: 第一个Excel文件路径
            file2_path: 第二个Excel文件路径
            sheet1_name: 第一个文件的sheet名称，如果为None则使用第一个sheet
            sheet2_name: 第二个文件的sheet名称，如果为None则使用第一个sheet
        """
        self.file1_path = file1_path
        self.file2_path = file2_path
        self.sheet1_name = sheet1_name
        self.sheet2_name = sheet2_name
        
        # 读取Excel文件
        self.df1 = self._read_excel(file1_path, sheet1_name)
        self.df2 = self._read_excel(file2_path, sheet2_name)
        
        # 对比结果
        self.comparison_result = {
            "added_rows": None,      # 新增的行
            "deleted_rows": None,    # 删除的行
            "modified_rows": None,   # 修改的行
            "common_rows": None,     # 共同的行
            "column_changes": None,  # 列的变化
            "summary": {}
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
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str)
            else:
                # 当sheet_name为None时，read_excel会返回字典，需要获取第一个sheet
                df_dict = pd.read_excel(file_path, sheet_name=None, dtype=str)
                if not df_dict:
                    raise Exception("Excel文件中没有找到任何sheet")
                # 获取第一个sheet的数据
                df = list(df_dict.values())[0]
            
            # 不再移除.n结尾，避免误删有效数据（如版本号、价格）
            
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
            excel_file = pd.ExcelFile(file_path)
            return excel_file.sheet_names
        except Exception as e:
            raise Exception(f"获取sheet名称失败: {str(e)}")
    
    def compare(self, primary_key: List[str] = None, ignore_columns: List[str] = None) -> Dict[str, Any]:
        """
        对比两个Excel文件
        
        Args:
            primary_key: 主键列列表，用于匹配行
            ignore_columns: 忽略的列列表
            
        Returns:
            Dict[str, Any]: 对比结果
        """
        if primary_key is None:
            primary_key = []
        
        if ignore_columns is None:
            ignore_columns = []
        
        # 保存主键和忽略列作为实例属性
        self.primary_key_columns = primary_key
        self.ignore_columns = ignore_columns
        
        # 复制数据框，但保留所有列（包括忽略的列）
        df1 = self.df1.copy()
        df2 = self.df2.copy()
        
        # 保存原始数据框用于导出整行数据
        self._original_df1 = df1.copy()
        self._original_df2 = df2.copy()
        
        # 列变化分析
        columns1 = set(df1.columns)
        columns2 = set(df2.columns)
        added_columns = columns2 - columns1
        deleted_columns = columns1 - columns2
        common_columns = columns1 & columns2
        
        self.comparison_result["column_changes"] = {
            "added_columns": list(added_columns),
            "deleted_columns": list(deleted_columns),
            "common_columns": list(common_columns)
        }
        
        # 如果没有主键，使用索引进行匹配
        if not primary_key:
            # 行数对比
            max_rows = max(len(df1), len(df2))
            
            # 获取所有非忽略的列
            non_ignored_columns1 = [col for col in df1.columns if col not in ignore_columns]
            non_ignored_columns2 = [col for col in df2.columns if col not in ignore_columns]
            
            # 新增行只包含非忽略的列
            added_rows = df2.iloc[len(df1):][non_ignored_columns2] if len(df2) > len(df1) else pd.DataFrame(columns=non_ignored_columns2)
            # 删除行只包含非忽略的列
            deleted_rows = df1.iloc[len(df2):][non_ignored_columns1] if len(df1) > len(df2) else pd.DataFrame(columns=non_ignored_columns1)
            
            # 对比共同的行
            common_rows = min(len(df1), len(df2))
            modified_rows = []
            
            for i in range(common_rows):
                row1 = df1.iloc[i]
                row2 = df2.iloc[i]
                
                # 检查是否有修改（忽略指定的列）
                has_modification = False
                modified_columns = []
                
                for col in common_columns:
                    # 跳过忽略的列
                    if col in ignore_columns:
                        continue
                    
                    if str(row1[col]) != str(row2[col]):
                        has_modification = True
                        modified_columns.append(col)
                
                if has_modification:
                    modified_rows.append({
                        "index": i,
                        "old_row": row1.to_dict(),
                        "new_row": row2.to_dict(),
                        "modified_columns": modified_columns
                    })
            
            self.comparison_result["added_rows"] = added_rows
            self.comparison_result["deleted_rows"] = deleted_rows
            self.comparison_result["modified_rows"] = modified_rows
        else:
            # 检查主键列是否存在
            for key in primary_key:
                if key not in df1.columns or key not in df2.columns:
                    raise Exception(f"主键列 {key} 在一个或两个文件中不存在")
            
            # 合并数据框进行对比
            merged_df = pd.merge(
                df1, df2,
                on=primary_key,
                how='outer',
                suffixes=('_old', '_new'),
                indicator=True
            )
            
            # 分离新增、删除和修改的行
            added_rows = merged_df[merged_df['_merge'] == 'right_only']
            deleted_rows = merged_df[merged_df['_merge'] == 'left_only']
            common_rows = merged_df[merged_df['_merge'] == 'both']
            
            # 立即处理手机号等长数字列，避免科学计数法
            for col in df1.columns:
                if any(keyword in col for keyword in self.LONG_NUMBER_KEYWORDS):
                    # 处理新增行中的长数字列
                    if f'{col}_new' in added_rows.columns:
                        added_rows = added_rows.copy()
                        added_rows[f'{col}_new'] = added_rows[f'{col}_new'].apply(lambda x: 
                            str(int(x)) if pd.notna(x) and isinstance(x, float) and x.is_integer() else x)
                    
                    # 处理删除行中的长数字列
                    if f'{col}_old' in deleted_rows.columns:
                        deleted_rows = deleted_rows.copy()
                        deleted_rows[f'{col}_old'] = deleted_rows[f'{col}_old'].apply(lambda x: 
                            str(int(x)) if pd.notna(x) and isinstance(x, float) and x.is_integer() else x)
                    
                    # 处理修改行中的长数字列
                    if f'{col}_old' in common_rows.columns and f'{col}_new' in common_rows.columns:
                        common_rows = common_rows.copy()
                        common_rows[f'{col}_old'] = common_rows[f'{col}_old'].apply(lambda x: 
                            str(int(x)) if pd.notna(x) and isinstance(x, float) and x.is_integer() else x)
                        common_rows[f'{col}_new'] = common_rows[f'{col}_new'].apply(lambda x: 
                            str(int(x)) if pd.notna(x) and isinstance(x, float) and x.is_integer() else x)
            
            # 处理新增行
            added_columns_only = [col for col in added_rows.columns if col.endswith('_new')]
            # 只保留非忽略的列（添加_new后缀后）
            added_columns_only = [col for col in added_columns_only if col.replace('_new', '') not in ignore_columns]
            # 添加主键列和非忽略的新增列
            added_rows = added_rows[primary_key + added_columns_only]
            # 重命名列名，去掉_new后缀
            added_rows.columns = primary_key + [col.replace('_new', '') for col in added_columns_only]
            
            # 处理删除行
            deleted_columns_only = [col for col in deleted_rows.columns if col.endswith('_old')]
            # 只保留非忽略的列（添加_old后缀后）
            deleted_columns_only = [col for col in deleted_columns_only if col.replace('_old', '') not in ignore_columns]
            # 添加主键列和非忽略的删除列
            deleted_rows = deleted_rows[primary_key + deleted_columns_only]
            # 重命名列名，去掉_old后缀
            deleted_rows.columns = primary_key + [col.replace('_old', '') for col in deleted_columns_only]
            
            # 识别修改的行
            modified_rows = []
            
            # 获取共同的非主键列
            common_non_key_columns = [col for col in common_columns if col not in primary_key]
            
            for _, row in common_rows.iterrows():
                row_modified = False
                modified_columns = []
                old_row = {}
                new_row = {}
                
                # 获取主键值
                key_values = {key: row[key] for key in primary_key}
                
                # 对比非主键列（忽略指定的列）
                for col in common_non_key_columns:
                    # 跳过忽略的列
                    if col in ignore_columns:
                        continue
                        
                    old_val = row[f'{col}_old']
                    new_val = row[f'{col}_new']
                    
                    # 特别处理手机号等长数字列，确保完整显示
                    if any(keyword in col for keyword in self.LONG_NUMBER_KEYWORDS):
                        # 处理旧值
                        if pd.notna(old_val):
                            if isinstance(old_val, float) and old_val.is_integer():
                                old_val = int(old_val)
                        # 处理新值
                        if pd.notna(new_val):
                            if isinstance(new_val, float) and new_val.is_integer():
                                new_val = int(new_val)
                    
                    if str(old_val) != str(new_val):
                        row_modified = True
                        modified_columns.append(col)
                    
                    old_row[col] = old_val
                    new_row[col] = new_val
                
                if row_modified:
                    modified_rows.append({
                        "key_values": key_values,
                        "old_row": old_row,
                        "new_row": new_row,
                        "modified_columns": modified_columns
                    })
            
            self.comparison_result["added_rows"] = added_rows
            self.comparison_result["deleted_rows"] = deleted_rows
            self.comparison_result["modified_rows"] = modified_rows
            self.comparison_result["common_rows"] = common_rows.shape[0]
        
        # 检测重复行
        # 源文件重复行检测
        if primary_key:
            # 基于主键检测重复行
            file1_duplicates = df1[df1.duplicated(subset=primary_key, keep=False)]
            file2_duplicates = df2[df2.duplicated(subset=primary_key, keep=False)]
        else:
            # 基于整行检测重复行
            file1_duplicates = df1[df1.duplicated(keep=False)]
            file2_duplicates = df2[df2.duplicated(keep=False)]
            
        # 计算重复行数量（去除重复项后的数量）
        if primary_key:
            file1_duplicate_count = df1.duplicated(subset=primary_key, keep='first').sum()
            file2_duplicate_count = df2.duplicated(subset=primary_key, keep='first').sum()
        else:
            file1_duplicate_count = df1.duplicated(keep='first').sum()
            file2_duplicate_count = df2.duplicated(keep='first').sum()
        
        # 存储重复行信息
        self.comparison_result["duplicate_rows"] = {
            "file1_duplicates": file1_duplicates,
            "file2_duplicates": file2_duplicates,
            "file1_duplicate_count": file1_duplicate_count,
            "file2_duplicate_count": file2_duplicate_count
        }
        
        # 生成摘要
        self.comparison_result["summary"] = {
            "file1_path": self.file1_path,
            "file2_path": self.file2_path,
            "sheet1_name": self.sheet1_name or "第一个Sheet",
            "sheet2_name": self.sheet2_name or "第一个Sheet",
            "file1_rows": len(self.df1),
            "file2_rows": len(self.df2),
            "added_rows_count": len(self.comparison_result["added_rows"]),
            "deleted_rows_count": len(self.comparison_result["deleted_rows"]),
            "modified_rows_count": len(self.comparison_result["modified_rows"]),
            "file1_duplicate_count": file1_duplicate_count,
            "file2_duplicate_count": file2_duplicate_count,
            "added_columns_count": len(self.comparison_result["column_changes"]["added_columns"]),
            "deleted_columns_count": len(self.comparison_result["column_changes"]["deleted_columns"]),
            "common_columns_count": len(self.comparison_result["column_changes"]["common_columns"])
        }
        
        return self.comparison_result
    
    def _ensure_string_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        确保所有可能包含长数字的列（包括合并后产生的如"手机号_old"）都保持为字符串类型，并处理缺失值
        
        Args:
            df: 需要处理的数据框
            
        Returns:
            pd.DataFrame: 处理后的数据框
        """
        if df.empty:
            return df
            
        df = df.copy()
        for col in df.columns:
            # 将缺失值转换为空字符串
            df[col] = df[col].fillna("")
            # 检查列名是否包含可能的长数字标识
            if any(keyword in col for keyword in self.LONG_NUMBER_KEYWORDS):
                # 将列转换为字符串类型
                df[col] = df[col].astype(str)
                # 不再移除.n结尾，避免误删有效数据（如版本号、价格）
        return df
    
    def _preprocess_data_for_export(self) -> Dict[str, Any]:
        """
        预处理导出数据，避免长数字（如手机号）显示为科学计数法
        
        Returns:
            Dict[str, Any]: 处理后的数据
        """
        # 复制结果字典
        processed_result = self.comparison_result.copy()
        
        # 处理新增行
        processed_result["added_rows"] = self._ensure_string_columns(processed_result["added_rows"])
        
        # 处理删除行
        processed_result["deleted_rows"] = self._ensure_string_columns(processed_result["deleted_rows"])
        
        # 处理重复行
        if "duplicate_rows" in processed_result and processed_result["duplicate_rows"]:
            if not processed_result["duplicate_rows"]["file1_duplicates"].empty:
                processed_result["duplicate_rows"]["file1_duplicates"] = self._ensure_string_columns(processed_result["duplicate_rows"]["file1_duplicates"])
            if not processed_result["duplicate_rows"]["file2_duplicates"].empty:
                processed_result["duplicate_rows"]["file2_duplicates"] = self._ensure_string_columns(processed_result["duplicate_rows"]["file2_duplicates"])
        
        return processed_result

    def generate_comparison_report(self, output_dir: str = "comparison_result", export_full_row: bool = True) -> str:
        """
        生成对比报告
        
        Args:
            output_dir: 报告输出目录
            export_full_row: 是否导出整行数据，默认True
            
        Returns:
            str: 报告文件路径
        """
        if not self.comparison_result["summary"]:
            raise Exception("请先运行compare方法进行对比")
        
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 生成导出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"differences_export_{timestamp}.xlsx"
        output_path = os.path.join(output_dir, output_filename)
        
        try:
            # 处理数据，避免长数字（如手机号）显示为科学计数法
            processed_result = self._preprocess_data_for_export()
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # 标记是否有任何工作表被创建
                has_sheet = False
                
                # 设置长数字列为文本格式的函数
                def set_text_format_for_long_numbers(worksheet, df):
                    from openpyxl.utils import get_column_letter
                    for col in df.columns:
                        if any(keyword in col for keyword in self.LONG_NUMBER_KEYWORDS):
                            # 获取列的字母标识
                            col_idx = df.columns.get_loc(col) + 1  # Excel列索引从1开始
                            col_letter = get_column_letter(col_idx)
                            
                            # 设置整列的格式为文本
                            worksheet.column_dimensions[col_letter].number_format = '@'
                
                # 写入新增行
                if not processed_result["added_rows"].empty:
                    if export_full_row:
                        # 导出整行数据，包含所有列
                        # 新增行是新表中的行，从原始数据框中获取完整行数据
                        if not self.primary_key_columns:
                            # 无主键模式，直接使用原始数据框中的新增行
                            full_added_rows = self._original_df2.iloc[len(self.df1):]
                        else:
                            # 有主键模式，使用主键匹配获取完整行
                            primary_key_values = processed_result["added_rows"][self.primary_key_columns].values.tolist()
                            full_added_rows = pd.DataFrame()
                            for values in primary_key_values:
                                # 创建查询条件
                                conditions = [f"{col} == '{val}'" for col, val in zip(self.primary_key_columns, values)]
                                query = " and ".join(conditions)
                                # 从原始数据框中获取完整行
                                row = self._original_df2.query(query)
                                full_added_rows = pd.concat([full_added_rows, row], ignore_index=True)
                    else:
                        # 不导出整行数据，只导出主键列
                        if self.primary_key_columns:
                            full_added_rows = processed_result["added_rows"][self.primary_key_columns].copy()
                        else:
                            # 无主键模式，不导出新增行
                            full_added_rows = pd.DataFrame()  # 空数据框
                    
                    full_added_rows.to_excel(writer, sheet_name='新增行', index=False)
                    # 设置长数字列为文本格式
                    set_text_format_for_long_numbers(writer.sheets['新增行'], full_added_rows)
                    has_sheet = True
                
                # 写入删除行
                if not processed_result["deleted_rows"].empty:
                    if export_full_row:
                        # 导出整行数据，包含所有列
                        # 删除行是旧表中的行，从原始数据框中获取完整行数据
                        if not self.primary_key_columns:
                            # 无主键模式，直接使用原始数据框中的删除行
                            full_deleted_rows = self._original_df1.iloc[len(self.df2):]
                        else:
                            # 有主键模式，使用主键匹配获取完整行
                            primary_key_values = processed_result["deleted_rows"][self.primary_key_columns].values.tolist()
                            full_deleted_rows = pd.DataFrame()
                            for values in primary_key_values:
                                # 创建查询条件
                                conditions = [f"{col} == '{val}'" for col, val in zip(self.primary_key_columns, values)]
                                query = " and ".join(conditions)
                                # 从原始数据框中获取完整行
                                row = self._original_df1.query(query)
                                full_deleted_rows = pd.concat([full_deleted_rows, row], ignore_index=True)
                    else:
                        # 不导出整行数据，只导出主键列
                        if self.primary_key_columns:
                            full_deleted_rows = processed_result["deleted_rows"][self.primary_key_columns].copy()
                        else:
                            # 无主键模式，不导出删除行
                            full_deleted_rows = pd.DataFrame()  # 空数据框
                    
                    full_deleted_rows.to_excel(writer, sheet_name='删除行', index=False)
                    # 设置长数字列为文本格式
                    set_text_format_for_long_numbers(writer.sheets['删除行'], full_deleted_rows)
                    has_sheet = True
                
                # 写入修改行
                if self.comparison_result["modified_rows"]:
                    full_modified_data = []
                    
                    for row in self.comparison_result["modified_rows"]:
                        row_data = {}
                        
                        if export_full_row:
                            # 导出整行数据：包含所有列和新旧值对比
                            # 获取所有原始列（包括忽略的列）
                            all_original_columns = list(self.df2.columns)
                            
                            # 首先获取行的索引或主键值，用于从原始数据框中获取完整行
                            if "index" in row:
                                # 无主键模式，使用索引
                                index = row["index"]
                                # 从原始数据框中获取完整行
                                if index < len(self._original_df2):
                                    full_new_row = self._original_df2.iloc[index]
                                    full_old_row = self._original_df1.iloc[index]
                                else:
                                    # 索引超出范围，使用现有数据
                                    full_new_row = row["new_row"]
                                    full_old_row = row["old_row"]
                            else:
                                # 有主键模式，使用主键值从原始数据框中查找完整行
                                key_values = row["key_values"]
                                # 创建查询条件
                                query = " and ".join([f"{k} == @key_values['{k}']" for k in key_values])
                                # 从原始数据框中获取完整行
                                full_new_row = self._original_df2.query(query).iloc[0]
                                full_old_row = self._original_df1.query(query).iloc[0]
                            
                            # 添加所有原始列（包括忽略的列）并处理缺失值
                            for col in all_original_columns:
                                if col in full_new_row:
                                    # 将None/pd.NA/np.nan转换为空字符串
                                    val = full_new_row[col]
                                    if pd.isna(val) or val is None:
                                        row_data[col] = ""
                                    else:
                                        row_data[col] = val
                            
                            # 添加有变化的列的旧值（带"_旧"后缀）并处理缺失值
                            for col in row["modified_columns"]:  # 只处理有变化的列
                                if col in full_old_row:
                                    old_val = full_old_row[col]
                                    # 将None/pd.NA/np.nan转换为空字符串
                                    if pd.isna(old_val) or old_val is None:
                                        row_data[f"{col}_旧"] = ""
                                    else:
                                        row_data[f"{col}_旧"] = old_val  # 使用"列名_旧"格式
                        else:
                            # 不导出整行数据：只导出主键列
                            if "key_values" in row:
                                # 有主键模式，只导出主键列
                                for key, val in row["key_values"].items():
                                    # 将None/pd.NA/np.nan转换为空字符串
                                    if pd.isna(val) or val is None:
                                        row_data[key] = ""
                                    else:
                                        row_data[key] = val
                            else:
                                # 无主键模式，不导出修改行（因为没有主键标识）
                                continue
                        
                        full_modified_data.append(row_data)
                    
                    # 如果没有生成任何数据（如无主键模式且不导出整行数据），则跳过
                    if not full_modified_data:
                        pass
                    else:
                        # 创建DataFrame
                        full_modified_df = pd.DataFrame(full_modified_data)
                        
                        if export_full_row:
                            # 导出整行数据时，调整列的顺序：使用新表的原始列顺序，然后追加旧值列
                            # 获取新表的完整列顺序
                            new_table_columns = list(self.df2.columns)
                            
                            # 获取列名列表
                            all_columns = list(full_modified_df.columns)
                            
                            # 分离新表列和旧值列
                            # 确保新表列与新表原始顺序一致
                            new_columns = [col for col in new_table_columns if col in all_columns]
                            old_columns = [col for col in all_columns if col.endswith("_旧")]
                            
                            # 组合新的列顺序：新表数据列 -> 旧值列
                            new_column_order = new_columns + old_columns
                            
                            # 重新排序DataFrame的列
                            full_modified_df = full_modified_df[new_column_order]
                        
                        # 直接使用转换后的DataFrame写入Excel
                        full_modified_df.to_excel(writer, sheet_name='修改行', index=False)
                        
                        # 设置长数字列为文本格式
                        set_text_format_for_long_numbers(writer.sheets['修改行'], full_modified_df)
                        has_sheet = True
                
                # 写入共同行
                common_rows_df = pd.DataFrame()
                if self.primary_key_columns:
                    # 有主键情况：共同行是指在两个文件中都存在的主键对应的行
                    if self.comparison_result["common_rows"] is not None:
                        # 使用合并数据获取共同行
                        merged_df = pd.merge(
                            self.df1, self.df2,
                            on=self.primary_key_columns,
                            how='inner'
                        )
                        
                        if not merged_df.empty:
                            # 从新表中获取完整的共同行数据
                            common_rows_df = self.df2[self.df2[self.primary_key_columns].apply(tuple, axis=1).isin(merged_df[self.primary_key_columns].apply(tuple, axis=1))]
                else:
                    # 无主键情况：共同行是指两个文件中相同索引位置的行
                    min_rows = min(len(self.df1), len(self.df2))
                    if min_rows > 0:
                        common_rows_df = self.df2.iloc[:min_rows]
                
                # 处理共同行数据
                if not common_rows_df.empty:
                    # 如果导出整行数据，则使用完整数据；否则只使用主键列
                    if not export_full_row and self.primary_key_columns:
                        common_rows_df = common_rows_df[self.primary_key_columns].copy()
                    
                    common_rows_df = self._ensure_string_columns(common_rows_df)
                    common_rows_df.to_excel(writer, sheet_name='共同行', index=False)
                    # 设置长数字列为文本格式
                    set_text_format_for_long_numbers(writer.sheets['共同行'], common_rows_df)
                    has_sheet = True
                else:
                    # 创建空的共同行sheet
                    if self.primary_key_columns:
                        # 有主键情况，使用新表的列名
                        columns = list(self.df2.columns)
                    else:
                        # 无主键情况，使用新表的列名
                        columns = list(self.df2.columns)
                    
                    if not export_full_row and self.primary_key_columns:
                        # 不导出整行数据时，只显示主键列
                        columns = [col for col in columns if col in self.primary_key_columns]
                    
                    empty_common_df = pd.DataFrame(columns=columns)
                    empty_common_df.to_excel(writer, sheet_name='共同行', index=False)
                    has_sheet = True
                
                # 写入重复行
                if export_full_row:  # 只有在导出整行数据时才导出重复行
                    # 只保留目标文件重复行sheet
                    if not processed_result["duplicate_rows"]["file2_duplicates"].empty:
                        processed_result["duplicate_rows"]["file2_duplicates"].to_excel(writer, sheet_name='目标文件重复行', index=False)
                        # 设置长数字列为文本格式
                        set_text_format_for_long_numbers(writer.sheets['目标文件重复行'], processed_result["duplicate_rows"]["file2_duplicates"])
                        has_sheet = True
                
                # 如果没有创建任何工作表，则创建一个包含"无差异"信息的工作表
                if not has_sheet:
                    no_diff_df = pd.DataFrame([{"结果": "无差异数据"}])
                    no_diff_df.to_excel(writer, sheet_name='结果', index=False)
        
        except Exception as e:
            raise Exception(f"导出失败: {str(e)}")
        
        return output_path


class ExcelComparisonPlugin(BasePlugin):
    """
    Excel表格对比插件
    支持行级、列级对比，对比出新增、删除、修改的数据
    """

    # 插件元数据
    PLUGIN_INFO = {
        "name": "表格对比",
        "description": "对比两个Excel文件，识别新增、删除、修改的数据",
        "version": "1.0.0",
        "author": "",
        "category": "数据处理",
        "icon": ""
    }

    def __init__(self):
        super().__init__()

        self.file1_path = ""
        self.file2_path = ""
        self.sheet1_name = None
        self.sheet2_name = None
        self.primary_key_columns = []
        self.ignore_columns = []

        self.comparator = None
        self.comparison_result = None

        self._setup_ui()
    
    def on_activate(self):
        """
        插件被激活时调用
        """
        logger.info("Excel表格对比插件被激活")
    
    def get_widget(self) -> QWidget:
        return self
    
    def _setup_ui(self):
        """
        设置UI界面
        """
        # 使用基类提供的内容布局
        layout = self.get_content_layout()

        # 文件选择区域
        file_group = QGroupBox("选择文件")
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
        
        # 文件1选择
        file1_layout = QHBoxLayout()
        file1_label = QLabel("源文件 (旧版本):")
        file1_label.setStyleSheet("font-size: 14px; min-width: 100px;")
        self.file1_edit = QLineEdit()
        self.file1_edit.setPlaceholderText("请选择源Excel文件")
        self.file1_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                color: #2c3e50;
            }
        """)
        self.select_file1_btn = QPushButton("选择文件")
        self.select_file1_btn.setStyleSheet("""
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
        self.select_file1_btn.clicked.connect(self.select_file1)
        
        file1_layout.addWidget(file1_label)
        file1_layout.addWidget(self.file1_edit, 1)
        file1_layout.addWidget(self.select_file1_btn)
        
        # 文件1 Sheet选择
        sheet1_layout = QHBoxLayout()
        sheet1_label = QLabel("Sheet:")
        sheet1_label.setStyleSheet("font-size: 14px; min-width: 100px;")
        self.sheet1_combo = QComboBox()
        self.sheet1_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        sheet1_layout.addWidget(sheet1_label)
        sheet1_layout.addWidget(self.sheet1_combo, 1)
        
        file_layout.addLayout(file1_layout)
        file_layout.addLayout(sheet1_layout)
        file_layout.addSpacing(10)
        
        # 文件2选择
        file2_layout = QHBoxLayout()
        file2_label = QLabel("目标文件 (新版本):")
        file2_label.setStyleSheet("font-size: 14px; min-width: 100px;")
        self.file2_edit = QLineEdit()
        self.file2_edit.setPlaceholderText("请选择目标Excel文件")
        self.file2_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                color: #2c3e50;
            }
        """)
        self.select_file2_btn = QPushButton("选择文件")
        self.select_file2_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.select_file2_btn.clicked.connect(self.select_file2)
        
        file2_layout.addWidget(file2_label)
        file2_layout.addWidget(self.file2_edit, 1)
        file2_layout.addWidget(self.select_file2_btn)
        
        # 文件2 Sheet选择
        sheet2_layout = QHBoxLayout()
        sheet2_label = QLabel("Sheet:")
        sheet2_label.setStyleSheet("font-size: 14px; min-width: 100px;")
        self.sheet2_combo = QComboBox()
        self.sheet2_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        sheet2_layout.addWidget(sheet2_label)
        sheet2_layout.addWidget(self.sheet2_combo, 1)
        
        file_layout.addLayout(file2_layout)
        file_layout.addLayout(sheet2_layout)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 对比选项
        option_group = QGroupBox("对比选项")
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
        
        # 主键选择
        primary_key_layout = QHBoxLayout()
        primary_key_label = QLabel("主键列:")
        primary_key_label.setStyleSheet("font-size: 14px; min-width: 80px;")
        self.primary_key_list = QListWidget()
        self.primary_key_list.setStyleSheet("""
            QListWidget {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        self.primary_key_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.primary_key_list.setFixedHeight(100)
        self.primary_key_list.setSelectionBehavior(QListWidget.SelectionBehavior.SelectRows)
        self.primary_key_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        
        primary_key_layout.addWidget(primary_key_label)
        primary_key_layout.addWidget(self.primary_key_list, 1)
        option_layout.addLayout(primary_key_layout)
        
        # 忽略列选择
        ignore_layout = QHBoxLayout()
        ignore_label = QLabel("忽略列:")
        ignore_label.setStyleSheet("font-size: 14px; min-width: 80px;")
        self.ignore_columns_list = QListWidget()
        self.ignore_columns_list.setStyleSheet("""
            QListWidget {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        self.ignore_columns_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.ignore_columns_list.setFixedHeight(100)
        self.ignore_columns_list.setSelectionBehavior(QListWidget.SelectionBehavior.SelectRows)
        self.ignore_columns_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        
        ignore_layout.addWidget(ignore_label)
        ignore_layout.addWidget(self.ignore_columns_list, 1)
        option_layout.addLayout(ignore_layout)
        
        option_group.setLayout(option_layout)
        layout.addWidget(option_group)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.compare_btn = QPushButton("开始对比")
        self.compare_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.compare_btn.clicked.connect(self.compare_files)
        self.compare_btn.setEnabled(False)
        
        # 导出整行数据选项
        self.export_full_row_checkbox = QCheckBox("导出整行数据")
        self.export_full_row_checkbox.setStyleSheet("font-size: 14px; margin-left: 10px;")
        self.export_full_row_checkbox.setChecked(True)  # 默认选中
        
        self.report_btn = QPushButton("导出结果")
        self.report_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
                margin-left: 10px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.report_btn.clicked.connect(self.generate_report)
        self.report_btn.setEnabled(False)
        
        button_layout.addWidget(self.compare_btn)
        button_layout.addWidget(self.export_full_row_checkbox)
        button_layout.addWidget(self.report_btn)
        
        layout.addLayout(button_layout)
        
        # 对比结果显示
        self.result_widget = QWidget()
        self.result_layout = QVBoxLayout(self.result_widget)
        self.result_layout.setContentsMargins(0, 0, 0, 0)
        
        # 摘要信息
        self.summary_label = QLabel("请先选择文件并点击开始对比")
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
        
        # 添加插件说明
        description_html = """
            <h3>Excel表格对比插件功能介绍</h3>
            <ul>
                <li><strong>文件对比</strong>：支持对比两个Excel文件，识别数据变化</li>
                <li><strong>行级对比</strong>：
                    <ul>
                        <li>识别新增行</li>
                        <li>识别删除行</li>
                        <li>识别修改行</li>
                    </ul>
                </li>
                <li><strong>列级对比</strong>：
                    <ul>
                        <li>识别新增列</li>
                        <li>识别删除列</li>
                        <li>识别修改的列内容</li>
                    </ul>
                </li>
                <li><strong>灵活配置</strong>：
                    <ul>
                        <li>支持选择主键列进行精确匹配</li>
                        <li>支持设置忽略列</li>
                        <li>支持选择不同的Sheet进行对比</li>
                    </ul>
                </li>
                <li><strong>报告生成</strong>：自动生成详细的对比报告</li>
            </ul>
        """

        description_header_layout, _, _, description_scroll = self.create_description_section(description_html)

        # 添加到主布局
        layout.addLayout(description_header_layout)
        layout.addWidget(description_scroll)
    
    def select_file1(self):
        """
        选择源文件
        """
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "选择源Excel文件",
            self.last_dir,
            "Excel文件 (*.xlsx *.xls);;所有文件 (*)"
        )
        
        if file_path:
            self.last_dir = os.path.dirname(file_path)
            self.file1_path = file_path
            self.file1_edit.setText(file_path)
            
            # 加载Sheet列表
            try:
                self.comparator = ExcelComparator(file_path, file_path)  # 临时创建
                sheet_names = self.comparator.get_sheet_names(file_path)
                self.sheet1_combo.clear()
                self.sheet1_combo.addItems(sheet_names)
                self.sheet1_name = sheet_names[0]
                
                # 加载列名并过滤掉Unnamed列
                df = pd.read_excel(file_path, sheet_name=sheet_names[0])
                columns = [col for col in df.columns.tolist() if not col.startswith('Unnamed:')]
                self.primary_key_list.clear()
                self.primary_key_list.addItems(columns)
                self.ignore_columns_list.clear()
                self.ignore_columns_list.addItems(columns)
            except Exception as e:
                QMessageBox.warning(self, "加载失败", f"加载文件信息失败: {str(e)}")
            
            self._check_enable_compare()
    
    def select_file2(self):
        """
        选择目标文件
        """
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "选择目标Excel文件",
            self.last_dir,
            "Excel文件 (*.xlsx *.xls);;所有文件 (*)"
        )
        
        if file_path:
            self.last_dir = os.path.dirname(file_path)
            self.file2_path = file_path
            self.file2_edit.setText(file_path)
            
            # 加载Sheet列表
            try:
                self.comparator = ExcelComparator(self.file1_path, file_path) if self.file1_path else ExcelComparator(file_path, file_path)
                sheet_names = self.comparator.get_sheet_names(file_path)
                self.sheet2_combo.clear()
                self.sheet2_combo.addItems(sheet_names)
                self.sheet2_name = sheet_names[0]
                
                # 如果两个文件都已选择，更新主键下拉框，只显示共有的列名
                if self.file1_path:
                    # 读取两个文件的第一个Sheet的列名
                    df1 = pd.read_excel(self.file1_path, sheet_name=self.sheet1_name)
                    df2 = pd.read_excel(file_path, sheet_name=self.sheet2_name)
                    
                    # 获取共有的列名并过滤掉Unnamed列，保持与第一个表格相同的顺序
                    df2_columns = set(df2.columns)
                    common_columns = [col for col in df1.columns.tolist() if col in df2_columns and not col.startswith('Unnamed:')]
                    
                    # 更新主键列表
                    self.primary_key_list.clear()
                    self.primary_key_list.addItems(common_columns)
                    
                    # 更新忽略列列表
                    self.ignore_columns_list.clear()
                    self.ignore_columns_list.addItems(common_columns)
                    
                    # 默认选择第一个共同列名作为主键列
                    if common_columns:
                        # 选择第一个共同列作为主键
                        item = self.primary_key_list.item(0)
                        if item:
                            item.setSelected(True)
                        # 忽略列列表默认不选择任何列
                        self.ignore_columns_list.clearSelection()
                    
                    if not common_columns:
                        QMessageBox.warning(self, "警告", "两个文件没有共同的列名，将使用索引进行对比")
            except Exception as e:
                QMessageBox.warning(self, "加载失败", f"加载文件信息失败: {str(e)}")
            
            self._check_enable_compare()
    
    def _toggle_item_selection(self, item):
        """
        切换项目的选择状态
        """
        # PyQt的itemClicked信号在默认选择行为之后触发，所以我们需要取反
        if item.isSelected():
            # 如果已选中，则取消选择
            item.setSelected(False)
        else:
            # 如果未选中，则选中
            item.setSelected(True)
    
    def _check_enable_compare(self):
        """
        检查是否可以启用对比按钮
        """
        self.compare_btn.setEnabled(bool(self.file1_path and self.file2_path))
    
    def compare_files(self):
        """
        开始对比文件
        """
        if not self.file1_path or not self.file2_path:
            QMessageBox.warning(self, "警告", "请先选择两个Excel文件")
            return
        
        # 获取对比参数
        # 获取选中的主键列
        primary_key = [item.text() for item in self.primary_key_list.selectedItems()]
        # 获取选中的忽略列
        ignore_columns = [item.text() for item in self.ignore_columns_list.selectedItems()]
        
        # 验证主键列和忽略列不能有重叠
        if set(primary_key) & set(ignore_columns):
            QMessageBox.warning(self, "警告", "主键列和忽略列不能重叠，请重新选择")
            return
        
        try:
            # 创建对比器
            self.comparator = ExcelComparator(
                self.file1_path, 
                self.file2_path, 
                self.sheet1_combo.currentText(), 
                self.sheet2_combo.currentText()
            )
            
            # 执行对比
            self.comparison_result = self.comparator.compare(primary_key, ignore_columns)
            
            # 更新结果显示
            self._update_result_display()
            
            # 启用生成报告按钮
            self.report_btn.setEnabled(True)
            
            QMessageBox.information(self, "对比完成", "Excel文件对比完成")
            
        except Exception as e:
            QMessageBox.critical(self, "对比失败", f"对比过程中发生错误: {str(e)}")
            logger.info(f"对比错误: {str(e)}")
    
    def _update_result_display(self):
        """
        更新对比结果显示
        """
        if not self.comparison_result:
            return
        
        summary = self.comparison_result["summary"]
        
        # 更新摘要信息
        summary_text = f"""
对比摘要：
源文件: {os.path.basename(summary['file1_path'])} (Sheet: {summary['sheet1_name']})
目标文件: {os.path.basename(summary['file2_path'])} (Sheet: {summary['sheet2_name']})
源文件行数: {summary['file1_rows']}
目标文件行数: {summary['file2_rows']}

行变化：
新增行: {summary['added_rows_count']}
删除行: {summary['deleted_rows_count']}
修改行: {summary['modified_rows_count']}
源文件重复行: {summary['file1_duplicate_count']}
目标文件重复行: {summary['file2_duplicate_count']}

列变化：
新增列: {summary['added_columns_count']}
删除列: {summary['deleted_columns_count']}
共同列: {summary['common_columns_count']}
        """.strip()
        
        self.summary_label.setText(summary_text)
    
    def generate_report(self):
        """
        生成对比报告
        """
        if not self.comparison_result:
            QMessageBox.warning(self, "警告", "请先完成文件对比")
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
            # 获取导出整行数据选项
            export_full_row = self.export_full_row_checkbox.isChecked()
            
            # 生成报告
            report_path = self.comparator.generate_comparison_report(output_dir, export_full_row=export_full_row)
            
            QMessageBox.information(
                self,
                "结果导出成功",
                f"差异数据已导出：\n{report_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出差异数据时发生错误: {str(e)}")
            logger.info(f"导出错误: {str(e)}")


if __name__ == "__main__":
    """
    用于测试修复的主函数
    """
    import sys
    import os
    
    # 测试文件路径
    file1_path = '/Users/sunxiaogang/study/pyproject/pyqt/x-tool/plugins/1.xlsx'
    file2_path = '/Users/sunxiaogang/study/pyproject/pyqt/x-tool/plugins/2.xlsx'
    
    if not os.path.exists(file1_path) or not os.path.exists(file2_path):
        logger.info(f"测试文件不存在：{file1_path} 或 {file2_path}")
        sys.exit(1)
    
    try:
        logger.info("开始测试修复...")
        
        # 创建对比器
        comparator = ExcelComparator(file1_path, file2_path)
        
        # 设置主键列
        primary_key = ['姓名']
        ignore_columns = []
        
        # 执行对比
        logger.info("执行文件对比...")
        result = comparator.compare(primary_key=primary_key, ignore_columns=ignore_columns)
        
        logger.info("对比完成，开始生成报告...")
        
        # 生成报告
        output_dir = 'fix_test_output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 测试导出整行数据
        report_path_full = comparator.generate_comparison_report(output_dir=output_dir, export_full_row=True)
        logger.info(f"✓ 导出整行数据报告成功: {report_path_full}")
        
        logger.info("\n✅ 修复验证成功！导出功能正常工作")
        
    except Exception as e:
        logger.info(f"\n❌ 修复验证失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
