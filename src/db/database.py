import sqlite3
import os
from .db_init import init_database
from .models.folder import FolderManager
from .models.plugin import PluginManager
from .models.plugin_association import PluginAssociationManager
from .models.config import ConfigManager
from src.utils.path_utils import get_data_directory

class Database:
    """SQLite数据库管理类 - 只负责核心连接管理和初始化"""
    def __init__(self, db_name="x_tool.db"):
        # 数据库文件路径，存储在data目录下
        self.db_path = os.path.join(get_data_directory(), db_name)
        
        # 当前上下文中的连接
        self._connection = None
        
        # 确保data目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 初始化数据库
        self._init_db_without_context()
        
        # 初始化业务管理器
        self.folder_manager = FolderManager(self)
        self.plugin_manager = PluginManager(self)
        self.plugin_association_manager = PluginAssociationManager(self)
        self.config_manager = ConfigManager(self)
    
    def _init_db_without_context(self):
        """不使用上下文管理器初始化数据库（仅用于__init__）"""
        conn = sqlite3.connect(self.db_path)
        try:
            init_database(conn)
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def __enter__(self):
        """实现上下文管理器协议的__enter__方法"""
        self._connection = sqlite3.connect(self.db_path, timeout=10)  # 增加超时时间到10秒
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """实现上下文管理器协议的__exit__方法"""
        if self._connection:
            if exc_type is None:
                self._connection.commit()
            else:
                self._connection.rollback()
            self._connection.close()
            self._connection = None
    
    def get_connection(self):
        """获取数据库连接"""
        if self._connection:  # 如果在上下文中，返回已存在的连接
            return self._connection
        # 不在上下文中时，也应该保持连接一致性
        raise RuntimeError("Database connection should be used within a context manager")
