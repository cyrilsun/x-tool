import os
import sys
import logging
from typing import List, Dict, Any
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QTextEdit, QLabel, QMessageBox, QGroupBox

from src.plugins.base_plugin import BasePlugin

# 尝试导入 pymysql，并记录错误信息
def try_import_pymysql():
    try:
        import pymysql
        return pymysql, "Success"
    except Exception as e:
        return None, str(e)

pymysql, import_error_msg = try_import_pymysql()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('WorkOrderTool')


class WorkOrderBackTool:
    def __init__(self, host: str, port: int, user: str, password: str, database: str = None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=pymysql.cursors.DictCursor
            )
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False

    def close(self):
        if self.connection and self.connection.open:
            self.connection.close()

    def huitoukan_to_handle(self, order_list: List[str]):
        if not self.connection or not self.connection.open:
            if not self.connect():
                return {"status": "error", "message": "数据库连接失败"}

        try:
            with self.connection.cursor() as cursor:
                results = []
                for order_id in order_list:
                    sql = "SELECT id, gdh, qdcb, htkzt, htkshzt, htkclfs, htkclzt FROM tb_gov_hot_line WHERE gdh = %s"
                    cursor.execute(sql, (order_id,))
                    result = cursor.fetchall()
                    logger.info(f'根据工单号: {order_id}, 查询工单信息: {result}')

                    if not result:
                        results.append({"status": "error", "message": f"工单 {order_id} 不存在", "order": order_id})
                        continue
                    if len(result) > 1:
                        for item in result:
                            if item['qdcb'] == 1:
                                sql1 = "update tb_gov_hot_line set htkzt =1, htkshzt=0, htkclfs=0, htkclzt=0 WHERE id = %s"
                                logger.info(f'执行更新重办工单表回头看状态SQL: {sql1}, 参数: {item["id"]}')
                                cursor.execute(sql1, (item['id'],))
                                sql2 = "update tb_gov_hot_line_handle_department set htkzt =1, htkshzt=0, htkclfs=0, htkclzt=0 WHERE event_id = %s"
                                logger.info(f'执行更新重办单办理部门回头看状态SQL: {sql2}, 参数: {item["id"]}')
                                cursor.execute(sql2, (item['id'],))
                            else:
                                sql1 = "update tb_gov_hot_line set htkzt =0, htkshzt=0, htkclfs=0, htkclzt=0 WHERE id = %s"
                                logger.info(f'执行更新重办工单表回头看状态SQL: {sql1}, 参数: {item["id"]}')
                                cursor.execute(sql1, (item['id'],))
                                sql2 = "update tb_gov_hot_line_handle_department set htkzt =0, htkshzt=0, htkclfs=0, htkclzt=0 WHERE event_id = %s"
                                logger.info(f'执行更新重办单办理部门回头看状态SQL: {sql2}, 参数: {item["id"]}')
                                cursor.execute(sql2, (item['id'],))
                    else:
                        for item in result:
                            sql1 = "update tb_gov_hot_line set htkzt =1, htkshzt=0, htkclfs=0, htkclzt=0 WHERE id = %s"
                            logger.info(f'执行更新办理单工单表回头看状态SQL: {sql1}, 参数: {item["id"]}')
                            cursor.execute(sql1, (item['id'],))
                            sql2 = "update tb_gov_hot_line_handle_department set htkzt =1, htkshzt=0, htkclfs=0, htkclzt=0 WHERE event_id = %s"
                            logger.info(f'执行更新办理单办理部门回头看状态SQL: {sql2}, 参数: {item["id"]}')
                            cursor.execute(sql2, (item['id'],))
                self.connection.commit()
                return {"status": "success", "results": results}

        except Exception as e:
            self.connection.rollback()
            return {"status": "error", "message": f"处理工单时发生错误: {str(e)}"}
        finally:
            self.close()

    def huitoukan_qd_pass2(self, order_list: List[str]):
        if not self.connection or not self.connection.open:
            if not self.connect():
                return {"status": "error", "message": "数据库连接失败"}

        try:
            with self.connection.cursor() as cursor:
                results = []
                for order_id in order_list:
                    sql = "SELECT id, gdh, qdcb, htkzt, htkshzt, htkclfs, htkclzt FROM tb_gov_hot_line WHERE gdh = %s and htkshzt = 2"
                    cursor.execute(sql, (order_id,))
                    result = cursor.fetchall()
                    logger.info(f'根据工单号: {order_id}, 查询工单信息: {result}')

                    if not result:
                        results.append({"status": "error", "message": f"工单 {order_id} 不存在", "order": order_id})
                        continue
                    for item in result:
                        sql1 = "update tb_gov_hot_line set  htkshzt=3 WHERE id = %s and htkshzt=2"
                        logger.info(f'执行更新办理单工单表回头看状态SQL: {sql1}, 参数: {item["id"]}')
                        cursor.execute(sql1, (item['id'],))
                        sql2 = "update tb_gov_hot_line_handle_department set htkshzt=3 WHERE event_id = %s and htkshzt=2"
                        logger.info(f'执行更新办理单办理部门回头看审核状态SQL: {sql2}, 参数: {item["id"]}')
                        cursor.execute(sql2, (item['id'],))
                self.connection.commit()
                return {"status": "success", "results": results}

        except Exception as e:
            self.connection.rollback()
            return {"status": "error", "message": f"处理工单时发生错误: {str(e)}"}
        finally:
            self.close()

    def huitoukan_remove_2(self, order_list: List[str]):
        if not self.connection or not self.connection.open:
            if not self.connect():
                return {"status": "error", "message": "数据库连接失败"}

        try:
            with self.connection.cursor() as cursor:
                results = []
                for order_id in order_list:
                    sql = "SELECT id, gdh, qdcb, htkzt, htkshzt, htkclfs, htkclzt FROM tb_gov_hot_line WHERE gdh = %s"
                    cursor.execute(sql, (order_id,))
                    result = cursor.fetchall()
                    logger.info(f'根据工单号: {order_id}, 查询工单信息: {result}')

                    if not result:
                        results.append({"status": "error", "message": f"工单 {order_id} 不存在", "order": order_id})
                        continue
                    for item in result:
                        sql1 = "update tb_gov_hot_line set htkzt =0, htkshzt=0, htkclfs=0, htkclzt=0 WHERE id = %s"
                        logger.info(f'执行更新工单表回头看待处理状态SQL: {sql1}, 参数: {item["id"]}')
                        cursor.execute(sql1, (item['id'],))
                        sql2 = "update tb_gov_hot_line_handle_department set htkzt =0, htkshzt=0, htkclfs=0, htkclzt=0 WHERE event_id = %s"
                        logger.info(f'执行更新办理部门回头看待处理状态SQL: {sql2}, 参数: {item["id"]}')
                        cursor.execute(sql2, (item['id'],))
                self.connection.commit()
                return {"status": "success", "results": results}

        except Exception as e:
            self.connection.rollback()
            return {"status": "error", "message": f"处理工单时发生错误: {str(e)}"}
        finally:
            self.close()


class HuitoukanPlugin(BasePlugin):
    def __init__(self):
        super().__init__("回头看工单", "设置回头看工单的状态")

        # 再次尝试导入（防止路径加载延迟）
        global pymysql, import_error_msg
        if pymysql is None:
            from src.utils.path_utils import get_lib_directory
            lib_dir = get_lib_directory()
            if lib_dir not in sys.path:
                sys.path.insert(0, lib_dir)
            pymysql, import_error_msg = try_import_pymysql()

        # 检查 pymysql 依赖
        if pymysql is None:
            self.work_order_back_tool = None
            self._show_dependency_error = True
        else:
            self.work_order_back_tool = WorkOrderBackTool(
                host="112.6.205.8",
                port=35403,
                user="user_gov_update",
                password="$137%Nauk4C2@*J4qP!",
                database="jiaoxinban"
            )
            self._show_dependency_error = False

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        status_group = QGroupBox("工单状态操作")
        status_group.setStyleSheet("""
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

        status_layout = QVBoxLayout()

        status_select_layout = QHBoxLayout()
        status_label = QLabel("选择操作类型：")
        status_label.setStyleSheet("font-size: 14px; color: #34495e;")
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            "移入待处理",
            "移出回头看",
            "青岛已通过"
        ])
        self.status_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                min-width: 180px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(noimg);
                width: 0px;
                height: 0px;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #7f8c8d;
            }
        """)
        status_select_layout.addWidget(status_label)
        status_select_layout.addWidget(self.status_combo)
        status_select_layout.addStretch()
        status_layout.addLayout(status_select_layout)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        input_group = QGroupBox("工单列表")
        input_group.setStyleSheet("""
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

        input_layout = QVBoxLayout()

        self.work_order_text = QTextEdit()
        self.work_order_text.setPlaceholderText("请输入工单号，每行一个工单号。")
        self.work_order_text.setMinimumHeight(250)
        self.work_order_text.setStyleSheet("""
            QTextEdit {
                padding: 10px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #ffffff;
            }
        """)
        input_layout.addWidget(self.work_order_text)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.update_button = QPushButton("更新")
        self.update_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.update_button.clicked.connect(self.update_work_orders)
        button_layout.addWidget(self.update_button)

        self.reset_button = QPushButton("重置")
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
                min-width: 100px;
                margin-left: 10px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """)
        self.reset_button.clicked.connect(self.reset_work_orders)
        button_layout.addWidget(self.reset_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def get_widget(self) -> "HuitoukanPlugin":
        return self

    def update_work_orders(self):
        # 检查依赖
        if self._show_dependency_error:
            from src.utils.path_utils import get_lib_directory
            expected_lib_path = get_lib_directory()
            
            # 获取实际目录内容用于诊断
            dir_contents = "目录不存在"
            if os.path.exists(expected_lib_path):
                try:
                    dir_contents = str(os.listdir(expected_lib_path))
                except Exception as e:
                    dir_contents = f"读取失败: {str(e)}"
            
            QMessageBox.critical(
                self, 
                "依赖缺失", 
                f"PyMySQL 库加载失败！\n\n"
                f"预期路径：{expected_lib_path}\n"
                f"目录内容：{dir_contents}\n"
                f"具体错误：{import_error_msg}\n\n"
                "请确保在上述目录下存在 pymysql 文件夹。\n"
                "如果您在项目根目录下执行过：\n"
                "pip install -t lib pymysql\n"
                "请重新运行软件。 "
            )
            return
        
        selected_index = self.status_combo.currentIndex()

        work_order_text = self.work_order_text.toPlainText()
        work_order_list = [wo.strip() for wo in work_order_text.splitlines() if wo.strip()]

        if not work_order_list:
            QMessageBox.warning(self, "警告", "请输入至少一个工单号")
            return

        reply = QMessageBox.question(
            self,
            "确认操作",
            f"您选择了 '{self.status_combo.currentText()}' 操作，\n共有 {len(work_order_list)} 个工单需要处理，\n是否继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return

        try:
            if selected_index == 0:
                result = self.work_order_back_tool.huitoukan_to_handle(work_order_list)
            elif selected_index == 1:
                result = self.work_order_back_tool.huitoukan_remove_2(work_order_list)
            elif selected_index == 2:
                result = self.work_order_back_tool.huitoukan_qd_pass2(work_order_list)
            else:
                QMessageBox.warning(self, "警告", "无效的状态选择")
                return

            if result["status"] == "success":
                QMessageBox.information(self, "成功", f"工单状态更新成功！\n处理了 {len(work_order_list)} 个工单")
            else:
                QMessageBox.critical(self, "错误", f"工单状态更新失败：{result['message']}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理工单时发生异常：{str(e)}")

    def reset_work_orders(self):
        self.work_order_text.clear()
        self.status_combo.setCurrentIndex(0)

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass
