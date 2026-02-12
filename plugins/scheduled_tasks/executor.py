"""
任务执行器模块
负责执行不同类型的定时任务
"""

import subprocess
from datetime import datetime
from typing import Dict, Any, Callable

from PyQt6.QtWidgets import QApplication, QMessageBox

from src.utils.logger import logger

from .database import get_database


class TaskExecutor:
    """任务执行器类"""

    def __init__(self, ui_callback: Callable[[str, str], None] = None):
        """初始化任务执行器

        Args:
            ui_callback: UI回调函数，用于在主线程显示消息等操作
                        签名: callback(action: str, data: str)
                        action: "show_message" | "log_output" | "task_complete"
                        data: 消息内容、日志或完成信息
        """
        self.ui_callback = ui_callback
        self.db = get_database()

    def execute_task(self, task: Dict[str, Any]) -> bool:
        """执行任务

        Args:
            task: 任务信息字典

        Returns:
            是否执行成功
        """
        task_id = task["id"]
        task_name = task["name"]
        task_type = task["task_type"]
        task_config = task["task_config"]

        logger.info(f"[执行器调试] execute_task被调用, 任务名: {task_name}, ID: {task_id}")
        logger.info(f"[执行器调试] executor对象ID: {id(self)}")

        start_time = datetime.now()
        status = "success"
        output = ""
        error_message = ""

        logger.info(f"开始执行任务: {task_name} (ID: {task_id})")

        try:
            if task_type == "message":
                output = self._execute_message(task_config)

            elif task_type == "command":
                output, error_message = self._execute_command(task_config)
                if error_message:
                    status = "failed"

            else:
                status = "failed"
                error_message = f"不支持的任务类型: {task_type}"

            logger.info(f"任务 '{task_name}' 执行{'成功' if status == 'success' else '失败'}")

        except Exception as e:
            status = "failed"
            error_message = str(e)
            logger.error(f"任务 '{task_name}' 执行异常: {str(e)}")

        finally:
            # 记录执行日志
            end_time = datetime.now()
            try:
                self.db.add_execution_log(
                    task_id, status, start_time.isoformat(), end_time.isoformat(),
                    output, error_message
                )

                # 更新任务最后执行时间
                self.db.update_task(task_name, last_run_time=start_time.isoformat())

                # 通知UI任务完成
                if self.ui_callback:
                    self.ui_callback("task_complete", f"{task_name}|{status}|{error_message}")

            except Exception as e:
                logger.error(f"记录执行日志失败: {str(e)}")

        return status == "success"

    def _execute_message(self, task_config: Dict[str, Any]) -> str:
        """执行消息任务

        Args:
            task_config: 任务配置

        Returns:
            执行输出
        """
        message = task_config.get("message", "定时任务执行")
        output = f"显示消息: {message}"

        logger.info(f"[消息执行调试] 准备显示消息: {message}")
        logger.info(f"[消息执行调试] ui_callback是否存在: {self.ui_callback is not None}")
        if self.ui_callback:
            logger.info(f"[消息执行调试] 调用ui_callback...")
            self.ui_callback("show_message", message)
            logger.info(f"[消息执行调试] ui_callback调用完成")

        return output

    def _execute_command(self, task_config: Dict[str, Any]) -> tuple:
        """执行命令任务

        Args:
            task_config: 任务配置

        Returns:
            (输出, 错误信息) 元组
        """
        command = task_config.get("command", "")
        if not command:
            return "", "命令为空"

        try:
            # 执行命令
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )

            output = result.stdout
            error_message = result.stderr

            if result.returncode != 0:
                error_message = f"命令执行失败 (返回码: {result.returncode})\n{error_message}"

            return output, error_message

        except subprocess.TimeoutExpired:
            return "", "命令执行超时（超过5分钟）"
        except Exception as e:
            return "", f"命令执行异常: {str(e)}"

    def set_ui_callback(self, callback: Callable[[str, str], None]):
        """设置UI回调函数

        Args:
            callback: UI回调函数
        """
        self.ui_callback = callback
