import json
import os
import sys
import uuid
import time
import threading
from typing import Optional

# 延迟导入第三方依赖
requests = None

from src.utils.logger import logger
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QTextEdit, QLabel, QMessageBox, QGroupBox,
    QWidget, QProgressBar, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject

from src.plugins.base_plugin import BasePlugin


class AudioTaskSignals(QObject):
    """处理任务状态信号"""
    status_updated = pyqtSignal(str)  # 状态描述
    progress_updated = pyqtSignal(int)  # 进度百分比
    result_received = pyqtSignal(str)  # 识别结果文本
    finished = pyqtSignal()  # 任务完成
    error = pyqtSignal(str)  # 错误信息


class LongAudioRecognitionPlugin(BasePlugin):
    """
    录音识别插件：基于火山引擎大模型的录音文件长语音转写工具
    """

    PLUGIN_INFO = {
        "name": "录音识别",
        "description": "基于火山引擎大模型的录音文件长语音转写工具",
        "version": "1.0.2",
        "category": "AI工具",
        "author": "X-Tool",
    }

    def __init__(self):
        super().__init__()
        self.config_file = self._get_config_path()
        self._lazy_import_dependencies()

        # 任务控制
        self.is_running = False
        self.signals = AudioTaskSignals()
        self.last_save_dir = ""

        self._setup_ui()
        self._load_config()
        # UI 创建完成后再连接信号
        self._connect_signals()

    def _lazy_import_dependencies(self):
        """延迟导入 requests"""
        global requests
        if requests is None:
            try:
                import requests as req_module
                requests = req_module
                logger.info("[录音识别插件] requests 导入成功")
            except ImportError:
                logger.error("[录音识别插件] requests 导入失败")

    def _get_config_path(self):
        """获取配置文件路径"""
        from src.utils.path_utils import get_data_directory
        data_dir = get_data_directory()
        config_dir = os.path.join(data_dir, "long_audio_recognition_plugin")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "config.json")

    def _load_config(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.appid_input.setText(config.get("appid", ""))
                    self.token_input.setText(config.get("token", ""))
                    self.resource_id_input.setText(config.get("resource_id", "volc.bigasr.auc"))
                    self.submit_url_input.setText(config.get("submit_url", "https://openspeech.bytedance.com/api/v3/auc/bigmodel/submit"))
                    self.query_url_input.setText(config.get("query_url", "https://openspeech.bytedance.com/api/v3/auc/bigmodel/query"))
            except Exception as e:
                logger.error(f"加载识别配置失败: {e}")

    def _save_config(self):
        """保存配置"""
        config = {
            "appid": self.appid_input.text().strip(),
            "token": self.token_input.text().strip(),
            "resource_id": self.resource_id_input.text().strip(),
            "submit_url": self.submit_url_input.text().strip(),
            "query_url": self.query_url_input.text().strip()
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"保存识别配置失败: {e}")

    def _setup_ui(self):
        """设置UI界面"""
        layout = self.get_content_layout()

        # 1. 音频地址输入
        layout.addWidget(QLabel("音频文件 URL (支持在线 URL，如 TOS/OSS 链接)*"))
        self.audio_url_input = QLineEdit()
        self.audio_url_input.setPlaceholderText("请输入音频文件的在线公网访问链接...")
        layout.addWidget(self.audio_url_input)

        # 2. 控制区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.start_btn = QPushButton("开始识别")
        self.start_btn.setStyleSheet(self._get_btn_qss("#3498db", "#2980b9"))
        self.start_btn.clicked.connect(self._start_task)
        btn_layout.addWidget(self.start_btn)

        self.toggle_config_btn = QPushButton("接口配置")
        self.toggle_config_btn.setStyleSheet(self._get_btn_qss("#95a5a6", "#7f8c8d"))
        self.toggle_config_btn.clicked.connect(self._toggle_config)
        btn_layout.addWidget(self.toggle_config_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 3. 状态与进度
        self.status_group = QGroupBox("处理状态")
        status_layout = QVBoxLayout()
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #606266;")
        status_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        status_layout.addWidget(self.progress_bar)
        self.status_group.setLayout(status_layout)
        layout.addWidget(self.status_group)

        # 4. 配置区域 (默认隐藏)
        self.config_group = QGroupBox("火山引擎接口配置")
        config_layout = QVBoxLayout()

        grid_layout = QHBoxLayout()
        v1 = QVBoxLayout()
        v1.addWidget(QLabel("AppID"))
        self.appid_input = QLineEdit()
        self.appid_input.textChanged.connect(self._save_config)
        v1.addWidget(self.appid_input)

        v2 = QVBoxLayout()
        v2.addWidget(QLabel("Access Token"))
        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.token_input.textChanged.connect(self._save_config)
        v2.addWidget(self.token_input)

        grid_layout.addLayout(v1)
        grid_layout.addLayout(v2)
        config_layout.addLayout(grid_layout)

        config_layout.addWidget(QLabel("Resource ID"))
        self.resource_id_input = QLineEdit("volc.bigasr.auc")
        self.resource_id_input.textChanged.connect(self._save_config)
        config_layout.addWidget(self.resource_id_input)

        config_layout.addWidget(QLabel("Submit API URL"))
        self.submit_url_input = QLineEdit("https://openspeech-direct.zijieapi.com/api/v3/auc/bigmodel/submit")
        self.submit_url_input.textChanged.connect(self._save_config)
        config_layout.addWidget(self.submit_url_input)

        config_layout.addWidget(QLabel("Query API URL"))
        self.query_url_input = QLineEdit("https://openspeech-direct.zijieapi.com/api/v3/auc/bigmodel/query")
        self.query_url_input.textChanged.connect(self._save_config)
        config_layout.addWidget(self.query_url_input)

        self.config_group.setLayout(config_layout)
        self.config_group.setVisible(False)
        layout.addWidget(self.config_group)

        # 5. 识别结果
        layout.addWidget(QLabel("识别结果 (可在此编辑修改)"))
        self.output_area = QTextEdit()
        self.output_area.setPlaceholderText("转写结果将在这里显示...")
        self.output_area.setReadOnly(False)
        self.output_area.setMinimumHeight(250)
        layout.addWidget(self.output_area)

        # 6. 底部操作
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(10)

        self.copy_btn = QPushButton("复制文本")
        self.copy_btn.setStyleSheet(self._get_btn_qss("#2ecc71", "#27ae60"))
        self.copy_btn.clicked.connect(self._copy_result)

        self.export_btn = QPushButton("导出文本")
        self.export_btn.setStyleSheet(self._get_btn_qss("#3498db", "#2980b9"))
        self.export_btn.clicked.connect(self._export_result)

        footer_layout.addStretch()
        footer_layout.addWidget(self.copy_btn)
        footer_layout.addWidget(self.export_btn)
        layout.addLayout(footer_layout)

        # 7. 插件说明
        description_html = """
            <h3>录音识别工具</h3>
            <ul>
                <li><strong>语音转写</strong>：基于火山引擎大模型，将长音频文件转换为文字。</li>
                <li><strong>发言人识别</strong>：支持说话人分离，自动标注不同发言人。</li>
                <li><strong>智能标点</strong>：自动添加标点符号，优化断句。</li>
                <li><strong>配置保存</strong>：API 配置自动保存，无需重复填写。</li>
            </ul>
        """
        header_layout, content_text, toggle_btn, scroll_area = self.create_description_section(description_html)
        layout.addLayout(header_layout)
        layout.addWidget(scroll_area)

    def _connect_signals(self):
        """连接信号"""
        self.signals.status_updated.connect(self.status_label.setText)
        self.signals.progress_updated.connect(self.progress_bar.setValue)
        self.signals.result_received.connect(self._on_result_received)
        self.signals.finished.connect(self._on_task_finished)
        self.signals.error.connect(self._on_task_error)

    def _get_btn_qss(self, normal_color, hover_color):
        return f"""
            QPushButton {{
                background-color: {normal_color};
                color: white;
                border: none;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """

    def _toggle_config(self):
        self.config_group.setVisible(not self.config_group.isVisible())

    def _copy_result(self):
        text = self.output_area.toPlainText().strip()
        if text:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "提示", "内容已复制到剪贴板")

    def _export_result(self):
        """导出识别结果为文本文件"""
        text = self.output_area.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "提醒", "当前没有可导出的内容")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出识别结果", self.last_save_dir, "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                # 记住这次保存的目录
                self.last_save_dir = os.path.dirname(file_path)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                QMessageBox.information(self, "成功", f"识别结果已导出至：\n{file_path}")
            except Exception as e:
                logger.error(f"导出识别结果失败: {e}")
                QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")

    def _start_task(self):
        if self.is_running:
            return

        audio_url = self.audio_url_input.text().strip()
        if not audio_url:
            QMessageBox.warning(self, "提醒", "请输入音频 URL")
            return

        appid = self.appid_input.text().strip()
        token = self.token_input.text().strip()
        if not appid or not token:
            QMessageBox.warning(self, "提醒", "请先在接口配置中填写 AppID 和 Token")
            self.config_group.setVisible(True)
            return

        if requests is None:
            QMessageBox.critical(self, "错误", "缺少 requests 依赖")
            return

        self.is_running = True
        self.start_btn.setEnabled(False)
        self.start_btn.setText("正在识别...")
        self.output_area.clear()
        self.progress_bar.setValue(0)

        threading.Thread(target=self._run_recognition_workflow, args=(audio_url,), daemon=True).start()

    def _run_recognition_workflow(self, audio_url):
        """核心识别工作流"""
        try:
            appid = self.appid_input.text().strip()
            token = self.token_input.text().strip()
            resource_id = self.resource_id_input.text().strip()
            submit_url = self.submit_url_input.text().strip()
            query_url = self.query_url_input.text().strip()

            task_id = str(uuid.uuid4())

            # 1. 提交任务
            self.signals.status_updated.emit("正在提交识别任务...")
            self.signals.progress_updated.emit(10)

            headers = {
                "X-Api-App-Key": appid,
                "X-Api-Access-Key": token,
                "X-Api-Resource-Id": resource_id,
                "X-Api-Request-Id": task_id,
                "X-Api-Sequence": "-1"
            }

            payload = {
                "user": {"uid": f"user_{int(time.time())}"},
                "audio": {"url": audio_url},
                "request": {
                    "model_name": "bigmodel",
                    "enable_channel_split": True,
                    "enable_ddc": True,
                    "enable_speaker_info": True,
                    "enable_punc": True,
                    "enable_itn": True,
                    "corpus": {
                        "correct_table_name": "",
                        "context": ""
                    }
                }
            }

            resp = requests.post(submit_url, json=payload, headers=headers, timeout=30)
            res_headers = resp.headers
            status_code = res_headers.get("X-Api-Status-Code")

            if status_code != "20000000":
                error_msg = res_headers.get("X-Api-Message", "提交任务失败")
                self.signals.error.emit(f"提交失败 ({status_code}): {error_msg}")
                return

            x_tt_logid = res_headers.get("X-Tt-Logid", "")
            logger.info(f"任务提交成功: task_id={task_id}, logid={x_tt_logid}")

            # 2. 轮询状态
            self.signals.status_updated.emit("任务提交成功，正在等待识别结果...")
            self.signals.progress_updated.emit(20)

            max_retries = 120  # 最多等待 120 次 (约 2-4 分钟)
            retry_count = 0

            query_headers = {
                "X-Api-App-Key": appid,
                "X-Api-Access-Key": token,
                "X-Api-Resource-Id": resource_id,
                "X-Api-Request-Id": task_id,
                "X-Tt-Logid": x_tt_logid
            }

            while retry_count < max_retries:
                time.sleep(2)
                retry_count += 1

                query_resp = requests.post(query_url, json={}, headers=query_headers, timeout=30)
                q_status = query_resp.headers.get("X-Api-Status-Code")

                if q_status == "20000000":  # SUCCESS
                    result_json = query_resp.json()
                    # 提取转写文本
                    utterances = result_json.get("result", {}).get("utterances", [])
                    full_text = ""
                    for utt in utterances:
                        speaker = f"发言人 {utt.get('speaker_id', '?')}"
                        text = utt.get("text", "")
                        full_text += f"{speaker}: {text}\n"

                    if not full_text:
                        # 尝试兜底提取
                        full_text = result_json.get("result", {}).get("text", "识别成功但未找到文本内容")

                    self.signals.result_received.emit(full_text)
                    self.signals.status_updated.emit("识别完成")
                    self.signals.progress_updated.emit(100)
                    self.signals.finished.emit()
                    return

                elif q_status in ["20000001", "20000002"]:  # PROCESSING
                    prog = min(20 + retry_count * 2, 95)
                    self.signals.progress_updated.emit(prog)
                    self.signals.status_updated.emit(f"识别中，已等待 {retry_count*2}s...")

                else:
                    error_msg = query_resp.headers.get("X-Api-Message", "查询任务失败")
                    self.signals.error.emit(f"识别出错 ({q_status}): {error_msg}")
                    return

            self.signals.error.emit("识别超时，请稍后检查音频链接是否有效")

        except Exception as e:
            logger.error(f"识别任务流程异常: {e}")
            self.signals.error.emit(f"发生异常: {str(e)}")

    def _on_result_received(self, text):
        self.output_area.setPlainText(text)

    def _on_task_finished(self):
        self.is_running = False
        self.start_btn.setEnabled(True)
        self.start_btn.setText("开始识别")
        QMessageBox.information(self, "成功", "语音转写已完成！")

    def _on_task_error(self, err):
        self.is_running = False
        self.start_btn.setEnabled(True)
        self.start_btn.setText("开始识别")
        self.status_label.setText("出错")
        QMessageBox.critical(self, "识别失败", err)

    def get_widget(self):
        return self

    def on_activate(self):
        logger.info("录音识别插件被激活")

    def on_deactivate(self):
        pass