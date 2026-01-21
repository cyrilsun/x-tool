class ConfigManager:
    """应用配置管理类"""
    
    def __init__(self, database):
        """初始化配置管理器
        
        Args:
            database: Database实例，用于获取数据库连接
        """
        self.database = database
    
    def get_config(self, key, default=None):
        """获取配置值
        
        Args:
            key: 配置键名
            default: 默认值
            
        Returns:
            配置值
        """
        conn = self.database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT value FROM app_config WHERE key = ?",
            (key,)
        )
        
        result = cursor.fetchone()
        return result[0] if result else default
    
    def set_config(self, key, value):
        """设置配置值
        
        Args:
            key: 配置键名
            value: 配置值
        """
        conn = self.database.get_connection()
        cursor = conn.cursor()
        
        # 更新或插入配置
        cursor.execute(
            "INSERT OR REPLACE INTO app_config (key, value) VALUES (?, ?)",
            (key, value)
        )
    
    def get_home_page_sort_order(self):
        """获取首页排序位置
        
        Returns:
            首页排序位置（整数）
        """
        value = self.get_config("home_page_sort_order", "0")
        try:
            return int(value)
        except ValueError:
            return 0
    
    def set_home_page_sort_order(self, sort_order):
        """设置首页排序位置
        
        Args:
            sort_order: 排序位置（整数）
        """
        self.set_config("home_page_sort_order", str(sort_order))