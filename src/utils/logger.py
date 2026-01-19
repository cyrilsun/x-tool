#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""日志配置模块"""
import logging
import os
import sys
import glob
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
from src.utils.path_utils import get_log_directory

# 定义日志目录
LOG_DIR = get_log_directory()

# 确保日志目录存在
if not os.path.exists(LOG_DIR):
    try:
        os.makedirs(LOG_DIR)
    except Exception as e:
        print(f"创建日志目录失败: {e}")
        LOG_DIR = os.getcwd()  # 回退到当前目录

# 定义日志文件基本名称（不包含日期）
LOG_FILE_BASE = os.path.join(LOG_DIR, "x-tool")
LOG_FILE = os.path.join(LOG_DIR, f"x-tool_{datetime.now().strftime('%Y-%m-%d')}.log")

# 创建logger对象
logger = logging.getLogger('x-tool')
logger.setLevel(logging.INFO)  # 设置最低日志级别

# 创建格式化器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s')

# 创建控制台处理器，将日志输出到控制台
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)  # 控制台日志级别为INFO及以上
console_handler.setFormatter(formatter)

# 创建TimedRotatingFileHandler，实现每日日志轮转
# when='midnight' 表示每天午夜轮转
# interval=1 表示每1个时间单位轮转一次
# backupCount=7 表示保留最近7个日志文件
file_handler = TimedRotatingFileHandler(
    filename=LOG_FILE,
    when='midnight',
    interval=1,
    backupCount=0,  # 不使用内置的备份功能，我们将自定义清理
    encoding='utf-8',
    delay=True
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# 自定义日志文件名后缀格式
file_handler.suffix = "%Y-%m-%d.log"

# 清除现有的处理器，避免重复日志
logger.handlers.clear()

# 将处理器添加到logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def clean_old_logs(days_to_keep=7):
    """清理旧日志文件，只保留最近指定天数的日志
    
    Args:
        days_to_keep: 要保留的日志天数，默认为7天
    """
    try:
        # 计算截止日期
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # 获取所有日志文件
        log_files = glob.glob(os.path.join(LOG_DIR, "x-tool_*.log"))
        
        for log_file in log_files:
            try:
                # 从文件名中提取日期
                file_name = os.path.basename(log_file)
                date_str = file_name.replace("x-tool_", "").replace(".log", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                # 如果文件日期早于截止日期，则删除
                if file_date < cutoff_date:
                    os.remove(log_file)
                    logger.info(f"已删除旧日志文件: {log_file}")
            except Exception as e:
                logger.error(f"处理日志文件 {log_file} 时出错: {e}")
    except Exception as e:
        logger.error(f"清理旧日志文件失败: {e}")


# 清理旧日志
clean_old_logs()

# 导出logger
export = logger

