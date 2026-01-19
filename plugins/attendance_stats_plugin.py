import os
from datetime import datetime
from typing import List

import pandas as pd
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog,
    QGroupBox, QMessageBox, QLineEdit, QComboBox, QScrollArea,
    QTextEdit, QWidget, QFrame
)

from src.plugins.base_plugin import BasePlugin
from src.utils.logger import logger


class AttendanceStats:
    """
    考勤数据统计类
    用于统计个人和整体的考勤数据
    """
    
    # 考勤状态映射
    STATUS_MAPPING = {
        '出勤': 'present',
        '迟到': 'late',
        '缺勤': 'absent',
        '请假': 'leave',
        '旷工': 'absent',
        '病假': 'leave',
        '事假': 'leave',
        '公假': 'leave'
    }
    
    def __init__(self, file_path: str, sheet_name: str = None):
        """
        初始化考勤统计器
        
        Args:
            file_path: Excel文件路径
            sheet_name: sheet名称，如果为None则使用第一个sheet
        """
        self.file_path = file_path
        self.sheet_name = sheet_name
        
        # 读取数据
        self.df = self._read_excel(file_path, sheet_name)
        
        # 统计结果
        self.stats_result = {
            'personal_stats': {},      # 个人考勤统计
            'overall_stats': {},       # 整体考勤统计
            'full_attendance': [],     # 全勤人员
            'rankings': [],            # 排名
            'raw_data': self.df.copy() # 原始数据备份
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
            # 首先验证文件是否存在
            if not os.path.exists(file_path):
                raise Exception(f"文件不存在: {file_path}")
            
            # 获取文件扩展名
            ext = os.path.splitext(file_path)[1].lower()
            
            # 验证文件扩展名
            if ext not in ['.xlsx', '.xls']:
                raise Exception(f"不支持的文件格式: {ext}")
            
            # 尝试读取文件，支持多种引擎
            engines = ['openpyxl', 'xlrd'] if ext == '.xlsx' else ['xlrd']
            
            for engine in engines:
                try:
                    if sheet_name:
                        df = pd.read_excel(file_path, sheet_name=sheet_name, engine=engine)
                    else:
                        # 当sheet_name为None时，read_excel会返回字典，需要获取第一个sheet
                        df_dict = pd.read_excel(file_path, sheet_name=None, engine=engine)
                        if not df_dict:
                            raise Exception("Excel文件中没有找到任何sheet")
                        # 获取第一个sheet的数据
                        df = list(df_dict.values())[0]
                    
                    return df
                except Exception as engine_e:
                    if engine == engines[-1]:  # 如果是最后一个引擎，抛出异常
                        raise Exception(f"读取Excel文件失败（尝试引擎: {engine}）: {str(engine_e)}")
                    continue  # 尝试下一个引擎
            
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
            # 首先验证文件是否存在
            if not os.path.exists(file_path):
                raise Exception(f"文件不存在: {file_path}")
            
            # 获取文件扩展名
            ext = os.path.splitext(file_path)[1].lower()
            
            # 验证文件扩展名
            if ext not in ['.xlsx', '.xls']:
                raise Exception(f"不支持的文件格式: {ext}")
            
            # 尝试获取sheet名称，支持多种引擎
            engines = ['openpyxl', 'xlrd'] if ext == '.xlsx' else ['xlrd']
            
            for engine in engines:
                try:
                    excel_file = pd.ExcelFile(file_path, engine=engine)
                    return excel_file.sheet_names
                except Exception as engine_e:
                    if engine == engines[-1]:  # 如果是最后一个引擎，抛出异常
                        raise Exception(f"获取sheet名称失败（尝试引擎: {engine}）: {str(engine_e)}")
                    continue  # 尝试下一个引擎
            
        except Exception as e:
            raise Exception(f"获取sheet名称失败: {str(e)}")
    
    def analyze_attendance(self):
        """
        分析考勤数据
        """
        # 转换考勤状态
        df_processed = self._process_status(self.df)
        
        # 统计个人考勤数据
        self._calculate_personal_stats(df_processed)
        
        # 统计整体考勤数据
        self._calculate_overall_stats()
        
        # 找出全勤人员
        self._find_full_attendance()
        
        # 生成排名
        self._generate_rankings()
        
        return self.stats_result
    
    def _process_status(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        处理考勤状态，统一格式
        
        Args:
            df: 原始数据
            
        Returns:
            pd.DataFrame: 处理后的数据
        """
        df_processed = df.copy()
        
        # 获取日期列
        date_columns = df_processed.columns[1:]  # 第一列是姓名
        
        # 转换状态
        for col in date_columns:
            df_processed[col] = df_processed[col].str.strip().str.replace('\\s+', '', regex=True)
            df_processed[col] = df_processed[col].apply(
                lambda x: self.STATUS_MAPPING.get(x, x) if pd.notna(x) else 'absent'
            )
        
        return df_processed
    
    def _calculate_personal_stats(self, df: pd.DataFrame):
        """
        计算个人考勤统计数据
        """
        # 获取日期列
        date_columns = df.columns[1:]  # 第一列是姓名
        total_days = len(date_columns)
        
        # 遍历每一行（每个人）
        for index, row in df.iterrows():
            name = row[df.columns[0]]  # 获取姓名
            personal_data = row[date_columns]  # 获取该人的考勤数据
            
            # 统计各种状态
            present = personal_data.value_counts().get('present', 0)
            late = personal_data.value_counts().get('late', 0)
            absent = personal_data.value_counts().get('absent', 0)
            leave = personal_data.value_counts().get('leave', 0)
            
            # 计算出勤率
            attendance_rate = (present + late) / total_days if total_days > 0 else 0
            
            # 保存统计结果
            self.stats_result['personal_stats'][name] = {
                'total_days': total_days,
                'present': present,
                'late': late,
                'absent': absent,
                'leave': leave,
                'attendance_rate': attendance_rate,
                'late_rate': late / total_days if total_days > 0 else 0,
                'absent_rate': absent / total_days if total_days > 0 else 0,
                'leave_rate': leave / total_days if total_days > 0 else 0
            }
    
    def _calculate_overall_stats(self):
        """
        计算整体考勤统计数据
        """
        personal_stats = self.stats_result['personal_stats']
        total_people = len(personal_stats)
        
        if total_people == 0:
            return
        
        # 计算平均值
        avg_attendance = sum([stats['attendance_rate'] for stats in personal_stats.values()]) / total_people
        avg_late = sum([stats['late_rate'] for stats in personal_stats.values()]) / total_people
        avg_absent = sum([stats['absent_rate'] for stats in personal_stats.values()]) / total_people
        avg_leave = sum([stats['leave_rate'] for stats in personal_stats.values()]) / total_people
        
        # 计算总出勤率
        total_days = next(iter(personal_stats.values()))['total_days']
        total_present_late = sum([stats['present'] + stats['late'] for stats in personal_stats.values()])
        overall_attendance_rate = total_present_late / (total_days * total_people) if (total_days * total_people) > 0 else 0
        
        # 保存整体统计结果
        self.stats_result['overall_stats'] = {
            'total_people': total_people,
            'total_days': total_days,
            'avg_attendance_rate': avg_attendance,
            'avg_late_rate': avg_late,
            'avg_absent_rate': avg_absent,
            'avg_leave_rate': avg_leave,
            'overall_attendance_rate': overall_attendance_rate
        }
    
    def _find_full_attendance(self):
        """
        找出全勤人员
        """
        for name, stats in self.stats_result['personal_stats'].items():
            if stats['absent'] == 0 and stats['leave'] == 0:
                self.stats_result['full_attendance'].append(name)
    
    def _generate_rankings(self):
        """
        生成考勤排名（按出勤率）
        """
        # 按出勤率降序排序
        sorted_stats = sorted(
            self.stats_result['personal_stats'].items(),
            key=lambda x: x[1]['attendance_rate'],
            reverse=True
        )
        
        # 生成排名
        rankings = []
        for i, (name, stats) in enumerate(sorted_stats, 1):
            rankings.append({
                'rank': i,
                'name': name,
                'attendance_rate': stats['attendance_rate'],
                'present': stats['present'],
                'late': stats['late']
            })
        
        self.stats_result['rankings'] = rankings
    
    def export_results(self, output_dir: str) -> str:
        """
        导出统计结果
        
        Args:
            output_dir: 输出目录
            
        Returns:
            str: 导出文件路径
        """
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 生成导出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"attendance_stats_{timestamp}.xlsx"
        output_path = os.path.join(output_dir, output_filename)
        
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # 写入原始数据
                self.stats_result['raw_data'].to_excel(writer, sheet_name='原始数据', index=False)
                
                # 写入个人统计
                personal_df = pd.DataFrame.from_dict(
                    self.stats_result['personal_stats'], orient='index'
                ).reset_index().rename(columns={'index': '姓名'})
                # 替换个人统计的英文列名为中文
                personal_columns_map = {
                    'total_days': '总天数',
                    'present': '出勤天数',
                    'late': '迟到次数',
                    'absent': '缺勤次数',
                    'leave': '请假次数',
                    'attendance_rate': '出勤率',
                    'late_rate': '迟到率',
                    'absent_rate': '缺勤率',
                    'leave_rate': '请假率'
                }
                personal_df = personal_df.rename(columns=personal_columns_map)
                personal_df.to_excel(writer, sheet_name='个人考勤统计', index=False)
                
                # 写入整体统计
                overall_df = pd.DataFrame([self.stats_result['overall_stats']])
                # 替换整体统计的英文列名为中文
                overall_columns_map = {
                    'total_people': '总人数',
                    'total_days': '总天数',
                    'avg_attendance_rate': '平均出勤率',
                    'avg_late_rate': '平均迟到率',
                    'avg_absent_rate': '平均缺勤率',
                    'avg_leave_rate': '平均请假率',
                    'overall_attendance_rate': '整体出勤率'
                }
                overall_df = overall_df.rename(columns=overall_columns_map)
                overall_df.to_excel(writer, sheet_name='整体考勤统计', index=False)
                
                # 写入全勤人员
                if self.stats_result['full_attendance']:
                    full_attendance_df = pd.DataFrame({
                        '全勤人员': self.stats_result['full_attendance']
                    })
                    full_attendance_df.to_excel(writer, sheet_name='全勤人员', index=False)
                
                # 写入排名
                rankings_df = pd.DataFrame(self.stats_result['rankings'])
                # 替换排名的英文列名为中文
                rankings_columns_map = {
                    'name': '姓名',
                    'attendance_rate': '出勤率',
                    'present': '出勤天数',
                    'late': '迟到次数'
                }
                rankings_df = rankings_df.rename(columns=rankings_columns_map)
                rankings_df.to_excel(writer, sheet_name='考勤排名', index=False)
            
            return output_path
        except Exception as e:
            raise Exception(f"导出失败: {str(e)}")


class AttendanceStatsPlugin(BasePlugin):
    """
    考勤统计插件
    用于统计个人和整体的考勤数据
    """
    
    def __init__(self):
        super().__init__("考勤统计", "统计个人和整体的考勤数据，支持导出结果")
        
        self.file_path = ""
        self.sheet_name = None
        self.stats = None
        self.stats_result = None
        
        self._setup_ui()
    
    def on_activate(self):
        """
        插件被激活时调用
        """
        logger.info("考勤统计插件被激活")
    
    def get_widget(self) -> QWidget:
        return self
    
    def _setup_ui(self):
        """
        设置UI界面
        """
        # 创建主滚动区域
        main_scroll = QScrollArea(self)
        main_scroll.setWidgetResizable(True)
        main_scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # 创建滚动区域内的主widget
        scroll_widget = QWidget()
        scroll_widget.setObjectName("pluginContainer")
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(main_scroll)
        main_scroll.setWidget(scroll_widget)
        
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
        file_instruction = QLabel("请选择要处理的Excel文件，支持.xlsx和.xls格式")
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
        
        # 2. 统计选项
        stats_group = QGroupBox("2. 统计选项")
        stats_group.setStyleSheet("""
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
        
        stats_layout = QVBoxLayout()
        
        # 统计选项说明
        stats_instruction = QLabel("选择要进行的统计分析")
        stats_instruction.setStyleSheet("font-size: 13px; color: #7f8c8d; margin-bottom: 10px;")
        stats_layout.addWidget(stats_instruction)
        
        # 统计操作按钮
        stats_btn_layout = QHBoxLayout()
        stats_btn_layout.addStretch()
        
        self.analyze_btn = QPushButton("执行统计分析")
        self.analyze_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.analyze_btn.clicked.connect(self.analyze_attendance)
        self.analyze_btn.setEnabled(False)
        
        stats_btn_layout.addWidget(self.analyze_btn)
        stats_layout.addLayout(stats_btn_layout)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # 3. 结果显示
        result_group = QGroupBox("3. 统计结果")
        result_group.setStyleSheet("""
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
        
        result_layout = QVBoxLayout()
        
        # 结果显示区域
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("font-size: 14px; padding: 10px;")
        self.result_text.setText("请先选择Excel文件并执行统计分析")
        
        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
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
        
        # 导出按钮
        export_btn_layout = QHBoxLayout()
        export_btn_layout.addStretch()
        
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
        
        export_btn_layout.addWidget(self.export_btn)
        export_layout.addLayout(export_btn_layout)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
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
            <h3>考勤统计插件功能介绍</h3>
            <p><strong>使用流程：</strong></p>
            <ol>
                <li><strong>上传文件、选择工作表</strong>：选择要处理的Excel文件，并从下拉列表中选择要操作的工作表<br>
                （注：Excel文件格式要求：第一列是姓名，其余列是日期，单元格内容为考勤状态）</li>
                <li><strong>执行统计分析</strong>：点击按钮开始分析考勤数据</li>
                <li><strong>查看统计结果</strong>：在结果区域查看个人和整体的考勤统计数据</li>
                <li><strong>导出结果</strong>：将统计结果导出为Excel文件</li>
            </ol>
            <p><strong>支持的考勤状态：</strong></p>
            <ul>
                <li>出勤、正常：视为出勤</li>
                <li>迟到：视为迟到</li>
                <li>缺勤、旷工：视为缺勤</li>
                <li>请假、病假、事假、公假：视为请假</li>
            </ul>
            <p><strong>统计内容：</strong></p>
            <ul>
                <li><strong>个人考勤统计</strong>：出勤天数、迟到次数、缺勤次数、请假次数、出勤率、迟到率、缺勤率、请假率</li>
                <li><strong>整体考勤统计</strong>：总人数、总天数、平均出勤率、平均迟到率、平均缺勤率、平均请假率、整体出勤率</li>
                <li><strong>全勤统计</strong>：列出所有全勤人员（无缺勤、无请假）</li>
                <li><strong>考勤排名</strong>：按出勤率进行排名</li>
            </ul>
        """)
        
        self.description_scroll = QScrollArea()
        self.description_scroll.setWidget(self.description_text)
        self.description_scroll.setWidgetResizable(True)
        self.description_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.description_scroll.setMaximumHeight(300)
        self.description_scroll.setFixedHeight(50)  # 默认收起高度
        
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
                self.stats = AttendanceStats(file_path, None)  # 临时创建
                sheet_names = self.stats.get_sheet_names(file_path)
                self.sheet_combo.clear()
                self.sheet_combo.addItems(sheet_names)
                self.sheet_name = sheet_names[0]
                
                # 启用统计按钮
                self.analyze_btn.setEnabled(True)
                self.export_btn.setEnabled(True)
                
            except Exception as e:
                QMessageBox.warning(self, "加载失败", f"加载文件信息失败: {str(e)}")
    
    def analyze_attendance(self):
        """
        分析考勤数据
        """
        if not self.file_path:
            QMessageBox.warning(self, "警告", "请先选择Excel文件")
            return
        
        try:
            # 创建统计器
            self.stats = AttendanceStats(self.file_path, self.sheet_name)
            
            # 分析考勤数据
            self.stats_result = self.stats.analyze_attendance()
            
            # 更新结果显示
            self._update_result_display()
            
            QMessageBox.information(self, "完成", "考勤统计分析完成")
            
        except Exception as e:
            QMessageBox.critical(self, "失败", f"考勤统计分析时发生错误: {str(e)}")
            logger.info(f"考勤统计分析错误: {str(e)}")
    
    def _update_result_display(self):
        """
        更新结果显示
        """
        if not self.stats_result:
            return
        
        try:
            # 构建结果文本
            result_text = """
考勤统计结果
==============

"""
            
            # 添加整体统计
            if 'overall_stats' in self.stats_result:
                overall = self.stats_result['overall_stats']
                result_text += "整体考勤统计\n"
                result_text += "-" * 20 + "\n"
                result_text += f"总人数: {overall['total_people']}\n"
                result_text += f"总天数: {overall['total_days']}\n"
                
                # 确保所有值都是数字并使用安全格式化
                try:
                    avg_attendance = float(overall['avg_attendance_rate']) if pd.notna(overall['avg_attendance_rate']) else 0
                    result_text += "平均出勤率: {:.2f}%\n".format(avg_attendance * 100)
                except Exception as e:
                    result_text += f"平均出勤率: 0.00%\n"
                
                try:
                    avg_late = float(overall['avg_late_rate']) if pd.notna(overall['avg_late_rate']) else 0
                    result_text += "平均迟到率: {:.2f}%\n".format(avg_late * 100)
                except Exception as e:
                    result_text += f"平均迟到率: 0.00%\n"
                
                try:
                    avg_absent = float(overall['avg_absent_rate']) if pd.notna(overall['avg_absent_rate']) else 0
                    result_text += "平均缺勤率: {:.2f}%\n".format(avg_absent * 100)
                except Exception as e:
                    result_text += f"平均缺勤率: 0.00%\n"
                
                try:
                    avg_leave = float(overall['avg_leave_rate']) if pd.notna(overall['avg_leave_rate']) else 0
                    result_text += "平均请假率: {:.2f}%\n".format(avg_leave * 100)
                except Exception as e:
                    result_text += f"平均请假率: 0.00%\n"
                
                try:
                    overall_attendance = float(overall['overall_attendance_rate']) if pd.notna(overall['overall_attendance_rate']) else 0
                    result_text += "整体出勤率: {:.2f}%\n".format(overall_attendance * 100)
                except Exception as e:
                    result_text += f"整体出勤率: 0.00%\n"
                
                result_text += "\n"
            
            # 添加全勤统计
            full_attendance = self.stats_result.get('full_attendance', [])
            result_text += "全勤人员\n"
            result_text += "-" * 20 + "\n"
            if full_attendance:
                for name in full_attendance:
                    result_text += f"- {name}\n"
            else:
                result_text += "无全勤人员\n"
            
            result_text += "\n"
            
            # 添加考勤排名（前10名）
            rankings = self.stats_result.get('rankings', [])[:10]  # 只显示前10名
            result_text += "考勤排名（按出勤率，前10名）\n"
            result_text += "-" * 30 + "\n"
            result_text += "{:<6}{:<10}{:<10}{:<6}{:<6}\n".format('排名', '姓名', '出勤率', '出勤', '迟到')
            result_text += "-" * 30 + "\n"
            for rank in rankings:
                try:
                    attendance_rate = float(rank['attendance_rate']) if pd.notna(rank['attendance_rate']) else 0
                    result_text += "{:<6}{:<10}{:<10.2f}%{:<6}{:<6}\n".format(
                        rank['rank'], 
                        rank['name'], 
                        attendance_rate * 100,
                        rank['present'], 
                        rank['late']
                    )
                except Exception as e:
                    result_text += "{:<6}{:<10}{:<10}{:<6}{:<6}\n".format(
                        rank['rank'], 
                        rank['name'], 
                        '0.00%',
                        rank['present'], 
                        rank['late']
                    )
            
            if len(self.stats_result.get('rankings', [])) > 10:
                result_text += f"... 共{len(self.stats_result['rankings'])}人\n"
            
            result_text += "\n"
            
            # 添加个人统计（前5名）
            personal = self.stats_result.get('personal_stats', {})
            top_5_names = [rank['name'] for rank in rankings[:5]]
            result_text += "个人考勤统计（前5名详情）\n"
            result_text += "-" * 50 + "\n"
            for name in top_5_names:
                if name in personal:
                    stats = personal[name]
                    result_text += f"姓名: {name}\n"
                    result_text += f"  出勤天数: {stats['present']}\n"
                    result_text += f"  迟到次数: {stats['late']}\n"
                    result_text += f"  缺勤次数: {stats['absent']}\n"
                    result_text += f"  请假次数: {stats['leave']}\n"
                    
                    # 确保所有值都是数字并使用安全格式化
                    try:
                        attendance_rate = float(stats['attendance_rate']) if pd.notna(stats['attendance_rate']) else 0
                        result_text += "  出勤率: {:.2f}%\n".format(attendance_rate * 100)
                    except Exception as e:
                        result_text += f"  出勤率: 0.00%\n"
                    
                    try:
                        late_rate = float(stats['late_rate']) if pd.notna(stats['late_rate']) else 0
                        result_text += "  迟到率: {:.2f}%\n".format(late_rate * 100)
                    except Exception as e:
                        result_text += f"  迟到率: 0.00%\n"
                    
                    try:
                        absent_rate = float(stats['absent_rate']) if pd.notna(stats['absent_rate']) else 0
                        result_text += "  缺勤率: {:.2f}%\n".format(absent_rate * 100)
                    except Exception as e:
                        result_text += f"  缺勤率: 0.00%\n"
                    
                    try:
                        leave_rate = float(stats['leave_rate']) if pd.notna(stats['leave_rate']) else 0
                        result_text += "  请假率: {:.2f}%\n".format(leave_rate * 100)
                    except Exception as e:
                        result_text += f"  请假率: 0.00%\n"
                    
                    result_text += "\n"
            
            # 更新结果显示
            self.result_text.setText(result_text)
            
        except Exception as e:
            # 如果发生任何错误，显示友好的错误信息
            self.result_text.setText(f"显示结果时发生错误: {str(e)}")
            logger.info(f"更新结果显示错误: {str(e)}")
    
    def export_results(self):
        """
        导出结果
        """
        if not self.stats_result:
            QMessageBox.warning(self, "警告", "请先执行考勤统计分析")
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
            # 生成报告
            report_path = self.stats.export_results(output_dir)
            
            QMessageBox.information(
                self,
                "结果导出成功",
                f"考勤统计结果已导出：\n{report_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出结果时发生错误: {str(e)}")
            logger.info(f"导出错误: {str(e)}")


if __name__ == "__main__":
    # 测试代码
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    plugin = AttendanceStatsPlugin()
    plugin.show()
    sys.exit(app.exec())
