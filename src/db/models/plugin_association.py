class PluginAssociationManager:
    """插件与文件夹关联管理类"""
    
    def __init__(self, database):
        """初始化插件关联管理器
        
        Args:
            database: Database实例，用于获取数据库连接
        """
        self.database = database
    
    def associate_plugin_with_folder(self, plugin_name, folder_id):
        """关联插件与文件夹，并设置排序顺序"""
        conn = self.database.get_connection()
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
    
    def get_plugin_folder(self, plugin_name):
        """获取插件所在的文件夹和排序顺序"""
        conn = self.database.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT folder_id, sort_order FROM plugin_folder_associations WHERE plugin_name = ?",
            (plugin_name,)
        )
        result = cursor.fetchone()
        
        if result:
            return result[0], result[1]  # 返回folder_id和sort_order
        return None, 0  # 默认返回None和0
    
    def remove_plugin_from_folder(self, plugin_name):
        """移除插件与文件夹的关联"""
        conn = self.database.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM plugin_folder_associations WHERE plugin_name = ?", (plugin_name,))
    
    def update_plugin_sort_order(self, plugin_name, sort_order):
        """更新插件排序顺序"""
        conn = self.database.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE plugin_folder_associations SET sort_order = ? WHERE plugin_name = ?",
            (sort_order, plugin_name)
        )
    
    def get_folder_plugins(self, folder_id):
        """获取文件夹下的所有插件及其排序顺序"""
        conn = self.database.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT plugin_name, sort_order FROM plugin_folder_associations WHERE folder_id = ? ORDER BY sort_order",
            (folder_id,)
        )
        return [(row[0], row[1]) for row in cursor.fetchall()]
