import sqlite3
import os

class Database:
    """SQLite数据库管理类"""
    def __init__(self, db_name="x_tool.db"):
        # 数据库文件路径，存储在data目录下
        self.db_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", db_name)
        
        # 当前上下文中的连接
        self._connection = None
        
        # 初始化数据库
        self.init_db()
    
    def __enter__(self):
        """实现上下文管理器协议的__enter__方法"""
        self._connection = sqlite3.connect(self.db_path)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """实现上下文管理器协议的__exit__方法"""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def get_connection(self):
        """获取数据库连接"""
        if self._connection:  # 如果在上下文中，返回已存在的连接
            return self._connection
        return sqlite3.connect(self.db_path)  # 否则创建新连接
    
    def init_db(self):
        """初始化数据库，创建表格"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
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
            conn.commit()
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
            conn.commit()
        except sqlite3.OperationalError as e:
            # 如果列已存在，忽略错误
            if "duplicate column name" not in str(e):
                raise
        
        conn.commit()
        conn.close()
    
    # 工具配置相关操作
    def get_tool_config(self, tool_name, config_key):
        """获取工具配置"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT config_value FROM tool_configs WHERE tool_name = ? AND config_key = ?",
            (tool_name, config_key)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def set_tool_config(self, tool_name, config_key, config_value):
        """设置工具配置"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO tool_configs (tool_name, config_key, config_value) VALUES (?, ?, ?)",
            (tool_name, config_key, config_value)
        )
        conn.commit()
        conn.close()
    
    # 插件文件夹相关操作
    def add_folder(self, name, parent_id=None):
        """添加文件夹"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 获取当前父文件夹下的最大排序值
        cursor.execute(
            "SELECT MAX(sort_order) FROM plugin_folders WHERE parent_id = ?",
            (parent_id,)
        )
        result = cursor.fetchone()
        next_sort_order = result[0] + 1 if result[0] is not None else 0
        
        # 插入新文件夹
        cursor.execute(
            "INSERT INTO plugin_folders (name, parent_id, sort_order) VALUES (?, ?, ?)",
            (name, parent_id, next_sort_order)
        )
        
        folder_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return folder_id
    
    def delete_folder(self, folder_id):
        """删除文件夹"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 先删除该文件夹下的所有子文件夹
        cursor.execute("DELETE FROM plugin_folders WHERE parent_id = ?", (folder_id,))
        
        # 再删除该文件夹下的所有插件关联
        cursor.execute("UPDATE plugin_folder_associations SET folder_id = NULL WHERE folder_id = ?", (folder_id,))
        
        # 最后删除文件夹本身
        cursor.execute("DELETE FROM plugin_folders WHERE id = ?", (folder_id,))
        
        conn.commit()
        conn.close()
    
    def update_folder_name(self, folder_id, new_name):
        """更新文件夹名称"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE plugin_folders SET name = ? WHERE id = ?",
            (new_name, folder_id)
        )
        conn.commit()
        conn.close()
    
    def get_all_folders(self):
        """获取所有文件夹，按parent_id和sort_order排序"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, parent_id, sort_order FROM plugin_folders ORDER BY parent_id, sort_order")
        folders = cursor.fetchall()
        conn.close()
        return folders
    
    def get_folder_plugins(self, folder_id):
        """获取文件夹下的所有插件及其排序顺序"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT plugin_name, sort_order FROM plugin_folder_associations WHERE folder_id = ? ORDER BY sort_order",
            (folder_id,)
        )
        plugins = [(row[0], row[1]) for row in cursor.fetchall()]
        
        # 如果不在上下文中，关闭连接
        if not self._connection:
            conn.close()
            
        return plugins
    
    def associate_plugin_with_folder(self, plugin_name, folder_id):
        """关联插件与文件夹，并设置排序顺序"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 获取当前文件夹下的最大排序值
        cursor.execute(
            "SELECT MAX(sort_order) FROM plugin_folder_associations WHERE folder_id = ?",
            (folder_id,)
        )
        result = cursor.fetchone()
        next_sort_order = result[0] + 1 if result[0] is not None else 0
        
        # 插入或更新关联记录
        cursor.execute(
            "INSERT OR REPLACE INTO plugin_folder_associations (plugin_name, folder_id, sort_order) VALUES (?, ?, ?)",
            (plugin_name, folder_id, next_sort_order)
        )
        conn.commit()
        
        # 如果不在上下文中，关闭连接
        if not self._connection:
            conn.close()
    
    def get_plugin_folder(self, plugin_name):
        """获取插件所在的文件夹和排序顺序"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT folder_id, sort_order FROM plugin_folder_associations WHERE plugin_name = ?",
            (plugin_name,)
        )
        result = cursor.fetchone()
        
        # 如果不在上下文中，关闭连接
        if not self._connection:
            conn.close()
            
        if result:
            return result[0], result[1]  # 返回folder_id和sort_order
        return None, 0  # 默认返回None和0
    
    def remove_plugin_from_folder(self, plugin_name):
        """移除插件与文件夹的关联"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM plugin_folder_associations WHERE plugin_name = ?", (plugin_name,))
        conn.commit()
        
        # 如果不在上下文中，关闭连接
        if not self._connection:
            conn.close()
    
    def update_folder_sort_order(self, folder_id, sort_order):
        """更新文件夹排序顺序"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE plugin_folders SET sort_order = ? WHERE id = ?",
            (sort_order, folder_id)
        )
        conn.commit()
        conn.close()
    
    def update_plugin_sort_order(self, plugin_name, sort_order):
        """更新插件排序顺序"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE plugin_folder_associations SET sort_order = ? WHERE plugin_name = ?",
            (sort_order, plugin_name)
        )
        conn.commit()
        
        # 如果不在上下文中，关闭连接
        if not self._connection:
            conn.close()
