import sqlite3
import os

class Database:
    """SQLite数据库管理类"""
    def __init__(self, db_name="x_tool.db"):
        # 数据库文件路径
        self.db_path = os.path.join(os.path.dirname(__file__), "..", "..", db_name)
        
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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
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
        
        conn.commit()
        conn.close()
    
    # 笔记相关操作
    def get_notes(self):
        """获取所有笔记"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, updated_at FROM notes ORDER BY updated_at DESC")
        notes = cursor.fetchall()
        conn.close()
        return notes
    
    def get_note(self, note_id):
        """获取单个笔记"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        note = cursor.fetchone()
        conn.close()
        return note
    
    def add_note(self, title, content):
        """添加笔记"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notes (title, content) VALUES (?, ?)",
            (title, content)
        )
        note_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return note_id
    
    def update_note(self, note_id, content):
        """更新笔记"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE notes SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (content, note_id)
        )
        conn.commit()
        conn.close()
    
    def delete_note(self, note_id):
        """删除笔记"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
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
