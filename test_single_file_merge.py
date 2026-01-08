import os
import pandas as pd
import tempfile
from plugins.excel_merge_plugin import ExcelMerger

def test_single_file_sheets_merge():
    """
    测试单个文件的多个sheet合并功能，特别是first模式的修复
    """
    print("=== 测试单个文件的多个sheet合并功能 ===")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # 创建测试文件
        test_file = os.path.join(temp_dir, "test_multi_sheet.xlsx")
        
        # 创建多个不同表头的sheet
        with pd.ExcelWriter(test_file, engine='openpyxl') as writer:
            # Sheet1 有姓名、年龄、部门列
            df1 = pd.DataFrame({
                '姓名': ['张三', '李四', '王五'],
                '年龄': [25, 30, 35],
                '部门': ['技术部', '市场部', '财务部']
            })
            df1.to_excel(writer, sheet_name='Sheet1', index=False)
            
            # Sheet2 有姓名、职位、薪资列
            df2 = pd.DataFrame({
                '姓名': ['赵六', '孙七', '周八'],
                '职位': ['工程师', '经理', '总监'],
                '薪资': [15000, 20000, 30000]
            })
            df2.to_excel(writer, sheet_name='Sheet2', index=False)
            
            # Sheet3 有姓名、年龄、联系方式列
            df3 = pd.DataFrame({
                '姓名': ['吴九', '郑十', '钱一'],
                '年龄': [28, 32, 40],
                '联系方式': ['13800138001', '13900139001', '13700137001']
            })
            df3.to_excel(writer, sheet_name='Sheet3', index=False)
        
        print(f"✓ 创建测试文件: {test_file}")
        
        # 测试first模式合并
        print("\n=== 测试first模式合并 ===")
        merger = ExcelMerger(temp_dir, output_dir, [test_file])
        result = merger.merge_single_file_sheets(header_mode="first")
        
        if result["success"]:
            print("✓ 合并成功!")
            print(f"输出文件: {result['output_files'][0]}")
            
            # 验证合并结果
            merged_df = pd.read_excel(result['output_files'][0])
            print(f"合并后列名: {list(merged_df.columns)}")
            print(f"合并后行数: {len(merged_df)}")
            
            # 应该只有Sheet1的列（姓名、年龄、部门）加上来源Sheet列
            expected_columns = ['姓名', '年龄', '部门', '来源Sheet']
            if list(merged_df.columns) == expected_columns:
                print("✓ 列名符合预期，first模式修复成功!")
            else:
                print(f"✗ 列名不符合预期，期望: {expected_columns}")
        else:
            print(f"✗ 合并失败: {result['message']}")
        
        # 测试union模式合并
        print("\n=== 测试union模式合并 ===")
        result = merger.merge_single_file_sheets(header_mode="union")
        
        if result["success"]:
            print("✓ 合并成功!")
            print(f"输出文件: {result['output_files'][0]}")
            
            # 验证合并结果
            merged_df = pd.read_excel(result['output_files'][0])
            print(f"合并后列名: {list(merged_df.columns)}")
            print(f"合并后行数: {len(merged_df)}")
        else:
            print(f"✗ 合并失败: {result['message']}")
        
        print("\n=== 单个文件的多个sheet合并测试完成 ===")

if __name__ == "__main__":
    test_single_file_sheets_merge()
