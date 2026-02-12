"""
定时任务插件数据库管理模块
独立于基础框架，完全自包含的数据库管理
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.utils.path_utils import get_data_directory
from src.utils.logger import logger


class ScheduledTasksDatabase:
    """定时任务数据库管理类"""

    def __init__(self):
        """初始化数据库"""
        self.db_dir = os.path.join(get_data_directory(), "scheduled_tasks_plugin")
        os.makedirs(self.db_dir, exist_ok=True)

        self.db_path = os.path.join(self.db_dir, "scheduled_tasks.db")
        self._init_database()

        logger.info(f"定时任务数据库初始化完成: {self.db_path}")

    def _init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()

            # 创建定时任务表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT DEFAULT '',
                    task_type TEXT NOT NULL,
                    trigger_type TEXT NOT NULL,
                    trigger_config TEXT NOT NULL,
                    task_config TEXT NOT NULL,
                    is_enabled BOOLEAN DEFAULT 1,
                    next_run_time TIMESTAMP,
                    last_run_time TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 创建任务执行日志表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task_execution_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    output TEXT,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES scheduled_tasks(id) ON DELETE CASCADE
                )
            ''')

            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_name ON scheduled_tasks(name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_enabled ON scheduled_tasks(is_enabled)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_execution_logs_task_id ON task_execution_logs(task_id)')

            conn.commit()
            logger.info("定时任务数据库表结构初始化完成")

        except Exception as e:
            conn.rollback()
            logger.error(f"初始化数据库失败: {str(e)}")
            raise
        finally:
            conn.close()

    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path, timeout=10)

    # ==================== 任务管理 ====================

    def add_task(self, name: str, description: str, task_type: str,
                 trigger_type: str, trigger_config: Dict[str, Any],
                 task_config: Dict[str, Any]) -> int:
        """添加定时任务

        Args:
            name: 任务名称
            description: 任务描述
            task_type: 任务类型 (message, command, plugin)
            trigger_type: 触发器类型 (once, interval, cron)
            trigger_config: 触发器配置字典
            task_config: 任务配置字典

        Returns:
            新创建任务的ID
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO scheduled_tasks
                   (name, description, task_type, trigger_type, trigger_config, task_config)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (name, description, task_type, trigger_type,
                 json.dumps(trigger_config, ensure_ascii=False),
                 json.dumps(task_config, ensure_ascii=False))
            )
            conn.commit()
            task_id = cursor.lastrowid
            logger.info(f"添加任务: {name} (ID: {task_id})")
            return task_id
        except Exception as e:
            conn.rollback()
            logger.error(f"添加任务失败: {str(e)}")
            raise
        finally:
            conn.close()

    def get_task(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取任务

        Args:
            name: 任务名称

        Returns:
            任务信息字典，如果不存在返回 None
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, name, description, task_type, trigger_type, trigger_config,
                          task_config, is_enabled, next_run_time, last_run_time, created_at, updated_at
                   FROM scheduled_tasks WHERE name = ?""",
                (name,)
            )
            result = cursor.fetchone()

            if result:
                return {
                    "id": result[0],
                    "name": result[1],
                    "description": result[2],
                    "task_type": result[3],
                    "trigger_type": result[4],
                    "trigger_config": json.loads(result[5]) if result[5] else {},
                    "task_config": json.loads(result[6]) if result[6] else {},
                    "is_enabled": bool(result[7]),
                    "next_run_time": result[8],
                    "last_run_time": result[9],
                    "created_at": result[10],
                    "updated_at": result[11]
                }
            return None
        finally:
            conn.close()

    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取任务

        Args:
            task_id: 任务ID

        Returns:
            任务信息字典，如果不存在返回 None
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, name, description, task_type, trigger_type, trigger_config,
                          task_config, is_enabled, next_run_time, last_run_time, created_at, updated_at
                   FROM scheduled_tasks WHERE id = ?""",
                (task_id,)
            )
            result = cursor.fetchone()

            if result:
                return {
                    "id": result[0],
                    "name": result[1],
                    "description": result[2],
                    "task_type": result[3],
                    "trigger_type": result[4],
                    "trigger_config": json.loads(result[5]) if result[5] else {},
                    "task_config": json.loads(result[6]) if result[6] else {},
                    "is_enabled": bool(result[7]),
                    "next_run_time": result[8],
                    "last_run_time": result[9],
                    "created_at": result[10],
                    "updated_at": result[11]
                }
            return None
        finally:
            conn.close()

    def get_all_tasks(self, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """获取所有任务

        Args:
            enabled_only: 是否只获取启用的任务

        Returns:
            任务列表
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            if enabled_only:
                cursor.execute(
                    """SELECT id, name, description, task_type, trigger_type, trigger_config,
                              task_config, is_enabled, next_run_time, last_run_time, created_at, updated_at
                       FROM scheduled_tasks WHERE is_enabled = 1
                       ORDER BY created_at DESC"""
                )
            else:
                cursor.execute(
                    """SELECT id, name, description, task_type, trigger_type, trigger_config,
                              task_config, is_enabled, next_run_time, last_run_time, created_at, updated_at
                       FROM scheduled_tasks
                       ORDER BY created_at DESC"""
                )

            tasks = []
            for row in cursor.fetchall():
                tasks.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "task_type": row[3],
                    "trigger_type": row[4],
                    "trigger_config": json.loads(row[5]) if row[5] else {},
                    "task_config": json.loads(row[6]) if row[6] else {},
                    "is_enabled": bool(row[7]),
                    "next_run_time": row[8],
                    "last_run_time": row[9],
                    "created_at": row[10],
                    "updated_at": row[11]
                })

            return tasks
        finally:
            conn.close()

    def update_task(self, name: str, **kwargs) -> bool:
        """更新任务信息

        Args:
            name: 任务名称
            **kwargs: 要更新的字段

        Returns:
            是否更新成功
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            allowed_fields = ['description', 'task_type', 'trigger_type', 'trigger_config',
                             'task_config', 'is_enabled', 'next_run_time', 'last_run_time']

            updates = []
            values = []

            for field in allowed_fields:
                if field in kwargs:
                    if field in ['trigger_config', 'task_config']:
                        updates.append(f"{field} = ?")
                        values.append(json.dumps(kwargs[field], ensure_ascii=False))
                    else:
                        updates.append(f"{field} = ?")
                        values.append(kwargs[field])

            if updates:
                values.append(name)
                query = f"UPDATE scheduled_tasks SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE name = ?"
                cursor.execute(query, values)
                conn.commit()
                logger.info(f"更新任务: {name}")
                return True

            return False
        except Exception as e:
            conn.rollback()
            logger.error(f"更新任务失败: {str(e)}")
            raise
        finally:
            conn.close()

    def delete_task(self, name: str) -> bool:
        """删除任务

        Args:
            name: 任务名称

        Returns:
            是否删除成功
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scheduled_tasks WHERE name = ?", (name,))
            conn.commit()
            logger.info(f"删除任务: {name}")
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"删除任务失败: {str(e)}")
            raise
        finally:
            conn.close()

    def delete_task_by_id(self, task_id: int) -> bool:
        """根据ID删除任务

        Args:
            task_id: 任务ID

        Returns:
            是否删除成功
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scheduled_tasks WHERE id = ?", (task_id,))
            conn.commit()
            logger.info(f"删除任务 ID: {task_id}")
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"删除任务失败: {str(e)}")
            raise
        finally:
            conn.close()

    # ==================== 执行日志管理 ====================

    def add_execution_log(self, task_id: int, status: str, start_time: str,
                          end_time: Optional[str] = None, output: Optional[str] = None,
                          error_message: Optional[str] = None) -> int:
        """添加任务执行日志

        Args:
            task_id: 任务ID
            status: 执行状态 (success, failed, running)
            start_time: 开始时间
            end_time: 结束时间
            output: 执行输出
            error_message: 错误信息

        Returns:
            日志ID
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO task_execution_logs
                   (task_id, status, start_time, end_time, output, error_message)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (task_id, status, start_time, end_time, output, error_message)
            )
            conn.commit()
            log_id = cursor.lastrowid
            return log_id
        except Exception as e:
            conn.rollback()
            logger.error(f"添加执行日志失败: {str(e)}")
            raise
        finally:
            conn.close()

    def get_execution_logs(self, task_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """获取任务执行日志

        Args:
            task_id: 任务ID
            limit: 返回记录数量限制

        Returns:
            执行日志列表
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, task_id, status, start_time, end_time, output, error_message, created_at
                   FROM task_execution_logs
                   WHERE task_id = ?
                   ORDER BY created_at DESC
                   LIMIT ?""",
                (task_id, limit)
            )

            logs = []
            for row in cursor.fetchall():
                # 转换字符串为 datetime 对象
                start_time = None
                end_time = None
                if row[3]:
                    try:
                        start_time = datetime.fromisoformat(row[3])
                    except:
                        start_time = row[3]
                if row[4]:
                    try:
                        end_time = datetime.fromisoformat(row[4])
                    except:
                        end_time = row[4]

                logs.append({
                    "id": row[0],
                    "task_id": row[1],
                    "status": row[2],
                    "start_time": start_time,
                    "end_time": end_time,
                    "output": row[5],
                    "error_message": row[6],
                    "created_at": row[7]
                })

            return logs
        finally:
            conn.close()

    def get_all_execution_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取所有执行日志

        Args:
            limit: 返回记录数量限制

        Returns:
            执行日志列表
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, task_id, status, start_time, end_time, output, error_message, created_at
                   FROM task_execution_logs
                   ORDER BY created_at DESC
                   LIMIT ?""",
                (limit,)
            )

            logs = []
            for row in cursor.fetchall():
                # 转换字符串为 datetime 对象
                start_time = None
                end_time = None
                if row[3]:
                    try:
                        start_time = datetime.fromisoformat(row[3])
                    except:
                        start_time = row[3]
                if row[4]:
                    try:
                        end_time = datetime.fromisoformat(row[4])
                    except:
                        end_time = row[4]

                logs.append({
                    "id": row[0],
                    "task_id": row[1],
                    "status": row[2],
                    "start_time": start_time,
                    "end_time": end_time,
                    "output": row[5],
                    "error_message": row[6],
                    "created_at": row[7]
                })

            return logs
        finally:
            conn.close()

    def clear_execution_logs(self, task_id: Optional[int] = None) -> bool:
        """清除执行日志

        Args:
            task_id: 任务ID，如果为None则清除所有日志

        Returns:
            是否清除成功
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            if task_id:
                cursor.execute("DELETE FROM task_execution_logs WHERE task_id = ?", (task_id,))
                logger.info(f"清除任务 {task_id} 的执行日志")
            else:
                cursor.execute("DELETE FROM task_execution_logs")
                logger.info("清除所有执行日志")

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"清除执行日志失败: {str(e)}")
            raise
        finally:
            conn.close()

    def delete_log_by_id(self, log_id: int) -> bool:
        """根据ID删除单条执行日志

        Args:
            log_id: 日志ID

        Returns:
            是否删除成功
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM task_execution_logs WHERE id = ?", (log_id,))
            conn.commit()
            logger.info(f"删除日志 ID: {log_id}")
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"删除日志失败: {str(e)}")
            raise
        finally:
            conn.close()


# 全局单例
_db_instance = None


def get_database() -> ScheduledTasksDatabase:
    """获取数据库单例实例"""
    global _db_instance
    if _db_instance is None:
        _db_instance = ScheduledTasksDatabase()
    return _db_instance
