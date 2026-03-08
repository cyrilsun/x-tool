from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QGridLayout,
                             QFrame, QSizePolicy, QScrollArea)

from src.db.database import Database
from src.utils.logger import logger


class PluginCard(QFrame):
    """插件卡片组件"""
    clicked = pyqtSignal(str)  # 发送插件名称
    
    def __init__(self, plugin_name, description, icon_text="🔧", is_hot=False, parent=None):
        super().__init__(parent)
        self.plugin_name = plugin_name
        self.setMinimumSize(260, 110)
        self.setMaximumSize(320, 130)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 设置样式
        self.setStyleSheet("""
            PluginCard {
                background-color: #ffffff;
                border: 1px solid #e8e8e8;
                border-radius: 12px;
            }
            PluginCard:hover {
                border: 1px solid #3498db;
                background-color: #f8f9fa;
            }
            QLabel#pluginIcon {
                font-size: 32px;
            }
            QLabel#pluginName {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
            }
            QLabel#pluginDesc {
                font-size: 13px;
                color: #7f8c8d;
            }
            QLabel#hotTag {
                background-color: #ff6b6b;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 2px 8px;
                border-radius: 10px;
            }
        """)
        
        # 主布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # 左侧图标
        icon_label = QLabel(icon_text)
        icon_label.setObjectName("pluginIcon")
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # 右侧内容
        content_layout = QVBoxLayout()
        content_layout.setSpacing(6)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # 标题行（名称 + HOT标签）
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        
        name_label = QLabel(plugin_name)
        name_label.setObjectName("pluginName")
        title_layout.addWidget(name_label)
        
        if is_hot:
            hot_label = QLabel("HOT")
            hot_label.setObjectName("hotTag")
            hot_label.setFixedHeight(20)
            title_layout.addWidget(hot_label)
        
        title_layout.addStretch()
        content_layout.addLayout(title_layout)
        
        # 描述
        desc_label = QLabel(description or "暂无描述")
        desc_label.setObjectName("pluginDesc")
        desc_label.setWordWrap(True)
        desc_label.setMaximumHeight(40)
        content_layout.addWidget(desc_label)
        
        layout.addLayout(content_layout, 1)
        
    def mousePressEvent(self, event):
        """点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.plugin_name)
        super().mousePressEvent(event)


class HomePage(QWidget):
    """首页组件"""
    plugin_selected = pyqtSignal(str)  # 发送选中的插件名称
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plugins = []  # 存储所有插件数据
        self.current_category = "全部"
        self._resize_timer = None  # 防抖定时器
        self.setup_ui()
        self.load_plugins()
        
    def setup_ui(self):
        """初始化UI"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)
        
        # 设置背景色
        self.setStyleSheet("background-color: #f5f7fa;")
        
        # ========== 标题区域 ==========
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.setSpacing(10)
        
        # 主标题
        # title_label = QLabel("🔧 X-Tool 工具箱")
        title_label = QLabel("X-Tool 工具箱")
        title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title_label)
        
        # 副标题
        # subtitle_label = QLabel("一站式桌面工具集合，让工作更高效")
        # subtitle_label.setStyleSheet("""
        #     font-size: 16px;
        #     color: #7f8c8d;
        # """)
        # subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # title_layout.addWidget(subtitle_label)
        #
        main_layout.addWidget(title_container)
        
        # ========== 搜索区域 ==========
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        search_layout.setSpacing(0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索工具，如：Excel对比...")
        self.search_input.setMinimumWidth(300)
        self.search_input.setMaximumWidth(500)
        self.search_input.setFixedHeight(44)
        self.search_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dcdde1;
                border-right: none;
                border-top-left-radius: 22px;
                border-bottom-left-radius: 22px;
                padding: 0 20px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("搜索")
        search_btn.setFixedWidth(80)
        search_btn.setFixedHeight(44)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-top-right-radius: 22px;
                border-bottom-right-radius: 22px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        search_btn.clicked.connect(self.on_search_clicked)
        search_layout.addWidget(search_btn)
        
        main_layout.addWidget(search_container)
        
        # ========== 分类标签区域 ==========
        self.category_container = QWidget()
        self.category_layout = QHBoxLayout(self.category_container)
        self.category_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.category_layout.setSpacing(12)
        
        # 分类按钮样式
        self.category_btn_style = """
            QPushButton {
                background-color: #f1f2f6;
                color: #636e72;
                border: none;
                border-radius: 20px;
                padding: 8px 24px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
            QPushButton:checked {
                background-color: #3498db;
                color: white;
            }
        """
        
        self.category_buttons = {}
        # 初始只创建"全部"按钮，其他分类从左侧文件夹动态获取
        self._create_category_button("全部")
        
        # 默认选中"全部"
        self.category_buttons["全部"].setChecked(True)
        
        main_layout.addWidget(self.category_container)
        
        # ========== 插件卡片网格区域（带滚动条） ==========
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f2f6;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a1a1a1;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(16)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        self.scroll_area.setWidget(self.cards_container)
        main_layout.addWidget(self.scroll_area, 1)
        
    def load_plugins(self):
        """加载插件 - 与左侧列表保持一致，从主窗口的 plugin_widget_map 获取"""
        try:
            main_window = self._get_main_window()
            logger.info(f"[load_plugins] _get_main_window 返回: {main_window}")
            if main_window and hasattr(main_window, 'plugin_widget_map'):
                # 从主窗口获取已加载的插件映射，与左侧列表保持一致
                plugin_map = main_window.plugin_widget_map
                logger.info(f"[load_plugins] plugin_widget_map: {plugin_map}")
                
                # 清空现有插件列表
                self.plugins = []
                
                # 遍历插件映射，构建插件数据
                for plugin_name, widget in plugin_map.items():
                    # 尝试从插件实例获取描述信息
                    description = ""
                    if hasattr(widget, 'description'):
                        description = widget.description
                    elif hasattr(widget, 'get_description'):
                        description = widget.get_description()
                    
                    self.plugins.append({
                        "id": 0,
                        "name": plugin_name,
                        "file_name": "",
                        "description": description,
                        "created_at": "",
                        "updated_at": ""
                    })
                
                self.refresh_cards()
                logger.info(f"[load_plugins] 首页从主窗口加载了 {len(self.plugins)} 个插件")
            else:
                # 如果无法获取主窗口，尝试从数据库加载
                logger.info(f"[load_plugins] 无法获取主窗口，从数据库加载")
                self._load_plugins_from_database()
        except Exception as e:
            logger.error(f"[load_plugins] 加载插件失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
    def _load_plugins_from_database(self):
        """从数据库加载插件（备用方案）"""
        try:
            with Database() as db:
                self.plugins = db.plugin_manager.get_all_plugins()
                self.refresh_cards()
                logger.info(f"首页从数据库加载了 {len(self.plugins)} 个插件")
        except Exception as e:
            logger.error(f"从数据库加载插件失败: {e}")
            
    def _get_main_window(self):
        """获取主窗口实例"""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'plugin_widget_map'):
                return parent
            parent = parent.parent()
        return None
        
    def _create_category_button(self, category_name):
        """创建分类按钮"""
        btn = QPushButton(category_name)
        btn.setCheckable(True)
        btn.setStyleSheet(self.category_btn_style)
        btn.clicked.connect(lambda checked, c=category_name: self.on_category_changed(c))
        self.category_layout.addWidget(btn)
        self.category_buttons[category_name] = btn
        
    def load_categories_from_sidebar(self):
        """从左侧边栏首层文件夹加载分类，保持与左侧栏相同的顺序"""
        main_window = self._get_main_window()
        if not main_window or not hasattr(main_window, 'tool_list_widget'):
            return
            
        tree = main_window.tool_list_widget
        
        # 按左侧栏顺序收集文件夹名称
        ordered_categories = ["全部"]  # "全部"始终放在第一位
        
        # 遍历左侧边栏首层项，按顺序获取文件夹名称
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i)
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            
            # 只处理文件夹类型
            if item_data and item_data.get("type") == "folder":
                folder_name = item.text(0)
                if folder_name not in ordered_categories:
                    ordered_categories.append(folder_name)
        
        # 获取现有的分类名称
        existing_categories = set(self.category_buttons.keys())
        new_categories_set = set(ordered_categories)
        
        # 移除不再存在的分类按钮（保留"全部"）
        for category in list(existing_categories):
            if category not in new_categories_set and category != "全部":
                btn = self.category_buttons.pop(category)
                self.category_layout.removeWidget(btn)
                btn.deleteLater()
        
        # 按左侧栏顺序重新排列按钮
        # 首先隐藏所有现有按钮
        for btn in self.category_buttons.values():
            btn.setParent(None)
        
        # 按顺序添加按钮（创建新按钮或重用现有按钮）
        for category in ordered_categories:
            if category in self.category_buttons:
                # 重用现有按钮
                btn = self.category_buttons[category]
                self.category_layout.addWidget(btn)
            else:
                # 创建新按钮
                self._create_category_button(category)
                
        logger.info(f"从左侧边栏加载了分类: {ordered_categories}")
        
    def refresh_plugins(self):
        """刷新插件列表 - 与左侧列表保持同步"""
        logger.info("[refresh_plugins] 开始刷新")
        self.load_plugins()
        # 同时刷新分类按钮
        self.load_categories_from_sidebar()
        logger.info("[refresh_plugins] 刷新完成")
            
    def calculate_columns(self):
        """根据窗口宽度计算每行显示的卡片数量"""
        # 卡片最小宽度260 + 间距16 = 276
        card_width = 276
        # 左右边距各40
        container_width = self.cards_container.width()
        # 如果容器还未显示，使用默认宽度
        if container_width <= 0:
            container_width = 800  # 默认宽度
        available_width = container_width - 80
        # 计算列数（至少1列，最多4列）
        cols = max(1, min(available_width // card_width, 4))
        return cols
        
    def resizeEvent(self, event):
        """窗口大小变化时重新布局卡片（带防抖）"""
        super().resizeEvent(event)
        # 使用定时器防抖，避免频繁刷新
        if self._resize_timer is None:
            self._resize_timer = QTimer(self)
            self._resize_timer.setSingleShot(True)
            self._resize_timer.timeout.connect(self.refresh_cards)
        self._resize_timer.start(100)  # 100ms 后刷新
        
    def refresh_cards(self):
        """刷新插件卡片显示"""
        try:
            logger.info(f"[refresh_cards] 开始刷新卡片，插件数量: {len(self.plugins)}")
            # 清除现有卡片
            while self.cards_layout.count():
                item = self.cards_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # 筛选插件
            filtered_plugins = self.filter_plugins()
            logger.info(f"[refresh_cards] 筛选后插件数量: {len(filtered_plugins)}")
            
            # 根据窗口宽度计算列数
            max_cols = self.calculate_columns()
            logger.info(f"[refresh_cards] 计算列数: {max_cols}")
            
            # 创建卡片
            row, col = 0, 0
            
            for plugin in filtered_plugins:
                # 判断是否为热门插件（可以根据使用频率或其他规则）
                is_hot = plugin["name"] in ["Excel对比", "Excel合并", "文本去重", "JSON格式化"]
                
                # 获取图标
                icon = self.get_plugin_icon(plugin["name"])
                
                card = PluginCard(
                    plugin_name=plugin["name"],
                    description=plugin["description"],
                    icon_text=icon,
                    is_hot=is_hot
                )
                card.clicked.connect(self.on_card_clicked)
                
                self.cards_layout.addWidget(card, row, col)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            logger.info(f"[refresh_cards] 刷新完成，创建了 {len(filtered_plugins)} 个卡片")
        except Exception as e:
            logger.error(f"[refresh_cards] 刷新卡片失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
                
    def filter_plugins(self):
        """根据搜索和分类筛选插件"""
        search_text = self.search_input.text().lower()
        category = self.current_category
        
        filtered = []
        for plugin in self.plugins:
            # 搜索筛选
            if search_text and search_text not in plugin["name"].lower():
                continue
                
            # 分类筛选
            if category == "全部":
                filtered.append(plugin)
            else:
                # 根据文件夹分类筛选
                if self._is_plugin_in_category(plugin["name"], category):
                    filtered.append(plugin)
                    
        return filtered
        
    def _is_plugin_in_category(self, plugin_name, category_name):
        """检查插件是否属于指定分类（文件夹）"""
        main_window = self._get_main_window()
        if not main_window or not hasattr(main_window, 'tool_list_widget'):
            return False
            
        tree = main_window.tool_list_widget
        
        # 遍历左侧边栏查找指定文件夹
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i)
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            
            # 找到匹配的文件夹
            if item_data and item_data.get("type") == "folder":
                if item.text(0) == category_name:
                    # 检查插件是否在该文件夹下
                    for j in range(item.childCount()):
                        child_item = item.child(j)
                        child_data = child_item.data(0, Qt.ItemDataRole.UserRole)
                        if child_data and child_data.get("type") == "tool":
                            if child_data.get("name") == plugin_name:
                                return True
                    return False
                    
        return False
        
    def get_plugin_icon(self, plugin_name):
        """根据插件名称获取对应图标"""
        icon_map = {
            "Excel对比": "📊",
            "Excel合并": "📈",
            "Excel拆分": "📉",
            "考勤统计": "📋",
            "数据对比": "🔢",
            "文本清理": "📝",
            "文本去重": "🔄",
            "行过滤": "🔍",
            "前后缀": "🏷️",
            "JSON格式化": "🎨",
            "JSON/XML转换": "🔄",
            "YAML/JSON转换": "📄",
            "XML格式化": "📃",
            "UUID生成": "🆔",
            "身份证生成": "🎫",
        }
        return icon_map.get(plugin_name, "🔧")
        
    def on_search_changed(self, text):
        """搜索文本变化"""
        self.refresh_cards()
        
    def on_search_clicked(self):
        """搜索按钮点击"""
        self.refresh_cards()
        
    def on_category_changed(self, category):
        """分类切换"""
        self.current_category = category
        
        # 更新按钮状态
        for btn_category, btn in self.category_buttons.items():
            btn.setChecked(btn_category == category)
            
        self.refresh_cards()
        
    def on_card_clicked(self, plugin_name):
        """卡片点击事件"""
        self.plugin_selected.emit(plugin_name)
