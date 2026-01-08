#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Excel合并插件的表头预览功能
"""

import os
import pandas as pd
import tempfile
from plugins.excel_merge_plugin import ExcelMerger


def create_test_excel_files(temp_dir):
    """
    创建测试用的Excel文件
    """
    print(f"创建测试文件到临时目录: {temp_dir}")
    
    # 测试文件1: 普通表头
    df1 = pd.DataFrame({
        '姓名': ['张三', '李四', '王五'],
        '年龄': [25, 30, 35],
        '部门': ['技术部', '市场部', '财务部']
    })
    df1.to_excel(os.path.join(temp_dir, 'test1.xlsx'), index=False)
    
    # 测试文件2: 不同的表头顺序
    df2 = pd.DataFrame({
        '姓名': ['赵六', '孙七', '周八'],
        '部门': ['销售部', '研发部', '人力资源部'],
        '年龄': [28, 32, 40],
        '职位': ['专员', '经理', '总监']  # 额外的列
    })
    df2.to_excel(os.path.join(temp_dir, 'test2.xlsx'), index=False)
    
    # 测试文件3: 多行表头
    df3_raw = pd.DataFrame([
        ['个人信息', '个人信息', '工作信息', '工作信息'],
        ['姓名', '年龄', '部门', '职位'],
        ['吴九', 27, '技术部', '工程师'],
        ['郑十', 31, '市场部', '主管']
    ])
    df3_raw.to_excel(os.path.join(temp_dir, 'test3.xlsx'), header=None, index=False)
    
    print("✓ 测试文件创建完成")
    return [os.path.join(temp_dir, f'test{i}.xlsx') for i in range(1, 4)]


def test_header_preview():
    """
    测试表头预览功能
    """
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文件
        test_files = create_test_excel_files(temp_dir)
        
        # 创建输出目录
        output_dir = os.path.join(temp_dir, 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        print("\n开始测试表头预览功能...")
        
        # 测试场景1: 自动合并模式
        print("\n=== 测试场景1: 自动合并模式 ===")
        test_preview_vs_merge(test_files, output_dir, 
                              merge_header=False, header_rows=1, header_mode="auto")
        
        # 测试场景2: 使用第一个表头模式
        print("\n=== 测试场景2: 使用第一个表头模式 ===")
        test_preview_vs_merge(test_files, output_dir, 
                              merge_header=False, header_rows=1, header_mode="first")
        
        # 测试场景3: 合并所有表头模式
        print("\n=== 测试场景3: 合并所有表头模式 ===")
        test_preview_vs_merge(test_files, output_dir, 
                              merge_header=False, header_rows=1, header_mode="union")
        
        # 测试场景4: 仅保留共同表头模式
        print("\n=== 测试场景4: 仅保留共同表头模式 ===")
        test_preview_vs_merge(test_files, output_dir, 
                              merge_header=False, header_rows=1, header_mode="intersection")
        
        print("\n✓ 所有测试完成")


def test_preview_vs_merge(test_files, output_dir, merge_header, header_rows, header_mode):
    """
    比较预览结果和实际合并结果
    """
    # 创建合并器实例
    merger = ExcelMerger(
        source_dir=os.path.dirname(test_files[0]),
        output_dir=output_dir,
        selected_files=test_files
    )
    
    # 1. 模拟预览过程
    print(f"\n正在模拟预览 (merge_header={merge_header}, header_rows={header_rows}, header_mode={header_mode})...")
    
    all_sheets_data = []
    for file_path in test_files:
        sheets_data = merger.read_excel_file(
            file_path, 
            header=0, 
            merge_header_rows=merge_header, 
            header_rows=header_rows
        )
        all_sheets_data.extend(sheets_data)
    
    # 模拟表头合并逻辑
    all_dataframes = []
    for i, file_path in enumerate(test_files):
        sheets_data = merger.read_excel_file(
            file_path, 
            header=0, 
            merge_header_rows=merge_header, 
            header_rows=header_rows
        )
        for sheet_data in sheets_data:
            df = sheet_data["dataframe"]
            df = df.copy()  # 创建副本
            df['来源文件'] = os.path.basename(file_path)
            df['来源Sheet'] = sheet_data["sheet_name"]
            all_dataframes.append(df)
    
    # 预览的表头
    if header_mode == "first":
        preview_columns = list(all_dataframes[0].columns)
    elif header_mode == "intersection":
        common_columns = set(all_dataframes[0].columns)
        for df in all_dataframes[1:]:
            common_columns.intersection_update(df.columns)
        preview_columns = sorted(list(common_columns))
    elif header_mode == "union":
        all_columns = set()
        for df in all_dataframes:
            all_columns.update(df.columns)
        preview_columns = sorted(list(all_columns))
    else:  # "auto"
        all_columns = set()
        for df in all_dataframes:
            all_columns.update(df.columns)
        preview_columns = sorted(list(all_columns))
    
    print(f"预览的表头: {preview_columns}")
    
    # 2. 实际合并
    print(f"正在执行实际合并...")
    result = merger.merge_excel_files(
        output_filename=f"merged_{header_mode}.xlsx",
        merge_header_rows=merge_header,
        header_rows=header_rows,
        header_mode=header_mode
    )
    
    if result["success"]:
        # 读取合并后的文件
        merged_df = pd.read_excel(result["output_path"])
        actual_columns = list(merged_df.columns)
        print(f"实际合并的表头: {actual_columns}")
        
        # 比较预览和实际结果
        if sorted(preview_columns) == sorted(actual_columns):
            print("✓ 预览和实际合并结果一致！")
            return True
        else:
            print("✗ 预览和实际合并结果不一致！")
            print(f"  差异: 预览有但实际没有的列: {set(preview_columns) - set(actual_columns)}")
            print(f"  差异: 实际有但预览没有的列: {set(actual_columns) - set(preview_columns)}")
            return False
    else:
        print(f"✗ 合并失败: {result['message']}")
        return False


if __name__ == "__main__":
    test_header_preview()
