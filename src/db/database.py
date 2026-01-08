import sqlite3
import os

class Database:
    """SQLite数据库管理类"""
    def __init__(self, db_name="x_tool.db"):
        # 数据库文件路径，存储在data目录下
        self.db_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", db_name)
        
        # 初始化数据库
        self.init_db()
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """初始化数据库，创建表格"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 创建笔记表
        # cursor.execute('''
        #     CREATE TABLE IF NOT EXISTS notes (
        #         id INTEGER PRIMARY KEY AUTOINCREMENT,
        #         title TEXT NOT NULL,
        #         content TEXT,
        #         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        #         updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        #     )
        # ''')
        
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
                UNIQUE(name, COALESCE(parent_id, -1))
            )
        ''')
        
        # 创建插件与文件夹关联表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plugin_folder_associations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plugin_name TEXT NOT NULL,
                folder_id INTEGER,
                UNIQUE(plugin_name)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # 笔记相关操作
    # def get_notes(self):
    #     """获取所有笔记"""
    #     conn = self.get_connection()
    #     cursor = conn.cursor()
    #     cursor.execute("SELECT id, title, updated_at FROM notes ORDER BY updated_at DESC")
    #     notes = cursor.fetchall()
    #     conn.close()
    #     return notes
    #
    # def get_note(self, note_id):
    #     """获取单个笔记"""
    #     conn = self.get_connection()
    #     cursor = conn.cursor()
    #     cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    #     note = cursor.fetchone()
    #     conn.close()
    #     return note
    #
    # def add_note(self, title, content):
    #     """添加笔记"""
    #     conn = self.get_connection()
    #     cursor = conn.cursor()
    #     cursor.execute(
    #         "INSERT INTO notes (title, content) VALUES (?, ?)",
    #         (title, content)
    #     )
    #     note_id = cursor.lastrowid
    #     conn.commit()
    #     conn.close()
    #     return note_id
    #
    # def update_note(self, note_id, content):
    #     """更新笔记"""
    #     conn = self.get_connection()
    #     cursor = conn.cursor()
    #     cursor.execute(
    #         "UPDATE notes SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
    #         (content, note_id)
    #     )
    #     conn.commit()
    #     conn.close()
    #
    # def delete_note(self, note_id):
    #     """删除笔记"""
    #     conn = self.get_connection()
    #     cursor = conn.cursor()
    #     cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    #     conn.commit()
    #     conn.close()
    
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
        cursor.execute(
            "INSERT INTO plugin_folders (name, parent_id) VALUES (?, ?)",
            (name, parent_id)
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
        """获取所有文件夹"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, parent_id FROM plugin_folders")
        folders = cursor.fetchall()
        conn.close()
        return folders
    
    def get_folder_plugins(self, folder_id):
        """获取文件夹下的所有插件"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT plugin_name FROM plugin_folder_associations WHERE folder_id = ?",
            (folder_id,)
        )
        plugins = [row[0] for row in cursor.fetchall()]
        conn.close()
        return plugins
    
    def associate_plugin_with_folder(self, plugin_name, folder_id):
        """关联插件与文件夹"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO plugin_folder_associations (plugin_name, folder_id) VALUES (?, ?)",
            (plugin_name, folder_id)
        )
        conn.commit()
        conn.close()
    
    def get_plugin_folder(self, plugin_name):
        """获取插件所在的文件夹"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT folder_id FROM plugin_folder_associations WHERE plugin_name = ?",
            (plugin_name,)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def remove_plugin_from_folder(self, plugin_name):
        """移除插件与文件夹的关联"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE plugin_folder_associations SET folder_id = NULL WHERE plugin_name = ?", (plugin_name,))
        conn.commit()
        conn.close()
