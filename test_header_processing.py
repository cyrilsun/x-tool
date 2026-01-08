#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Excel合并插件的表头处理功能
"""

import os
import sys
import tempfile
import pandas as pd
from openpyxl import Workbook

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

def test_single_row_headers():
    """测试单行表头处理"""
    print("\n" + "="*60)
    print("测试1: 单行表头处理")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试文件1
        file1 = os.path.join(tmpdir, "test1.xlsx")
        create_test_file(file1, {
            "Sheet1": {
                "姓名": ["张三", "李四"],
                "年龄": [25, 30],
                "城市": ["北京", "上海"]
            }
        })
        
        # 创建测试文件2
        file2 = os.path.join(tmpdir, "test2.xlsx")
        create_test_file(file2, {
            "Sheet1": {
                "姓名": ["王五", "赵六"],
                "年龄": [28, 35],
                "城市": ["广州", "深圳"]
            }
        })
        
        # 测试不同表头模式
        merger = ExcelMerger(tmpdir, tmpdir)
        
        print("\n测试auto模式...")
        result = merger.merge_excel_files(merge_header_rows=False, header_rows=1, header_mode="auto")
        if result["success"]:
            df = pd.read_excel(result["output_path"])
            print(f"  合并后列: {list(df.columns)}")
            print(f"  行数: {len(df)}")
        
        print("\n测试first模式...")
        result = merger.merge_excel_files(merge_header_rows=False, header_rows=1, header_mode="first")
        if result["success"]:
            df = pd.read_excel(result["output_path"])
            print(f"  合并后列: {list(df.columns)}")
            print(f"  行数: {len(df)}")

def test_different_headers():
    """测试不同表头处理"""
    print("\n" + "="*60)
    print("测试2: 不同表头处理")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试文件1
        file1 = os.path.join(tmpdir, "test1.xlsx")
        create_test_file(file1, {
            "Sheet1": {
                "姓名": ["张三", "李四"],
                "年龄": [25, 30],
                "城市": ["北京", "上海"]
            }
        })
        
        # 创建测试文件2（不同表头）
        file2 = os.path.join(tmpdir, "test2.xlsx")
        create_test_file(file2, {
            "Sheet1": {
                "姓名": ["王五", "赵六"],
                "性别": ["男", "女"],
                "电话": ["13800138000", "13900139000"]
            }
        })
        
        merger = ExcelMerger(tmpdir, tmpdir)
        
        print("\n测试auto模式（基于列名匹配）...")
        result = merger.merge_excel_files(merge_header_rows=False, header_rows=1, header_mode="auto")
        if result["success"]:
            df = pd.read_excel(result["output_path"])
            print(f"  合并后列: {list(df.columns)}")
            print(f"  行数: {len(df)}")
        
        print("\n测试union模式（包含所有列）...")
        result = merger.merge_excel_files(merge_header_rows=False, header_rows=1, header_mode="union")
        if result["success"]:
            df = pd.read_excel(result["output_path"])
            print(f"  合并后列: {list(df.columns)}")
            print(f"  行数: {len(df)}")
        
        print("\n测试intersection模式（仅包含共同列）...")
        result = merger.merge_excel_files(merge_header_rows=False, header_rows=1, header_mode="intersection")
        if result["success"]:
            df = pd.read_excel(result["output_path"])
            print(f"  合并后列: {list(df.columns)}")
            print(f"  行数: {len(df)}")

def test_multi_row_headers():
    """测试多行表头处理"""
    print("\n" + "="*60)
    print("测试3: 多行表头处理")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建多行表头测试文件1
        file1 = os.path.join(tmpdir, "multi_header1.xlsx")
        headers1 = [
            ["个人信息", "个人信息", "联系方式"],
            ["姓名", "年龄", "电话"]
        ]
        data1 = [
            ["张三", 25, "13800138000"],
            ["李四", 30, "13900139000"]
        ]
        create_multi_header_file(file1, headers1, data1)
        
        # 创建多行表头测试文件2
        file2 = os.path.join(tmpdir, "multi_header2.xlsx")
        headers2 = [
            ["个人信息", "个人信息", "联系方式"],
            ["姓名", "年龄", "邮箱"]
        ]
        data2 = [
            ["王五", 28, "wangwu@example.com"],
            ["赵六", 35, "zhaoliu@example.com"]
        ]
        create_multi_header_file(file2, headers2, data2)
        
        # 测试多行表头合并
        merger = ExcelMerger(tmpdir, tmpdir)
        
        print("\n测试多行表头合并...")
        result = merger.merge_excel_files(merge_header_rows=True, header_rows=2, header_mode="auto")
        if result["success"]:
            df = pd.read_excel(result["output_path"])
            print(f"  合并后列: {list(df.columns)}")
            print(f"  行数: {len(df)}")
            print(f"  数据:")
            print(df)
        
        print("\n测试多行表头+union模式...")
        result = merger.merge_excel_files(merge_header_rows=True, header_rows=2, header_mode="union")
        if result["success"]:
            df = pd.read_excel(result["output_path"])
            print(f"  合并后列: {list(df.columns)}")
            print(f"  行数: {len(df)}")

def test_single_file_multiple_sheets():
    """测试同一文件多个sheet的表头处理"""
    print("\n" + "="*60)
    print("测试4: 同一文件多个sheet的表头处理")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建多sheet测试文件
        file1 = os.path.join(tmpdir, "multi_sheet.xlsx")
        create_test_file(file1, {
            "Sheet1": {
                "姓名": ["张三", "李四"],
                "年龄": [25, 30],
                "城市": ["北京", "上海"]
            },
            "Sheet2": {
                "姓名": ["王五", "赵六"],
                "年龄": [28, 35],
                "性别": ["男", "女"]
            }
        })
        
        # 设置合并器（选择单个文件）
        merger = ExcelMerger(os.path.dirname(file1), tmpdir, [file1])
        
        print("\n测试单个文件多sheet合并（auto模式）...")
        result = merger.merge_single_file_sheets(merge_header_rows=False, header_rows=1, header_mode="auto")
        if result["success"]:
            output_file = result["output_files"][0]
            df = pd.read_excel(output_file)
            print(f"  合并后列: {list(df.columns)}")
            print(f"  行数: {len(df)}")
        
        print("\n测试单个文件多sheet合并（intersection模式）...")
        result = merger.merge_single_file_sheets(merge_header_rows=False, header_rows=1, header_mode="intersection")
        if result["success"]:
            output_file = result["output_files"][0]
            df = pd.read_excel(output_file)
            print(f"  合并后列: {list(df.columns)}")
            print(f"  行数: {len(df)}")

def test_empty_cells_in_headers():
    """测试表头中的空单元格处理"""
    print("\n" + "="*60)
    print("测试5: 表头中空单元格处理")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建带空单元格表头的文件
        file1 = os.path.join(tmpdir, "empty_headers.xlsx")
        headers = [
            ["个人信息", "", "联系方式"],
            ["姓名", "年龄", ""]
        ]
        data = [
            ["张三", 25, "13800138000"],
            ["李四", 30, "13900139000"]
        ]
        create_multi_header_file(file1, headers, data)
        
        merger = ExcelMerger(tmpdir, tmpdir)
        
        print("\n测试带空单元格的多行表头合并...")
        result = merger.merge_excel_files(merge_header_rows=True, header_rows=2, header_mode="auto")
        if result["success"]:
            df = pd.read_excel(result["output_path"])
            print(f"  合并后列: {list(df.columns)}")
            print(f"  行数: {len(df)}")

def main():
    """主函数"""
    print("Excel合并插件表头处理功能测试")
    print("="*60)
    
    try:
        test_single_row_headers()
        test_different_headers()
        test_multi_row_headers()
        test_single_file_multiple_sheets()
        test_empty_cells_in_headers()
        
        print("\n" + "="*60)
        print("所有测试完成！")
        print("="*60)
        return 0
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
