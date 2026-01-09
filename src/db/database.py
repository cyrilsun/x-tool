import sqlite3
import os
from .models.folder import FolderManager
from .models.plugin_association import PluginAssociationManager

class Database:
    """SQLite数据库管理类 - 只负责核心连接管理和初始化"""
    def __init__(self, db_name="x_tool.db"):
        # 数据库文件路径，存储在data目录下
        self.db_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", db_name)
        
        # 当前上下文中的连接
        self._connection = None
        
        # 确保data目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 初始化数据库
        self._init_db_without_context()
        
        # 初始化业务管理器
        self.folder_manager = FolderManager(self)
        self.plugin_association_manager = PluginAssociationManager(self)
    
    def _init_db_without_context(self):
        """不使用上下文管理器初始化数据库（仅用于__init__）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 执行初始化SQL
        try:
            # 创建工具配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tool_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_name TEXT NOT NULL,
                    config_key TEXT NOT NULL,
                    config_value TEXT,
                    UNIQUE(tool_name, config_key)
                )
            ''')
            
            # 创建插件文件夹表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plugin_folders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    parent_id INTEGER,
                    sort_order INTEGER DEFAULT 0,
                    UNIQUE(name, COALESCE(parent_id, -1))
                )
            ''')
            
            # 添加sort_order列（如果不存在）
            try:
                cursor.execute("ALTER TABLE plugin_folders ADD COLUMN sort_order INTEGER DEFAULT 0")
            except sqlite3.OperationalError as e:
                # 如果列已存在，忽略错误
                if "duplicate column name" not in str(e):
                    raise
            
            # 创建插件与文件夹关联表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plugin_folder_associations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_name TEXT NOT NULL,
                    folder_id INTEGER,
                    sort_order INTEGER DEFAULT 0,
                    UNIQUE(plugin_name)
                )
            ''')
            
            # 添加sort_order列（如果不存在）
            try:
                cursor.execute("ALTER TABLE plugin_folder_associations ADD COLUMN sort_order INTEGER DEFAULT 0")
            except sqlite3.OperationalError as e:
                # 如果列已存在，忽略错误
                if "duplicate column name" not in str(e):
                    raise
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def __enter__(self):
        """实现上下文管理器协议的__enter__方法"""
        self._connection = sqlite3.connect(self.db_path)
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
