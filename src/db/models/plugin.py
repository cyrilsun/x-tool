class PluginManager:
    """插件实体管理类"""
    
    def __init__(self, database):
        """初始化插件管理器
        
        Args:
            database: Database实例，用于获取数据库连接
        """
        self.database = database
    
    def add_plugin(self, name, file_name, description=""):
        """添加插件元数据"""
        conn = self.database.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO plugins (name, file_name, description, updated_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
            (name, file_name, description)
        )
    
    def get_plugin(self, name):
        """获取插件元数据"""
        conn = self.database.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, file_name, description, created_at, updated_at FROM plugins WHERE name = ?",
            (name,)
        )
        return cursor.fetchone()
    
    def update_plugin(self, name, file_name=None, description=None):
        """更新插件元数据"""
        conn = self.database.get_connection()
        cursor = conn.cursor()
        
        if file_name and description:
            cursor.execute(
                "UPDATE plugins SET file_name = ?, description = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?",
                (file_name, description, name)
            )
        elif file_name:
            cursor.execute(
                "UPDATE plugins SET file_name = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?",
                (file_name, name)
            )
        elif description:
            cursor.execute(
                "UPDATE plugins SET description = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?",
                (description, name)
            )
    
    def delete_plugin(self, name):
        """删除插件元数据"""
        conn = self.database.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM plugins WHERE name = ?", (name,))
    
    def get_all_plugins(self):
        """获取所有插件"""
        conn = self.database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, file_name, description, created_at, updated_at FROM plugins ORDER BY name")
        return cursor.fetchall()