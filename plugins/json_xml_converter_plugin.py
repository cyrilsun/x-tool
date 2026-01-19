import json
import xml.etree.ElementTree as ET
import xml.dom.minidom
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox, 
    QMessageBox, QWidget, QScrollArea, QPlainTextEdit, QFrame, 
    QApplication, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from src.plugins.base_plugin import BasePlugin
from src.utils.logger import logger

class XmlJsonConverterPlugin(BasePlugin):
    """
    XML/JSON 互转插件
    支持 XML 转 JSON 以及 JSON 转 XML，具备格式化输出选项
    """
    
    XML_SAMPLE = """<note>
    <to>Tove</to>
    <from>Jani</from>
    <heading>Reminder</heading>
    <body>Don't forget me this weekend!</body>
</note>"""

    JSON_SAMPLE = """{
    "note": {
        "to": "Tove",
        "from": "Jani",
        "heading": "Reminder",
        "body": "Don't forget me this weekend!"
    }
}"""

    def __init__(self):
        super().__init__("XML/JSON互转", "支持 XML 与 JSON 格式的相互转换")
        self._setup_ui()

    def get_widget(self) -> QWidget:
        return self

    def on_activate(self):
        logger.info("XML/JSON互转插件被激活")

    def _setup_ui(self):
        """设置UI界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 全局滚动区域
        main_scroll = QScrollArea(self)
        main_scroll.setWidgetResizable(True)
        main_scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        scroll_widget = QWidget()
        scroll_widget.setObjectName("pluginContainer")
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        main_scroll.setWidget(scroll_widget)
        main_layout.addWidget(main_scroll)

        # 1. 标题
        title_label = QLabel("XML/JSON互转")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 5px;")
        layout.addWidget(title_label)

        # 2. 编辑器区域 (双栏布局)
        editor_container = QHBoxLayout()
        editor_container.setSpacing(20)

        # 左侧输入
        left_layout = QVBoxLayout()
        input_label_layout = QHBoxLayout()
        input_label = QLabel("输入数据(XML或JSON) : ")
        
        xml_sample_btn = QPushButton("XML样例")
        xml_sample_btn.setFlat(True)
        xml_sample_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        xml_sample_btn.setStyleSheet("color: #3498db; text-decoration: underline; border: none; background: transparent; padding: 0;")
        xml_sample_btn.clicked.connect(lambda: self.input_editor.setPlainText(self.XML_SAMPLE))
        
        sep_label = QLabel("、")
        
        json_sample_btn = QPushButton("JSON样例")
        json_sample_btn.setFlat(True)
        json_sample_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        json_sample_btn.setStyleSheet("color: #3498db; text-decoration: underline; border: none; background: transparent; padding: 0;")
        json_sample_btn.clicked.connect(lambda: self.input_editor.setPlainText(self.JSON_SAMPLE))

        input_label_layout.addWidget(input_label)
        input_label_layout.addWidget(xml_sample_btn)
        input_label_layout.addWidget(sep_label)
        input_label_layout.addWidget(json_sample_btn)
        input_label_layout.addStretch()
        
        self.input_editor = QPlainTextEdit()
        self.input_editor.setPlaceholderText("粘贴 XML 或 JSON 数据于此...")
        self.input_editor.setStyleSheet(self._get_editor_qss())
        self.input_editor.setMinimumHeight(400)
        
        left_layout.addLayout(input_label_layout)
        left_layout.addWidget(self.input_editor)

        # 右侧结果
        right_layout = QVBoxLayout()
        result_label = QLabel("转换结果 :")
        self.result_editor = QPlainTextEdit()
        self.result_editor.setReadOnly(True)
        self.result_editor.setPlaceholderText("转换后的结果将显示在这里...")
        self.result_editor.setStyleSheet(self._get_editor_qss())
        self.result_editor.setMinimumHeight(400)
        
        right_layout.addWidget(result_label)
        right_layout.addWidget(self.result_editor)

        editor_container.addLayout(left_layout, 1)
        editor_container.addLayout(right_layout, 1)
        layout.addLayout(editor_container)

        # 3. 底部操作按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.xml_to_json_btn = QPushButton("XML转换为JSON")
        self.xml_to_json_btn.setStyleSheet(self._get_btn_qss("#3498db", "#2980b9"))
        self.xml_to_json_btn.clicked.connect(self.convert_xml_to_json)
        
        self.json_to_xml_btn = QPushButton("JSON转换为XML")
        self.json_to_xml_btn.setStyleSheet(self._get_btn_qss("#3498db", "#2980b9"))
        self.json_to_xml_btn.clicked.connect(self.convert_json_to_xml)

        self.pretty_check = QCheckBox("PRETTY JSON / XML")
        self.pretty_check.setChecked(True)
        self.pretty_check.setStyleSheet("margin-left: 10px; color: #2c3e50; font-weight: bold;")

        self.copy_btn = QPushButton("复制结果")
        self.copy_btn.setStyleSheet(self._get_btn_qss("#2ecc71", "#27ae60"))
        self.copy_btn.clicked.connect(self.copy_to_clipboard)

        self.clear_btn = QPushButton("清空")
        self.clear_btn.setStyleSheet(self._get_btn_qss("#e74c3c", "#c0392b"))
        self.clear_btn.clicked.connect(self.clear_all)

        btn_layout.addWidget(self.xml_to_json_btn)
        btn_layout.addWidget(self.json_to_xml_btn)
        btn_layout.addWidget(self.pretty_check)
        btn_layout.addStretch()
        btn_layout.addWidget(self.copy_btn)
        btn_layout.addWidget(self.clear_btn)
        layout.addLayout(btn_layout)

        # 4. 插件说明
        self.description_expanded = False
        description_header_layout = QHBoxLayout()
        description_title = QLabel("<h3 style='margin: 0;'>插件说明</h3>")
        self.toggle_description_btn = QPushButton("▼ 展开")
        self.toggle_description_btn.setStyleSheet("background-color: #f8f9fa; color: #343a40; border: 1px solid #dee2e6; padding: 4px 8px; font-size: 12px; border-radius: 4px;")
        self.toggle_description_btn.clicked.connect(self.toggle_description)
        description_header_layout.addWidget(description_title)
        description_header_layout.addStretch()
        description_header_layout.addWidget(self.toggle_description_btn)
        
        self.description_content = QPlainTextEdit()
        self.description_content.setReadOnly(True)
        self.description_content.setPlainText(
            "XML/JSON互转工具说明：\n"
            "1. XML 转 JSON：解析 XML 结构并生成对应的 JSON 格式，支持处理属性及嵌套标签。\n"
            "2. JSON 转 XML：将 JSON 对象转为 XML 结构，根节点默认使用 'root' 或首个键名。\n"
            "3. PRETTY：勾选后输出将包含缩进，方便阅读；不勾选则输出紧凑型文本。\n"
            "4. 容错提示：如果输入的数据格式不符合规范，插件会给出具体的错误原因。"
        )
        self.description_scroll = QScrollArea()
        self.description_scroll.setWidget(self.description_content)
        self.description_scroll.setWidgetResizable(True)
        self.description_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.description_scroll.setFixedHeight(50)
        
        layout.addLayout(description_header_layout)
        layout.addWidget(self.description_scroll)

    def _get_editor_qss(self):
        return """
            QPlainTextEdit {
                background-color: #ffffff;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 13px;
                padding: 10px;
                line-height: 1.4;
            }
        """

    def _get_btn_qss(self, normal_color, hover_color):
        return f"""
            QPushButton {{ 
                background-color: {normal_color}; 
                color: white; 
                border: none; 
                padding: 8px 16px; 
                font-size: 13px; 
                font-weight: bold; 
                border-radius: 4px; 
            }}
            QPushButton:hover {{ 
                background-color: {hover_color}; 
            }}
        """

    def toggle_description(self):
        if self.description_expanded:
            self.description_scroll.setFixedHeight(50)
            self.toggle_description_btn.setText("▼ 展开")
            self.description_expanded = False
        else:
            self.description_scroll.setFixedHeight(120)
            self.toggle_description_btn.setText("▲ 收起")
            self.description_expanded = True

    def clear_all(self):
        self.input_editor.clear()
        self.result_editor.clear()

    def convert_xml_to_json(self):
        """XML 转换为 JSON"""
        text = self.input_editor.toPlainText().strip()
        if not text:
            return
        
        try:
            root = ET.fromstring(text)
            data = self._xml_to_dict(root)
            
            # Wrap in root tag name to preserve structure
            result_dict = {root.tag: data}
            
            indent = 4 if self.pretty_check.isChecked() else None
            json_res = json.dumps(result_dict, indent=indent, ensure_ascii=False)
            self.result_editor.setPlainText(json_res)
        except Exception as e:
            QMessageBox.critical(self, "XML 解析错误", f"无效的 XML 格式！\n错误信息: {str(e)}")

    def _xml_to_dict(self, element):
        """递归将 XML 元素转为字典"""
        res = {}
        # 处理属性
        for name, value in element.attrib.items():
            res[f"@{name}"] = value
            
        # 处理子节点
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in res:
                if isinstance(res[child.tag], list):
                    res[child.tag].append(child_data)
                else:
                    res[child.tag] = [res[child.tag], child_data]
            else:
                res[child.tag] = child_data
        
        # 处理文本内容
        if element.text and element.text.strip():
            if not res:
                return element.text.strip()
            res["#text"] = element.text.strip()
            
        return res or ""

    def convert_json_to_xml(self):
        """JSON 转换为 XML"""
        text = self.input_editor.toPlainText().strip()
        if not text:
            return
        
        try:
            data = json.loads(text)
            if not isinstance(data, dict):
                raise ValueError("JSON 顶层必须是一个对象")
            
            # 确定根节点
            if len(data) == 1:
                root_tag = list(data.keys())[0]
                root_data = data[root_tag]
            else:
                root_tag = "root"
                root_data = data
                
            root_elem = self._dict_to_xml(root_tag, root_data)
            
            raw_xml = ET.tostring(root_elem, encoding='utf-8')
            
            if self.pretty_check.isChecked():
                dom = xml.dom.minidom.parseString(raw_xml)
                formatted_xml = dom.toprettyxml(indent="    ")
                # 移除多余空行
                formatted_xml = "\n".join([line for line in formatted_xml.splitlines() if line.strip()])
                self.result_editor.setPlainText(formatted_xml)
            else:
                self.result_editor.setPlainText(raw_xml.decode('utf-8'))
                
        except Exception as e:
            QMessageBox.critical(self, "JSON 解析错误", f"无效的 JSON 格式！\n错误信息: {str(e)}")

    def _dict_to_xml(self, tag, d):
        """递归将字典转为 XML 元素"""
        elem = ET.Element(tag)
        if isinstance(d, dict):
            for key, val in d.items():
                if key.startswith("@"):
                    elem.set(key[1:], str(val))
                elif key == "#text":
                    elem.text = str(val)
                elif isinstance(val, list):
                    for item in val:
                        elem.append(self._dict_to_xml(key, item))
                else:
                    elem.append(self._dict_to_xml(key, val))
        else:
            elem.text = str(d)
        return elem

    def copy_to_clipboard(self):
        """复制结果到剪贴板"""
        text = self.result_editor.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "提示", "已成功复制到剪贴板")
        else:
            QMessageBox.warning(self, "警告", "没有可复制的内容")
