import random
import os
import sys
import json
from datetime import date
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox, 
    QMessageBox, QSpinBox, QComboBox, QWidget, QScrollArea, 
    QTextEdit, QFrame, QApplication, QDateEdit
)
from PyQt6.QtCore import QDate
from src.plugins.base_plugin import BasePlugin
from src.utils.logger import logger

class IdCardGeneratorPlugin(BasePlugin):
    """
    身份证号码生成器插件
    支持根据省市区、出生日期、性别批量生成身份证号码
    """

    # 插件元数据
    PLUGIN_INFO = {
        "name": "身份证生成",
        "description": "批量生成符合规则的身份证号码 (用于测试)",
        "version": "1.0.0",
        "category": "数据生成",
        "author": "X-Tool Team"
    }

    # 简化的行政区划数据 (省: {市: {区: 代码}})
    # 为了演示提供基础数据，实际应用中建议使用完整的 GB/T 2260 数据库
    AREA_DATA = {
        "北京市": {
            "市辖区": {
                "东城区": "110101",
                "西城区": "110102",
                "朝阳区": "110105",
                "丰台区": "110106",
                "石景山区": "110107",
                "海淀区": "110108",
                "门头沟区": "110109",
                "房山区": "110111",
                "通州区": "110112",
                "顺义区": "110113",
                "昌平区": "110114",
                "大兴区": "110115",
                "怀柔区": "110116",
                "平谷区": "110117",
            }
        },
        "上海市": {
            "市辖区": {
                "黄浦区": "310101",
                "徐汇区": "310104",
                "长宁区": "310105",
                "静安区": "310106",
                "普陀区": "310107",
                "虹口区": "310109",
                "杨浦区": "310110",
                "闵行区": "310112",
                "宝山区": "310113",
                "嘉定区": "310114",
                "浦东新区": "310115",
            }
        },
        "广东省": {
            "广州市": {
                "越秀区": "440104",
                "海珠区": "440105",
                "荔湾区": "440103",
                "天河区": "440106",
                "白云区": "440111",
                "黄埔区": "440112",
                "番禺区": "440113",
                "花都区": "440114",
                "南沙区": "440115",
                "从化区": "440117",
                "增城区": "440118",
            },
            "深圳市": {
                "罗湖区": "440303",
                "福田区": "440304",
                "南山区": "440305",
                "宝安区": "440306",
                "龙岗区": "440307",
                "盐田区": "440308",
                "龙华区": "440310",
                "坪山区": "440311",
            }
        }
    }

    def __init__(self):
        super().__init__()

        # 1. 动态加载插件私有库 (不影响基础代码)
        self._init_plugin_libs()

        # 2. 加载完整省市区数据 (外部 JSON 优先，内置兜底)
        self.area_data = self._load_area_data()

        self._setup_ui()

    def _init_plugin_libs(self):
        """
        初始化插件私有库目录
        允许将第三方库放入 plugins/libs 目录并直接 import
        """
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        libs_dir = os.path.join(plugin_dir, "libs")
        if not os.path.exists(libs_dir):
            try:
                os.makedirs(libs_dir)
            except:
                pass
        
        if libs_dir not in sys.path:
            sys.path.insert(0, libs_dir)
            logger.info(f"身份证生成插件：已挂载私有库目录 {libs_dir}")

    def _load_area_data(self) -> dict:
        """
        加载行政区划数据
        逻辑：尝试读取同级目录下的 area_data.json，失败则使用内置 AREA_DATA
        """
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(plugin_dir, "area_data.json")
        
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info("身份证生成插件：成功加载外部完整省市区数据")
                    return data
            except Exception as e:
                logger.error(f"身份证生成插件：加载外部 JSON 失败: {e}")
        
        return self.AREA_DATA

    def get_widget(self) -> QWidget:
        return self

    def on_activate(self):
        logger.info("身份证生成器插件被激活")

    def _setup_ui(self):
        """设置UI界面"""
        layout = self.get_content_layout()

        # 1. 生成设置区域
        settings_group = QGroupBox("生成设置")
        settings_group.setStyleSheet("""
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
        
        settings_layout = QVBoxLayout()
        
        # 行政区划选择
        area_layout = QHBoxLayout()
        self.province_combo = QComboBox()
        self.city_combo = QComboBox()
        self.district_combo = QComboBox()
        
        for combo in [self.province_combo, self.city_combo, self.district_combo]:
            combo.setStyleSheet("padding: 5px; border: 1px solid #bdc3c7; border-radius: 4px; min-width: 120px;")

        self.province_combo.addItems(self.area_data.keys())
        self.province_combo.currentTextChanged.connect(self._update_cities)
        
        self.city_combo.currentTextChanged.connect(self._update_districts)
        
        area_layout.addWidget(QLabel("省/直辖市:"))
        area_layout.addWidget(self.province_combo)
        area_layout.addWidget(QLabel("市:"))
        area_layout.addWidget(self.city_combo)
        area_layout.addWidget(QLabel("区/县:"))
        area_layout.addWidget(self.district_combo)
        area_layout.addStretch()
        
        # 出生日期与性别
        birth_gender_layout = QHBoxLayout()
        self.birth_date = QDateEdit()
        self.birth_date.setDisplayFormat("yyyy-MM-dd")
        self.birth_date.setDate(QDate(2000, 1, 1))
        self.birth_date.setCalendarPopup(True)
        
        # 优化日历控件样式
        calendar = self.birth_date.calendarWidget()
        calendar.setStyleSheet("""
            QCalendarWidget QWidget { 
                alternate-background-color: #f8f9fa;
            }
            #qt_calendar_navigationbar {
                background-color: white;
                border-bottom: 1px solid #dee2e6;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #2c3e50;  
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #bdc3c7;
            }
            QCalendarWidget QToolButton {
                color: #2c3e50;
                background-color: transparent;
                border: none;
                margin: 2px;
                padding: 5px;
                font-weight: bold;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #ecf0f1;
                border-radius: 4px;
            }
            QCalendarWidget QMenu {
                background-color: white;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
            }
            QCalendarWidget QMenu::item:selected {
                background-color: #3498db;
                color: white;
            }
            QCalendarWidget QSpinBox {
                color: #2c3e50;
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
                border: none;
            }
        """)
        
        self.birth_date.setStyleSheet("""
            QDateEdit {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                min-width: 120px;
                color: #2c3e50;
            }
            QDateEdit::drop-down {
                border: none;
            }
        """)
        
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["男", "女"])
        self.gender_combo.setStyleSheet("padding: 5px; border: 1px solid #bdc3c7; border-radius: 4px; min-width: 80px;")
        
        birth_gender_layout.addWidget(QLabel("出生日期:"))
        birth_gender_layout.addWidget(self.birth_date)
        birth_gender_layout.addSpacing(20)
        birth_gender_layout.addWidget(QLabel("性别:"))
        birth_gender_layout.addWidget(self.gender_combo)
        birth_gender_layout.addStretch()

        # 数量设置
        count_layout = QHBoxLayout()
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 100)
        self.count_spin.setValue(5)
        self.count_spin.setStyleSheet("padding: 5px; border: 1px solid #bdc3c7; border-radius: 4px; min-width: 80px;")
        
        count_layout.addWidget(QLabel("生成数量:"))
        count_layout.addWidget(self.count_spin)
        count_layout.addStretch()

        settings_layout.addLayout(area_layout)
        settings_layout.addLayout(birth_gender_layout)
        settings_layout.addLayout(count_layout)
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # 2. 操作按钮
        btn_layout = QHBoxLayout()
        self.generate_btn = QPushButton("生成身份证号")
        self.generate_btn.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white; border: none; padding: 10px 24px; font-size: 14px; font-weight: bold; border-radius: 4px; }
            QPushButton:hover { background-color: #229954; }
        """)
        self.generate_btn.clicked.connect(self.generate_ids)
        
        self.copy_btn = QPushButton("复制全部")
        self.copy_btn.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white; border: none; padding: 10px 24px; font-size: 14px; font-weight: bold; border-radius: 4px; }
            QPushButton:hover { background-color: #2980b9; }
        """)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        
        self.clear_btn = QPushButton("清空")
        self.clear_btn.setStyleSheet("""
            QPushButton { background-color: #95a5a6; color: white; border: none; padding: 10px 24px; font-size: 14px; font-weight: bold; border-radius: 4px; }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        self.clear_btn.clicked.connect(lambda: self.result_text.clear())

        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(self.copy_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 3. 结果显示
        result_group = QGroupBox("生成结果")
        result_group.setStyleSheet("""
            QGroupBox { font-size: 16px; font-weight: bold; color: #2c3e50; border: 2px solid #bdc3c7; border-radius: 8px; margin-top: 10px; padding-top: 15px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }
        """)
        result_layout = QVBoxLayout()
        self.result_text = QTextEdit()
        self.result_text.setPlaceholderText("生成的身份证号码将显示在这里...")
        self.result_text.setStyleSheet("font-family: 'Courier New', monospace; font-size: 14px; padding: 10px; border: 1px solid #bdc3c7; border-radius: 4px;")
        self.result_text.setMinimumHeight(200)
        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        # 4. 插件说明 (使用标准化方法，自动包含元数据)
        description_html = """
            <p><strong>身份证号码生成器</strong> 用于生成符合 GB11643-1999 标准的 18 位身份证号码。</p>
            <ul>
                <li><strong>行政区划</strong>：支持从外部加载完整数据。若需使用完整数据，请在插件目录下放置 <code>area_data.json</code>。</li>
                <li><strong>私有扩展</strong>：支持在插件目录下的 <code>libs</code> 文件夹中放入第三方库，插件会自动识别并允许 import。</li>
                <li><strong>校验位计算</strong>：严格按照 ISO 7064:1983.MOD 11-2 算法。</li>
            </ul>
            <p><span style='color: #e74c3c;'>注：本工具仅用于软件开发和测试目的，生成的号码不具有法律效力。</span></p>
        """
        description_header, _, _, description_scroll = self.create_description_section(description_html)
        layout.addLayout(description_header)
        layout.addWidget(description_scroll)

        # 初始化数据
        self._update_cities()

    def _update_cities(self):
        province = self.province_combo.currentText()
        self.city_combo.clear()
        if province in self.area_data:
            self.city_combo.addItems(self.area_data[province].keys())
        self._update_districts()

    def _update_districts(self):
        province = self.province_combo.currentText()
        city = self.city_combo.currentText()
        self.district_combo.clear()
        if province in self.area_data and city in self.area_data[province]:
            self.district_combo.addItems(self.area_data[province][city].keys())

    def calculate_check_digit(self, id17):
        """计算第18位校验码"""
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_map = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        sum_val = sum(int(id17[i]) * weights[i] for i in range(17))
        return check_map[sum_val % 11]

    def generate_ids(self):
        province = self.province_combo.currentText()
        city = self.city_combo.currentText()
        district = self.district_combo.currentText()
        
        try:
            area_code = self.area_data[province][city][district]
            birth_str = self.birth_date.date().toString("yyyyMMdd")
            is_male = self.gender_combo.currentText() == "男"
            count = self.count_spin.value()
            
            results = []
            for _ in range(count):
                # 生成顺序码 (15-17位)
                # 第17位：奇数男，偶数女
                seq = random.randint(0, 499) * 2 + (1 if is_male else 0)
                seq_str = f"{seq:03d}"
                
                id17 = area_code + birth_str + seq_str
                check_digit = self.calculate_check_digit(id17)
                results.append(id17 + check_digit)
            
            self.result_text.setPlainText("\n".join(results))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成失败: {str(e)}")

    def copy_to_clipboard(self):
        text = self.result_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "提示", "已成功复制到剪贴板")
