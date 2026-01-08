#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试表头处理中发现的问题
"""

import os
import sys
import tempfile
import pandas as pd

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.excel_merge_plugin import ExcelMerger

def create_test_file(file_path, sheets_data):
    """创建测试Excel文件"""
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        for sheet_name, data in sheets_data.items():
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"✓ 创建测试文件: {file_path}")

def create_multi_header_file(file_path, headers, data):
    """创建多行表头测试文件"""
    from openpyxl import Workbook
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    
    # 写入多行表头
    for header_row in headers:
        ws.append(header_row)
    
    # 写入数据
    for data_row in data:
        ws.append(data_row)
    
    wb.save(file_path)
    print(f"✓ 创建多行表头测试文件: {file_path}")

def test_string_data_type_preservation():
    """测试字符串数据类型在表头处理中的保留"""
    print("\n" + "="*60)
    print("测试: 字符串数据类型保留")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建包含长数字的测试文件
        file1 = os.path.join(tmpdir, "long_numbers.xlsx")
        headers = [
            ["个人信息", "联系方式"],
            ["姓名", "电话"]
        ]
        data = [
            ["张三", "13800138000"],
            ["李四", "13900139000"]
        ]
        create_multi_header_file(file1, headers, data)
        
        merger = ExcelMerger(tmpdir, tmpdir)
        
        print("测试多行表头合并中的字符串保留...")
        result = merger.merge_excel_files(merge_header_rows=True, header_rows=2, header_mode="auto")
        if result["success"]:
            df = pd.read_excel(result["output_path"])
            print(f"合并后列: {list(df.columns)}")
            print(f"数据类型:")
            for col in df.columns:
                print(f"  {col}: {df[col].dtype}")
            print(f"数据:")
            print(df)
            
            # 检查电话列是否为字符串类型
            phone_col = [col for col in df.columns if '电话' in col][0]
            if df[phone_col].dtype == 'object':
                print("✓ 电话列保持为字符串类型")
            else:
                print("✗ 电话列不是字符串类型")

def test_header_deduplication():
    """测试表头去重功能"""
    print("\n" + "="*60)
    print("测试: 表头去重")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建包含相同表头的多个文件
        file1 = os.path.join(tmpdir, "file1.xlsx")
        create_test_file(file1, {
            "Sheet1": {
                "姓名": ["张三", "李四"],
                "年龄": [25, 30]
            }
        })
        
        file2 = os.path.join(tmpdir, "file2.xlsx")
        create_test_file(file2, {
            "Sheet1": {
                "姓名": ["王五", "赵六"],
                "年龄": [28, 35]
            }
        })
        
        merger = ExcelMerger(tmpdir, tmpdir)
        
        print("测试相同表头合并...")
        result = merger.merge_excel_files(merge_header_rows=False, header_rows=1, header_mode="auto")
        if result["success"]:
            df = pd.read_excel(result["output_path"])
            print(f"合并后列: {list(df.columns)}")
            print(f"行数: {len(df)}")
            
            # 检查是否有重复的表头
            if len(df.columns) == len(set(df.columns)):
                print("✓ 表头没有重复")
            else:
                print("✗ 表头存在重复")

def test_header_merged_content():
    """测试合并后的表头内容"""
    print("\n" + "="*60)
    print("测试: 合并后的表头内容")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建多行表头测试文件
        file1 = os.path.join(tmpdir, "merged_headers.xlsx")
        headers = [
            ["销售数据", "销售数据", "销售数据"],
            ["产品", "数量", "金额"],
            ["名称", "件数", "元"]
        ]
        data = [
            ["产品A", 100, 5000],
            ["产品B", 200, 8000]
        ]
        create_multi_header_file(file1, headers, data)
        
        merger = ExcelMerger(tmpdir, tmpdir)
        
        print("测试3行表头合并...")
        result = merger.merge_excel_files(merge_header_rows=True, header_rows=3, header_mode="auto")
        if result["success"]:
            df = pd.read_excel(result["output_path"])
            print(f"合并后列: {list(df.columns)}")
            print(f"数据:")
            print(df)

def main():
    """主函数"""
    print("Excel合并插件表头处理问题测试")
    print("="*60)
    
    try:
        test_string_data_type_preservation()
        test_header_deduplication()
        test_header_merged_content()
        
        print("\n" + "="*60)
        print("所有测试完成！")
        print("="*60)
        return 0
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
