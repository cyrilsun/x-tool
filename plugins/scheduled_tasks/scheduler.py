"""
定时任务调度器模块
使用 APScheduler 实现任务调度
"""

from datetime import datetime
from typing import Callable, Dict, Any, Optional

from src.utils.logger import logger

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.triggers.date import DateTrigger
    APScheduler_AVAILABLE = True
except ImportError:
    APScheduler_AVAILABLE = False
    logger.warning("APScheduler 未安装，定时任务功能将受限")


class TaskScheduler:
    """任务调度器管理类（单例模式）"""

    _instance = None
    _scheduler = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化调度器"""
        # 只初始化一次
        if self._scheduler is None:
            self._init_scheduler()

    def _init_scheduler(self):
        """初始化 APScheduler"""
        if not APScheduler_AVAILABLE:
            logger.warning("APScheduler 不可用，调度器未启动")
            return

        try:
            TaskScheduler._scheduler = BackgroundScheduler()
            TaskScheduler._scheduler.start()
            logger.info("任务调度器已启动（单例）")
        except Exception as e:
            logger.error(f"启动调度器失败: {str(e)}")
            TaskScheduler._scheduler = None

    @property
    def scheduler(self):
        """获取调度器实例"""
        return TaskScheduler._scheduler

    def shutdown(self):
        """关闭调度器"""
        if TaskScheduler._scheduler:
            try:
                TaskScheduler._scheduler.shutdown()
                TaskScheduler._scheduler = None
                logger.info("任务调度器已关闭")
            except Exception as e:
                logger.error(f"关闭调度器失败: {str(e)}")

    def add_task(self, task_id: int, task_func: Callable,
                 trigger_type: str, trigger_config: Dict[str, Any],
                 task_name: str) -> bool:
        """添加任务到调度器

        Args:
            task_id: 任务ID
            task_func: 任务执行函数
            trigger_type: 触发器类型 (once, interval, cron)
            trigger_config: 触发器配置
            task_name: 任务名称

        Returns:
            是否添加成功
        """
        if not self.scheduler:
            logger.warning("调度器不可用，无法添加任务")
            return False

        try:
            # 检查任务是否已存在
            existing_job = self.scheduler.get_job(str(task_id))
            if existing_job:
                logger.info(f"任务 '{task_name}' (ID: {task_id}) 已存在于调度器中，跳过重复添加")
                return True

            # 创建触发器
            trigger = self._create_trigger(trigger_type, trigger_config)
            if trigger is None:
                return False

            # 添加任务
            self.scheduler.add_job(
                task_func,
                trigger=trigger,
                id=str(task_id),
                name=task_name,
                replace_existing=True
            )

            logger.info(f"任务 '{task_name}' (ID: {task_id}) 已添加到调度器")
            return True

        except Exception as e:
            logger.error(f"添加任务到调度器失败: {str(e)}")
            return False

    def remove_task(self, task_id: int) -> bool:
        """从调度器移除任务

        Args:
            task_id: 任务ID

        Returns:
            是否移除成功
        """
        if not self.scheduler:
            return False

        try:
            self.scheduler.remove_job(str(task_id))
            logger.info(f"任务 {task_id} 已从调度器移除")
            return True
        except Exception as e:
            logger.warning(f"移除任务失败: {str(e)}")
            return False

    def get_next_run_time(self, task_id: int) -> Optional[datetime]:
        """获取任务下次运行时间

        Args:
            task_id: 任务ID

        Returns:
            下次运行时间，如果任务不存在返回 None
        """
        if not self.scheduler:
            return None

        try:
            job = self.scheduler.get_job(str(task_id))
            if job:
                return job.next_run_time
            return None
        except Exception as e:
            logger.error(f"获取下次运行时间失败: {str(e)}")
            return None

    def pause_task(self, task_id: int) -> bool:
        """暂停任务

        Args:
            task_id: 任务ID

        Returns:
            是否暂停成功
        """
        if not self.scheduler:
            return False

        try:
            self.scheduler.pause_job(str(task_id))
            logger.info(f"任务 {task_id} 已暂停")
            return True
        except Exception as e:
            logger.error(f"暂停任务失败: {str(e)}")
            return False

    def resume_task(self, task_id: int) -> bool:
        """恢复任务

        Args:
            task_id: 任务ID

        Returns:
            是否恢复成功
        """
        if not self.scheduler:
            return False

        try:
            self.scheduler.resume_job(str(task_id))
            logger.info(f"任务 {task_id} 已恢复")
            return True
        except Exception as e:
            logger.error(f"恢复任务失败: {str(e)}")
            return False

    def _create_trigger(self, trigger_type: str, trigger_config: Dict[str, Any]):
        """创建触发器

        Args:
            trigger_type: 触发器类型
            trigger_config: 触发器配置

        Returns:
            触发器对象，如果创建失败返回 None
        """
        try:
            if trigger_type == "once":
                run_date_str = trigger_config.get("run_date")
                if run_date_str:
                    # 支持多种日期格式
                    if isinstance(run_date_str, str):
                        run_date = datetime.fromisoformat(run_date_str.replace('Z', '+00:00'))
                    else:
                        run_date = run_date_str
                    return DateTrigger(run_date=run_date)

            elif trigger_type == "interval":
                seconds = trigger_config.get("seconds", 0)
                minutes = trigger_config.get("minutes", 0)
                hours = trigger_config.get("hours", 0)

                return IntervalTrigger(
                    seconds=seconds,
                    minutes=minutes,
                    hours=hours
                )

            elif trigger_type == "cron":
                hour = trigger_config.get("hour", "*")
                minute = trigger_config.get("minute", "*")
                day = trigger_config.get("day", "*")
                day_of_week = trigger_config.get("day_of_week", "*")

                # 转换参数格式
                cron_kwargs = {}
                if hour != "*":
                    cron_kwargs['hour'] = hour
                if minute != "*":
                    cron_kwargs['minute'] = minute
                if day != "*":
                    cron_kwargs['day'] = day
                if day_of_week != "*":
                    cron_kwargs['day_of_week'] = day_of_week

                return CronTrigger(**cron_kwargs)

            else:
                logger.error(f"不支持的触发器类型: {trigger_type}")
                return None

        except Exception as e:
            logger.error(f"创建触发器失败: {str(e)}")
            return None

    def is_available(self) -> bool:
        """检查调度器是否可用"""
        return self.scheduler is not None

    def get_job_count(self) -> int:
        """获取当前任务数量"""
        if not self.scheduler:
            return 0
        return len(self.scheduler.get_jobs())

    def get_all_jobs(self) -> list:
        """获取所有任务"""
        if not self.scheduler:
            return []
        return self.scheduler.get_jobs()
