"""
定时任务插件
完全独立的定时任务管理插件，不依赖基础框架的数据库
"""

import os
import sys
import json
import time
from datetime import datetime

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox,
    QMessageBox, QWidget, QScrollArea, QFrame, QApplication,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QCheckBox,
    QDateEdit, QTimeEdit, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QDate, QTime, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QColor, QPixmap, QIcon
from PyQt6.QtWidgets import QStyle

from src.plugins.base_plugin import BasePlugin
from src.utils.logger import logger

# 导入独立的定时任务模块
import sys
plugin_dir = os.path.join(os.path.dirname(__file__), 'scheduled_tasks')
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)

from scheduled_tasks.database import get_database
from scheduled_tasks.scheduler import TaskScheduler
from scheduled_tasks.executor import TaskExecutor


class UICallbackHandler(QObject):
    """UI回调处理器，用于在工作线程和主线程之间传递消息"""

    show_message_signal = pyqtSignal(str)
    log_output_signal = pyqtSignal(str)
    task_complete_signal = pyqtSignal(str)
    refresh_logs_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # 信号连接延迟到首次使用时，确保QApplication已准备好
        self._signals_connected = False
        # 记录消息显示时间，防止短时间重复弹窗（5秒内）
        self.message_timestamps = {}
        # 保持对消息框的引用，防止被垃圾回收
        self._active_message_boxes = []

    def _ensure_signals_connected(self):
        """确保信号已连接"""
        if not self._signals_connected:
            try:
                self.show_message_signal.connect(self._on_show_message)
                self.task_complete_signal.connect(self._on_task_complete)
                self._signals_connected = True
                logger.info("[UICallbackHandler] 信号连接成功")
            except Exception as e:
                logger.error(f"[UICallbackHandler] 信号连接失败: {e}")

    def callback(self, action: str, data: str):
        """回调函数，从工作线程调用"""
        self._ensure_signals_connected()
        if action == "show_message":
            self.show_message_signal.emit(data)
        elif action == "task_complete":
            self.task_complete_signal.emit(data)

    def _on_show_message(self, message: str):
        """在主线程显示消息（不中断其他软件操作）"""
        current_time = time.time()

        logger.info(f"[弹窗调试] 尝试显示消息: {message}, 当前时间: {current_time}")
        logger.info(f"[弹窗调试] 已记录的消息时间戳: {self.message_timestamps}")

        # 检查是否在5秒内显示过相同消息
        if message in self.message_timestamps:
            last_time = self.message_timestamps[message]
            time_diff = current_time - last_time
            logger.info(f"[弹窗调试] 消息已存在，距离上次显示: {time_diff}秒")
            if time_diff < 5:  # 5秒内不重复显示
                logger.info(f"[弹窗调试] 消息在5秒内已显示过，跳过重复弹窗: {message}")
                return

        # 更新消息显示时间
        self.message_timestamps[message] = current_time

        logger.info(f"[弹窗调试] 创建消息框...")

        # 创建消息对话框 - 使用exec()阻塞显示确保可见
        msg_box = QMessageBox(parent=None)
        msg_box.setWindowTitle("定时任务提醒")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        # 设置为应用程序模态，确保显示在最前面但不阻塞其他应用
        msg_box.setWindowModality(Qt.WindowModality.ApplicationModal)
        # 使用Dialog窗口类型 + StayOnTop，确保显示并获取焦点
        msg_box.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Dialog |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowTitleHint
        )

        # 使用 PyQt6 标准图标 SP_MessageBoxInformation
        icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
        msg_box.setIconPixmap(icon.pixmap(64, 64))

        # 保持引用防止垃圾回收
        self._active_message_boxes.append(msg_box)

        logger.info(f"[弹窗调试] 显示消息框 (exec阻塞模式)...")
        # 使用exec()阻塞显示，确保用户能看到
        msg_box.exec()

        # 显示完成后移除引用
        if msg_box in self._active_message_boxes:
            self._active_message_boxes.remove(msg_box)

        logger.info(f"[弹窗调试] 消息框已关闭")

    def _on_task_complete(self, info: str):
        """任务完成时的处理"""
        parts = info.split("|")
        if len(parts) >= 2:
            task_name = parts[0]
            status = parts[1]
            logger.info(f"任务完成: {task_name} - {status}")

        # 触发刷新日志信号
        logger.info(f"[信号调试] 准备发送 refresh_logs_signal, ui_handler ID: {id(self)}")
        self.refresh_logs_signal.emit()
        logger.info(f"[信号调试] refresh_logs_signal 已发送")


class CreateTaskDialog(QDialog):
    """创建/编辑任务对话框"""

    def __init__(self, parent=None, task_data=None):
        super().__init__(parent)
        self.task_data = task_data
        self._setup_ui()
        if task_data:
            self._load_task_data()

    def _setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("创建定时任务" if not self.task_data else "编辑定时任务")
        self.setMinimumSize(500, 600)

        layout = QVBoxLayout(self)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(15)

        # 基本信息
        basic_group = QGroupBox("基本信息")
        basic_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
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
        basic_layout = QVBoxLayout()

        # 任务名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("任务名称:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请输入任务名称")
        name_layout.addWidget(self.name_edit)
        basic_layout.addLayout(name_layout)

        # 任务描述
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("任务描述:"))
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("请输入任务描述（可选）")
        desc_layout.addWidget(self.desc_edit)
        basic_layout.addLayout(desc_layout)

        basic_group.setLayout(basic_layout)
        container_layout.addWidget(basic_group)

        # 任务类型
        type_group = QGroupBox("任务类型")
        type_group.setStyleSheet(basic_group.styleSheet())
        type_layout = QVBoxLayout()

        type_label_layout = QHBoxLayout()
        type_label_layout.addWidget(QLabel("任务类型:"))
        self.task_type_combo = QComboBox()
        self.task_type_combo.addItem("显示消息", "message")
        self.task_type_combo.addItem("执行命令", "command")
        self.task_type_combo.currentIndexChanged.connect(self._on_task_type_changed)
        type_label_layout.addWidget(self.task_type_combo)
        type_layout.addLayout(type_label_layout)

        # 任务配置
        self.task_config_label = QLabel("消息内容:")
        type_layout.addWidget(self.task_config_label)

        self.task_config_edit = QTextEdit()
        self.task_config_edit.setPlaceholderText(
            '对于"显示消息"类型，输入要显示的消息文本\n'
            '对于"执行命令"类型，输入要执行的命令'
        )
        self.task_config_edit.setMaximumHeight(100)
        type_layout.addWidget(self.task_config_edit)

        type_group.setLayout(type_layout)
        container_layout.addWidget(type_group)

        # 触发器配置
        trigger_group = QGroupBox("触发器配置")
        trigger_group.setStyleSheet(basic_group.styleSheet())
        trigger_layout = QVBoxLayout()

        # 触发器类型
        trigger_type_layout = QHBoxLayout()
        trigger_type_layout.addWidget(QLabel("触发方式:"))
        self.trigger_type_combo = QComboBox()
        self.trigger_type_combo.addItem("单次执行", "once")
        self.trigger_type_combo.addItem("周期执行", "interval")
        self.trigger_type_combo.addItem("Cron表达式", "cron")
        self.trigger_type_combo.currentIndexChanged.connect(self._on_trigger_type_changed)
        trigger_type_layout.addWidget(self.trigger_type_combo)
        trigger_layout.addLayout(trigger_type_layout)

        # 单次执行配置
        self.once_widget = QWidget()
        once_layout = QVBoxLayout(self.once_widget)
        once_layout.setContentsMargins(0, 0, 0, 0)

        date_time_layout = QHBoxLayout()
        date_time_layout.addWidget(QLabel("执行时间:"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate().addDays(1))
        date_time_layout.addWidget(self.date_edit)

        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime(9, 0))
        date_time_layout.addWidget(self.time_edit)
        once_layout.addLayout(date_time_layout)

        # 周期执行配置
        self.interval_widget = QWidget()
        interval_layout = QVBoxLayout(self.interval_widget)
        interval_layout.setContentsMargins(0, 0, 0, 0)

        interval_time_layout = QHBoxLayout()
        interval_time_layout.addWidget(QLabel("间隔时间:"))

        interval_time_layout.addWidget(QLabel("小时:"))
        self.interval_hours = QSpinBox()
        self.interval_hours.setRange(0, 23)
        self.interval_hours.setValue(1)
        interval_time_layout.addWidget(self.interval_hours)

        interval_time_layout.addWidget(QLabel("分钟:"))
        self.interval_minutes = QSpinBox()
        self.interval_minutes.setRange(0, 59)
        interval_time_layout.addWidget(self.interval_minutes)

        interval_time_layout.addWidget(QLabel("秒:"))
        self.interval_seconds = QSpinBox()
        self.interval_seconds.setRange(0, 59)
        self.interval_seconds.setValue(0)
        interval_time_layout.addWidget(self.interval_seconds)

        interval_layout.addLayout(interval_time_layout)

        # Cron配置
        self.cron_widget = QWidget()
        cron_layout = QVBoxLayout(self.cron_widget)
        cron_layout.setContentsMargins(0, 0, 0, 0)

        cron_time_layout = QHBoxLayout()
        cron_time_layout.addWidget(QLabel("执行时间:"))

        cron_time_layout.addWidget(QLabel("小时:"))
        self.cron_hour = QSpinBox()
        self.cron_hour.setRange(0, 23)
        self.cron_hour.setValue(9)
        cron_time_layout.addWidget(self.cron_hour)

        cron_time_layout.addWidget(QLabel("分钟:"))
        self.cron_minute = QSpinBox()
        self.cron_minute.setRange(0, 59)
        self.cron_minute.setValue(0)
        cron_time_layout.addWidget(self.cron_minute)

        cron_layout.addLayout(cron_time_layout)

        cron_day_layout = QHBoxLayout()
        cron_day_layout.addWidget(QLabel("执行周期:"))

        cron_day_layout.addWidget(QLabel("天:"))
        self.cron_day = QSpinBox()
        self.cron_day.setRange(0, 31)
        self.cron_day.setValue(0)
        self.cron_day.setSpecialValueText("每天")
        cron_day_layout.addWidget(self.cron_day)

        cron_layout.addLayout(cron_day_layout)

        # 默认显示单次执行
        self.once_widget.setVisible(True)
        self.interval_widget.setVisible(False)
        self.cron_widget.setVisible(False)

        trigger_layout.addWidget(self.once_widget)
        trigger_layout.addWidget(self.interval_widget)
        trigger_layout.addWidget(self.cron_widget)

        trigger_group.setLayout(trigger_layout)
        container_layout.addWidget(trigger_group)

        # 启用选项
        self.enabled_check = QCheckBox("启用任务")
        self.enabled_check.setChecked(True)
        container_layout.addWidget(self.enabled_check)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_task_type_changed(self):
        """任务类型改变事件"""
        task_type = self.task_type_combo.currentData()
        if task_type == "message":
            self.task_config_label.setText("消息内容:")
        elif task_type == "command":
            self.task_config_label.setText("命令:")

    def _on_trigger_type_changed(self):
        """触发器类型改变事件"""
        trigger_type = self.trigger_type_combo.currentData()
        self.once_widget.setVisible(trigger_type == "once")
        self.interval_widget.setVisible(trigger_type == "interval")
        self.cron_widget.setVisible(trigger_type == "cron")

    def _load_task_data(self):
        """加载任务数据"""
        if not self.task_data:
            return

        self.name_edit.setText(self.task_data.get("name", ""))
        self.desc_edit.setText(self.task_data.get("description", ""))

        # 任务类型
        task_type = self.task_data.get("task_type", "message")
        index = self.task_type_combo.findData(task_type)
        if index >= 0:
            self.task_type_combo.setCurrentIndex(index)

        # 任务配置
        task_config = self.task_data.get("task_config", {})
        if task_type == "message":
            self.task_config_edit.setPlainText(task_config.get("message", ""))
        elif task_type == "command":
            self.task_config_edit.setPlainText(task_config.get("command", ""))

        # 触发器类型
        trigger_type = self.task_data.get("trigger_type", "once")
        index = self.trigger_type_combo.findData(trigger_type)
        if index >= 0:
            self.trigger_type_combo.setCurrentIndex(index)

        # 触发器配置
        trigger_config = self.task_data.get("trigger_config", {})

        if trigger_type == "once":
            run_date = trigger_config.get("run_date", "")
            if run_date:
                dt = datetime.fromisoformat(run_date)
                self.date_edit.setDate(QDate(dt.year, dt.month, dt.day))
                self.time_edit.setTime(QTime(dt.hour, dt.minute))
        elif trigger_type == "interval":
            self.interval_hours.setValue(trigger_config.get("hours", 1))
            self.interval_minutes.setValue(trigger_config.get("minutes", 0))
            self.interval_seconds.setValue(trigger_config.get("seconds", 0))
        elif trigger_type == "cron":
            hour = trigger_config.get("hour", 9)
            minute = trigger_config.get("minute", 0)
            day = trigger_config.get("day", 0)

            self.cron_hour.setValue(hour if hour != "*" else 9)
            self.cron_minute.setValue(minute if minute != "*" else 0)
            self.cron_day.setValue(day if day != "*" else 0)

        self.enabled_check.setChecked(self.task_data.get("is_enabled", True))

    def get_task_data(self):
        """获取任务数据"""
        task_type = self.task_type_combo.currentData()
        trigger_type = self.trigger_type_combo.currentData()

        # 构建任务配置
        task_config = {}
        if task_type == "message":
            task_config["message"] = self.task_config_edit.toPlainText()
        elif task_type == "command":
            task_config["command"] = self.task_config_edit.toPlainText()

        # 构建触发器配置
        trigger_config = {}
        if trigger_type == "once":
            date = self.date_edit.date()
            time = self.time_edit.time()
            run_date = datetime(date.year(), date.month(), date.day(), time.hour(), time.minute())
            trigger_config["run_date"] = run_date.isoformat()
        elif trigger_type == "interval":
            trigger_config["hours"] = self.interval_hours.value()
            trigger_config["minutes"] = self.interval_minutes.value()
            trigger_config["seconds"] = self.interval_seconds.value()
        elif trigger_type == "cron":
            hour = self.cron_hour.value()
            minute = self.cron_minute.value()
            day = self.cron_day.value()

            trigger_config["hour"] = hour if self.cron_day.value() != self.cron_day.minimum() else "*"
            trigger_config["minute"] = minute
            trigger_config["day"] = day if self.cron_day.value() != self.cron_day.minimum() else "*"
            trigger_config["day_of_week"] = "*"

        return {
            "name": self.name_edit.text().strip(),
            "description": self.desc_edit.text().strip(),
            "task_type": task_type,
            "trigger_type": trigger_type,
            "task_config": task_config,
            "trigger_config": trigger_config,
            "is_enabled": self.enabled_check.isChecked()
        }


class ScheduledTasksPlugin(BasePlugin):
    """定时任务插件（单例模式）"""

    # 共享组件（所有实例共享）
    _shared_db = None
    _shared_scheduler = None
    _shared_executor = None
    _shared_ui_handler = None
    _shared_ui_instance = None  # 共享的UI实例（第一个）
    _lock = False  # 简单的锁，防止并发初始化

    def __new__(cls):
        # 如果已有共享UI实例，返回它（但这会被框架多次调用）
        # 我们不能阻止框架创建多个实例，但可以确保它们共享核心组件
        return super().__new__(cls)

    def __init__(self):
        logger.info(f"[插件初始化调试] __init__ 被调用, ID: {id(self)}")
        if ScheduledTasksPlugin._shared_ui_instance is not None:
            logger.info(f"[插件初始化调试] 已存在主实例: {id(ScheduledTasksPlugin._shared_ui_instance)}")

        # 防止并发初始化
        if ScheduledTasksPlugin._lock:
            logger.info(f"[插件初始化调试] 已有实例正在初始化，等待...")
            # 等待初始化完成
            import time
            while ScheduledTasksPlugin._lock:
                time.sleep(0.001)
            # 使用已初始化的共享组件
            self.db = ScheduledTasksPlugin._shared_db
            self.scheduler = ScheduledTasksPlugin._shared_scheduler
            self.executor = ScheduledTasksPlugin._shared_executor
            self.ui_handler = ScheduledTasksPlugin._shared_ui_handler
            logger.info(f"[插件初始化调试] 等待完成，使用共享组件")
            self._setup_minimal_ui()
            return

        # 如果已有主实例，直接使用共享组件
        if ScheduledTasksPlugin._shared_ui_instance is not None:
            logger.info(f"[插件初始化调试] 主实例已存在，使用共享组件")
            self.db = ScheduledTasksPlugin._shared_db
            self.scheduler = ScheduledTasksPlugin._shared_scheduler
            self.executor = ScheduledTasksPlugin._shared_executor
            self.ui_handler = ScheduledTasksPlugin._shared_ui_handler
            self._setup_minimal_ui()
            return

        # 第一个实例 - 设置锁
        logger.info(f"[插件初始化调试] 这是第一个实例，开始初始化")
        ScheduledTasksPlugin._lock = True

        super().__init__("定时任务", "创建和管理定时执行的任务")

        logger.info(f"[插件初始化调试] ========== 主实例初始化开始 ==========")
        logger.info(f"[插件初始化调试] 插件对象ID: {id(self)}")

        # 初始化共享组件
        ScheduledTasksPlugin._shared_db = get_database()
        ScheduledTasksPlugin._shared_scheduler = TaskScheduler()

        # 创建UI处理器（绑定到这个主实例）
        ScheduledTasksPlugin._shared_ui_handler = UICallbackHandler(self)
        ScheduledTasksPlugin._shared_executor = TaskExecutor(ScheduledTasksPlugin._shared_ui_handler.callback)

        # 引用共享组件
        self.db = ScheduledTasksPlugin._shared_db
        self.scheduler = ScheduledTasksPlugin._shared_scheduler
        self.executor = ScheduledTasksPlugin._shared_executor
        self.ui_handler = ScheduledTasksPlugin._shared_ui_handler

        logger.info(f"[插件初始化调试] executor对象ID: {id(self.executor)}")
        logger.info(f"[插件初始化调试] ui_handler对象ID: {id(self.ui_handler)}")

        # 立即连接信号，确保弹窗能正常工作
        self.ui_handler._ensure_signals_connected()

        # 连接信号：任务完成后自动刷新日志（连接到主实例）
        self.ui_handler.refresh_logs_signal.connect(self._refresh_logs)

        # 保存主实例引用
        ScheduledTasksPlugin._shared_ui_instance = self

        # 标记是否已加载任务，防止重复加载
        self._tasks_loaded = False

        # 加载已保存的任务
        self._load_tasks_from_db()

        # 设置UI
        self._setup_ui()

        # 释放锁
        ScheduledTasksPlugin._lock = False

        logger.info(f"[插件初始化调试] ========== 主实例初始化完成 ==========")

    def _setup_minimal_ui(self):
        """为非主实例创建一个最小的UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        label = QLabel("定时任务插件（使用主实例）")
        label.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        layout.addWidget(label)
        logger.info(f"[插件初始化调试] 非主实例UI已设置")

    def get_widget(self) -> QWidget:
        # 非主实例返回自己（有minimal UI）
        # 主实例返回自己（有完整UI）
        return self

    def on_activate(self):
        # 只有主实例才响应激活
        if self is not ScheduledTasksPlugin._shared_ui_instance:
            logger.info(f"[激活调试] 非主实例被激活，忽略")
            return

        logger.info("定时任务插件被激活")
        self._refresh_task_list()
        self._refresh_logs()  # 加载执行日志

    def on_deactivate(self):
        # 只有主实例才响应停用
        if self is not ScheduledTasksPlugin._shared_ui_instance:
            logger.info(f"[停用调试] 非主实例被停用，忽略")
            return

        if self.scheduler:
            self.scheduler.shutdown()

    def _load_tasks_from_db(self):
        """从数据库加载任务到调度器"""
        # 只有主实例才加载任务
        if self is not ScheduledTasksPlugin._shared_ui_instance:
            logger.info(f"[任务加载调试] 非主实例，跳过任务加载")
            return

        logger.info(f"[任务加载调试] _load_tasks_from_db被调用, 插件ID: {id(self)}, _tasks_loaded={self._tasks_loaded}")

        if self._tasks_loaded:
            logger.info("任务已加载，跳过重复加载")
            return

        if not self.scheduler.is_available():
            logger.warning("调度器不可用，跳过任务加载")
            return

        try:
            tasks = self.db.get_all_tasks(enabled_only=True)
            logger.info(f"[任务加载调试] 找到 {len(tasks)} 个启用任务")

            for task in tasks:
                if task["is_enabled"]:
                    logger.info(f"[任务加载调试] 调度任务: {task['name']}")
                    self._schedule_task(task)

            self._tasks_loaded = True
            logger.info(f"已加载 {len(tasks)} 个任务到调度器")

        except Exception as e:
            logger.error(f"从数据库加载任务失败: {str(e)}")

    def _schedule_task(self, task):
        """将任务添加到调度器"""
        def task_func():
            self.executor.execute_task(task)

        self.scheduler.add_task(
            task["id"],
            task_func,
            task["trigger_type"],
            task["trigger_config"],
            task["name"]
        )

    def _setup_ui(self):
        """设置UI界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建滚动区域
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_widget = QWidget()
        scroll_widget.setObjectName("pluginContainer")
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        main_scroll.setWidget(scroll_widget)
        main_layout.addWidget(main_scroll)

        # 标题和按钮
        header_layout = QHBoxLayout()
        title_label = QLabel("定时任务管理")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        if not self.scheduler.is_available():
            warning_label = QLabel("⚠️ APScheduler 未安装，请运行: pip install APScheduler")
            warning_label.setStyleSheet("color: #e74c3c; font-size: 12px;")
            layout.addWidget(warning_label)

        self.add_btn = QPushButton("新建任务")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.add_btn.clicked.connect(self._create_task)
        header_layout.addWidget(self.add_btn)

        layout.addLayout(header_layout)

        # 任务列表
        list_group = QGroupBox("任务列表")
        list_group.setStyleSheet("""
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
        list_layout = QVBoxLayout()

        self.task_table = QTableWidget()
        self.task_table.setColumnCount(6)
        self.task_table.setHorizontalHeaderLabels([
            "任务名称", "类型", "触发方式", "状态", "下次执行", "操作"
        ])

        header = self.task_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        self.task_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.task_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        list_layout.addWidget(self.task_table)

        list_group.setLayout(list_layout)
        layout.addWidget(list_group)

        # 执行日志
        log_group = QGroupBox("执行日志")
        log_group.setStyleSheet(list_group.styleSheet())
        log_layout = QVBoxLayout()

        self.log_table = QTableWidget()
        self.log_table.setColumnCount(5)
        self.log_table.setHorizontalHeaderLabels([
            "任务", "状态", "开始时间", "结束时间", "输出"
        ])

        log_header = self.log_table.horizontalHeader()
        log_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        log_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        log_header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        log_header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        log_header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        self.log_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.log_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.log_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.log_table.setMaximumHeight(200)
        log_layout.addWidget(self.log_table)

        # 日志操作按钮
        log_btn_layout = QHBoxLayout()

        refresh_log_btn = QPushButton("刷新日志")
        refresh_log_btn.clicked.connect(self._refresh_logs)
        log_btn_layout.addWidget(refresh_log_btn)

        delete_selected_log_btn = QPushButton("删除选中")
        delete_selected_log_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 6px 12px;
                font-size: 13px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        delete_selected_log_btn.clicked.connect(self._delete_selected_log)
        log_btn_layout.addWidget(delete_selected_log_btn)

        clear_all_logs_btn = QPushButton("清空所有")
        clear_all_logs_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 6px 12px;
                font-size: 13px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        clear_all_logs_btn.clicked.connect(self._clear_all_logs)
        log_btn_layout.addWidget(clear_all_logs_btn)

        log_btn_layout.addStretch()
        log_layout.addLayout(log_btn_layout)

        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # 插件说明
        self.description_expanded = False
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

        self.description_content = QTextEdit()
        self.description_content.setReadOnly(True)
        self.description_content.setHtml("""
            <p><strong>定时任务插件</strong> 让您可以创建和管理自动执行的任务。</p>
            <ul>
                <li><strong>支持的任务类型</strong>：
                    <ul>
                        <li>显示消息：在指定时间弹出消息提示</li>
                        <li>执行命令：执行系统命令或脚本</li>
                    </ul>
                </li>
                <li><strong>触发方式</strong>：
                    <ul>
                        <li>单次执行：在指定的日期时间执行一次</li>
                        <li>周期执行：按指定的时间间隔重复执行</li>
                        <li>Cron表达式：使用类似Cron的规则定期执行</li>
                    </ul>
                </li>
                <li><strong>功能特点</strong>：
                    <ul>
                        <li>任务的创建、编辑、删除和启用/禁用</li>
                        <li>实时查看任务执行状态和日志</li>
                        <li>任务持久化存储，重启后自动恢复</li>
                    </ul>
                </li>
            </ul>
        """)

        self.description_scroll = QScrollArea()
        self.description_scroll.setWidget(self.description_content)
        self.description_scroll.setWidgetResizable(True)
        self.description_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.description_scroll.setMaximumHeight(200)
        self.description_scroll.setFixedHeight(50)

        layout.addLayout(description_header_layout)
        layout.addWidget(self.description_scroll)

        # 初始加载数据
        QTimer.singleShot(500, self._refresh_task_list)

    def toggle_description(self):
        """切换插件说明的展开/收起状态"""
        if self.description_expanded:
            self.description_scroll.setFixedHeight(50)
            self.toggle_description_btn.setText("▼ 展开")
            self.description_expanded = False
        else:
            self.description_scroll.setFixedHeight(180)
            self.toggle_description_btn.setText("▲ 收起")
            self.description_expanded = True

    def _refresh_task_list(self):
        """刷新任务列表"""
        try:
            tasks = self.db.get_all_tasks()

            self.task_table.setRowCount(len(tasks))

            for row, task in enumerate(tasks):
                # 任务名称
                self.task_table.setItem(row, 0, QTableWidgetItem(task["name"]))

                # 任务类型
                task_type_text = {
                    "message": "显示消息",
                    "command": "执行命令"
                }.get(task["task_type"], task["task_type"])
                self.task_table.setItem(row, 1, QTableWidgetItem(task_type_text))

                # 触发器类型
                trigger_type_text = {
                    "once": "单次",
                    "interval": "周期",
                    "cron": "Cron"
                }.get(task["trigger_type"], task["trigger_type"])
                self.task_table.setItem(row, 2, QTableWidgetItem(trigger_type_text))

                # 状态
                status_text = "✅ 启用" if task["is_enabled"] else "⏸️ 禁用"
                status_item = QTableWidgetItem(status_text)
                if task["is_enabled"]:
                    status_item.setForeground(QColor("#27ae60"))
                else:
                    status_item.setForeground(QColor("#95a5a6"))
                self.task_table.setItem(row, 3, status_item)

                # 下次执行时间
                next_run = self.scheduler.get_next_run_time(task["id"]) if self.scheduler.is_available() else None
                if next_run:
                    next_run_text = next_run.strftime("%Y-%m-%d %H:%M:%S")
                elif task["is_enabled"]:
                    next_run_text = "等待调度..."
                else:
                    next_run_text = "-"
                self.task_table.setItem(row, 4, QTableWidgetItem(next_run_text))

                # 操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(4, 2, 4, 2)

                edit_btn = QPushButton("编辑")
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        padding: 4px 8px;
                        font-size: 12px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                edit_btn.clicked.connect(lambda checked, t=task: self._edit_task(t))
                btn_layout.addWidget(edit_btn)

                delete_btn = QPushButton("删除")
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: none;
                        padding: 4px 8px;
                        font-size: 12px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, t=task: self._delete_task(t))
                btn_layout.addWidget(delete_btn)

                toggle_btn = QPushButton("禁用" if task["is_enabled"] else "启用")
                toggle_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f39c12;
                        color: white;
                        border: none;
                        padding: 4px 8px;
                        font-size: 12px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #e67e22;
                    }
                """)
                toggle_btn.clicked.connect(lambda checked, t=task: self._toggle_task(t))
                btn_layout.addWidget(toggle_btn)

                self.task_table.setCellWidget(row, 5, btn_widget)

            logger.info(f"刷新任务列表: {len(tasks)} 个任务")

        except Exception as e:
            logger.error(f"刷新任务列表失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"刷新任务列表失败: {str(e)}")

    def _refresh_logs(self):
        """刷新执行日志"""
        # 只有主实例才刷新UI
        if self is not ScheduledTasksPlugin._shared_ui_instance:
            logger.info(f"[日志刷新调试] 非主实例，跳过刷新")
            return

        logger.info(f"[日志刷新调试] _refresh_logs被调用，插件ID: {id(self)}")
        logger.info(f"[日志刷新调试] log_table对象ID: {id(self.log_table)}")

        try:
            logs = self.db.get_all_execution_logs(limit=50)
            logger.info(f"[日志刷新调试] 从数据库获取到 {len(logs)} 条日志")

            self.log_table.setRowCount(len(logs))
            logger.info(f"[日志刷新调试] 设置表格行数: {len(logs)}")

            for row, log in enumerate(logs):
                # 获取任务名称
                task = self.db.get_task_by_id(log["task_id"])
                task_name = task["name"] if task else f"任务 #{log['task_id']}"

                # 状态
                status_text = {
                    "success": "✅ 成功",
                    "failed": "❌ 失败",
                    "running": "⏳ 运行中"
                }.get(log["status"], log["status"])

                self.log_table.setItem(row, 0, QTableWidgetItem(task_name))
                self.log_table.setItem(row, 1, QTableWidgetItem(status_text))
                self.log_table.setItem(row, 2, QTableWidgetItem(
                    log["start_time"].strftime("%Y-%m-%d %H:%M:%S") if log["start_time"] else "-"
                ))
                self.log_table.setItem(row, 3, QTableWidgetItem(
                    log["end_time"].strftime("%Y-%m-%d %H:%M:%S") if log["end_time"] else "-"
                ))

                # 输出
                output = log["output"] or ""
                if log["error_message"]:
                    output += f"\n错误: {log['error_message']}"
                output_item = QTableWidgetItem(output[:100] + "..." if len(output) > 100 else output)
                output_item.setToolTip(output)
                self.log_table.setItem(row, 4, output_item)

            logger.info(f"刷新执行日志: {len(logs)} 条记录")
            logger.info(f"[日志刷新调试] 表格更新完成，表格当前行数: {self.log_table.rowCount()}")

        except Exception as e:
            logger.error(f"刷新执行日志失败: {str(e)}")
            logger.info(f"[日志刷新调试] 刷新失败")
            QMessageBox.critical(self, "错误", f"刷新执行日志失败: {str(e)}")

    def _create_task(self):
        """创建新任务"""
        dialog = CreateTaskDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            task_data = dialog.get_task_data()

            if not task_data["name"]:
                QMessageBox.warning(self, "警告", "请输入任务名称")
                return

            try:
                # 检查任务名是否已存在
                if self.db.get_task(task_data["name"]):
                    QMessageBox.warning(self, "警告", f"任务 '{task_data['name']}' 已存在")
                    return

                # 添加任务到数据库
                task_id = self.db.add_task(
                    task_data["name"],
                    task_data["description"],
                    task_data["task_type"],
                    task_data["trigger_type"],
                    task_data["trigger_config"],
                    task_data["task_config"]
                )

                # 如果启用，添加到调度器
                if task_data["is_enabled"] and self.scheduler.is_available():
                    task = self.db.get_task(task_data["name"])
                    if task:
                        self._schedule_task(task)

                self._refresh_task_list()
                QMessageBox.information(self, "成功", f"任务 '{task_data['name']}' 创建成功")

            except Exception as e:
                logger.error(f"创建任务失败: {str(e)}")
                QMessageBox.critical(self, "错误", f"创建任务失败: {str(e)}")

    def _edit_task(self, task):
        """编辑任务"""
        dialog = CreateTaskDialog(self, task)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            task_data = dialog.get_task_data()

            if not task_data["name"]:
                QMessageBox.warning(self, "警告", "请输入任务名称")
                return

            try:
                # 从调度器移除旧任务
                if self.scheduler.is_available():
                    self.scheduler.remove_task(task["id"])

                # 更新数据库
                self.db.update_task(
                    task["name"],
                    description=task_data["description"],
                    task_type=task_data["task_type"],
                    trigger_type=task_data["trigger_type"],
                    trigger_config=task_data["trigger_config"],
                    task_config=task_data["task_config"],
                    is_enabled=task_data["is_enabled"]
                )

                # 如果启用，重新添加到调度器
                if task_data["is_enabled"] and self.scheduler.is_available():
                    updated_task = self.db.get_task(task["name"])
                    if updated_task:
                        self._schedule_task(updated_task)

                self._refresh_task_list()
                QMessageBox.information(self, "成功", f"任务 '{task_data['name']}' 更新成功")

            except Exception as e:
                logger.error(f"更新任务失败: {str(e)}")
                QMessageBox.critical(self, "错误", f"更新任务失败: {str(e)}")

    def _delete_task(self, task):
        """删除任务"""
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除任务 '{task['name']}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 从调度器移除
                if self.scheduler.is_available():
                    self.scheduler.remove_task(task["id"])

                # 从数据库删除
                self.db.delete_task_by_id(task["id"])

                self._refresh_task_list()
                QMessageBox.information(self, "成功", f"任务 '{task['name']}' 已删除")

            except Exception as e:
                logger.error(f"删除任务失败: {str(e)}")
                QMessageBox.critical(self, "错误", f"删除任务失败: {str(e)}")

    def _toggle_task(self, task):
        """切换任务启用状态"""
        try:
            new_status = not task["is_enabled"]

            # 更新数据库
            self.db.update_task(
                task["name"],
                is_enabled=new_status
            )

            # 更新调度器
            if self.scheduler.is_available():
                if new_status:
                    self._schedule_task(task)
                else:
                    self.scheduler.remove_task(task["id"])

            self._refresh_task_list()

            status_text = "启用" if new_status else "禁用"
            QMessageBox.information(self, "成功", f"任务 '{task['name']}' 已{status_text}")

        except Exception as e:
            logger.error(f"切换任务状态失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"切换任务状态失败: {str(e)}")

    def _delete_selected_log(self):
        """删除选中的日志"""
        selected_items = self.log_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "提示", "请先选择要删除的日志记录")
            return

        # 获取选中的行索引
        selected_rows = sorted(set(item.row() for item in selected_items), reverse=True)

        if not selected_rows:
            return

        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除选中的 {len(selected_rows)} 条日志记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 获取所有日志
                all_logs = self.db.get_all_execution_logs(limit=1000)

                # 根据选中行删除对应的日志
                deleted_count = 0
                for row in selected_rows:
                    if row < len(all_logs):
                        log_id = all_logs[row]["id"]
                        self.db.delete_log_by_id(log_id)
                        deleted_count += 1

                if deleted_count > 0:
                    self._refresh_logs()
                    QMessageBox.information(self, "成功", f"已删除 {deleted_count} 条日志记录")
                else:
                    QMessageBox.warning(self, "警告", "没有找到对应的日志记录")

            except Exception as e:
                logger.error(f"删除日志失败: {str(e)}")
                QMessageBox.critical(self, "错误", f"删除日志失败: {str(e)}")

    def _clear_all_logs(self):
        """清空所有日志"""
        reply = QMessageBox.question(
            self, "确认清空",
            "确定要清空所有执行日志吗？此操作不可恢复！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 清空所有日志
                self.db.clear_execution_logs()
                self._refresh_logs()
                QMessageBox.information(self, "成功", "已清空所有日志记录")
            except Exception as e:
                logger.error(f"清空日志失败: {str(e)}")
                QMessageBox.critical(self, "错误", f"清空日志失败: {str(e)}")
