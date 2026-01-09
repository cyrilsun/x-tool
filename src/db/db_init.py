def init_database(conn):
    """初始化数据库表结构"""
    cursor = conn.cursor()
    
    try:
        # 创建插件元数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plugins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                file_name TEXT NOT NULL,
                description TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建插件文件夹表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plugin_folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                parent_id INTEGER,
                sort_order INTEGER DEFAULT 0,
                UNIQUE(name, COALESCE(parent_id, -1)),
                FOREIGN KEY (parent_id) REFERENCES plugin_folders(id) ON DELETE CASCADE
            )
        ''')
        
        # 创建插件与文件夹关联表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plugin_folder_associations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plugin_name TEXT NOT NULL,
                folder_id INTEGER,
                sort_order INTEGER DEFAULT 0,
                UNIQUE(plugin_name),
                FOREIGN KEY (plugin_name) REFERENCES plugins(name) ON DELETE CASCADE,
                FOREIGN KEY (folder_id) REFERENCES plugin_folders(id) ON DELETE SET NULL
            )
        ''')
        
        # 创建索引以提高查询性能
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plugins_name ON plugins(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plugin_folders_parent_id ON plugin_folders(parent_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plugin_folder_associations_folder_id ON plugin_folder_associations(folder_id)')
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
