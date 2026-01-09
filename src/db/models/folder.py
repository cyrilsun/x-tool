class FolderManager:
    """插件文件夹管理类"""
    
    def __init__(self, database):
        """初始化文件夹管理器
        
        Args:
            database: Database实例，用于获取数据库连接
        """
        self.database = database
    
    def add_folder(self, name, parent_id=None):
        """添加文件夹"""
        conn = self.database.get_connection()
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
        
        return cursor.lastrowid
    
    def delete_folder(self, folder_id):
        """删除文件夹"""
        conn = self.database.get_connection()
        cursor = conn.cursor()
        
        # 先删除该文件夹下的所有子文件夹
        cursor.execute("DELETE FROM plugin_folders WHERE parent_id = ?", (folder_id,))
        
        # 再删除该文件夹下的所有插件关联
        cursor.execute("UPDATE plugin_folder_associations SET folder_id = NULL WHERE folder_id = ?", (folder_id,))
        
        # 最后删除文件夹本身
        cursor.execute("DELETE FROM plugin_folders WHERE id = ?", (folder_id,))
    
    def update_folder_name(self, folder_id, new_name):
        """更新文件夹名称"""
        conn = self.database.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE plugin_folders SET name = ? WHERE id = ?",
            (new_name, folder_id)
        )
    
    def get_all_folders(self):
        """获取所有文件夹，按parent_id和sort_order排序"""
        conn = self.database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, parent_id, sort_order FROM plugin_folders ORDER BY parent_id, sort_order")
        return cursor.fetchall()
    
    def get_folder_plugins(self, folder_id):
        """获取文件夹下的所有插件及其排序顺序"""
        conn = self.database.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT plugin_name, sort_order FROM plugin_folder_associations WHERE folder_id = ? ORDER BY sort_order",
            (folder_id,)
        )
        return [(row[0], row[1]) for row in cursor.fetchall()]
    
    def update_folder_sort_order(self, folder_id, sort_order):
        """更新文件夹排序顺序"""
        conn = self.database.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE plugin_folders SET sort_order = ? WHERE id = ?",
            (sort_order, folder_id)
        )
