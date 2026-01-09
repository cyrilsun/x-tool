import sqlite3


def init_database(conn):
    """初始化数据库表结构"""
    cursor = conn.cursor()
    
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
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
