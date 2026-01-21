class PluginManager:
    """插件管理类"""
    
    def __init__(self, database):
        """初始化插件管理器
        
        Args:
            database: Database实例，用于获取数据库连接
        """
        self.database = database
    
    def add_plugin(self, name, file_name, description=""):
        """添加插件
        
        Args:
            name: 插件名称
            file_name: 插件文件名
            description: 插件描述
        """
        conn = self.database.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO plugins (name, file_name, description) VALUES (?, ?, ?)",
            (name, file_name, description)
        )
    
    def get_plugin(self, name):
        """获取插件信息
        
        Args:
            name: 插件名称
            
        Returns:
            插件信息字典
        """
        conn = self.database.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, file_name, description, created_at, updated_at FROM plugins WHERE name = ?",
            (name,)
        )
        result = cursor.fetchone()
        
        if result:
            return {
                "id": result[0],
                "name": result[1],
                "file_name": result[2],
                "description": result[3],
                "created_at": result[4],
                "updated_at": result[5]
            }
        return None
    
    def delete_plugin(self, name):
        """删除插件
        
        Args:
            name: 插件名称
        """
        conn = self.database.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM plugins WHERE name = ?", (name,))
    
    def update_plugin_info(self, name, description=None):
        """更新插件信息
        
        Args:
            name: 插件名称
            description: 插件描述
        """
        conn = self.database.get_connection()
        cursor = conn.cursor()
        
        if description is not None:
            cursor.execute(
                "UPDATE plugins SET description = ? WHERE name = ?",
                (description, name)
            )
    
    def get_all_plugins(self):
        """获取所有插件
        
        Returns:
            插件列表
        """
        conn = self.database.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, file_name, description, created_at, updated_at FROM plugins"
        )
        
        plugins = []
        for row in cursor.fetchall():
            plugins.append({
                "id": row[0],
                "name": row[1],
                "file_name": row[2],
                "description": row[3],
                "created_at": row[4],
                "updated_at": row[5]
            })
        
        return plugins
    
    def get_plugin_file_name(self, name):
        """获取插件文件名
        
        Args:
            name: 插件名称
            
        Returns:
            插件文件名
        """
        conn = self.database.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT file_name FROM plugins WHERE name = ?",
            (name,)
        )
        result = cursor.fetchone()
        return result[0] if result else None
    
    def get_plugins_by_file_name(self, file_name):
        """根据插件文件名获取所有匹配的插件名称列表
        
        Args:
            file_name: 插件文件名（不包含扩展名）
        
        Returns:
            插件名称列表
        """
        conn = self.database.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM plugins WHERE file_name = ?",
            (file_name,)
        )
        return [row[0] for row in cursor.fetchall()]
