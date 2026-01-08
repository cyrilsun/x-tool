from PyQt6.QtWidgets import QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, \
    QStackedWidget, QHeaderView, QLabel, QSpacerItem, QSizePolicy, QMenu, QLineEdit, QInputDialog, QMessageBox
from PyQt6.QtCore import Qt, QMimeData, QPoint, QCoreApplication
from PyQt6.QtGui import QFont, QPixmap, QDrag, QCursor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("X-Tool")
        self.setGeometry(100, 100, 1200, 700)
        
        # 插件与widget映射
        self.plugin_widget_map = {}
        
        # 插件文件夹映射，用于数据库操作
        self.plugin_folder_map = {}  # plugin_name: folder_id

        # 设置应用样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QMainWindow::separator {
                background-color: #d0d0d0;
            }
            QMenuBar {
                background-color: #f5f5f5;
                border-bottom: 1px solid #d0d0d0;
                padding: 4px;
                font-size: 14px;
            }
            QMenuBar::item:selected {
                background-color: #e0e0e0;
            }
            QMenu {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
            }
            QMenu::item:selected {
                background-color: #4a90e2;
                color: white;
            }
            QSplitter::handle {
                background-color: #d0d0d0;
            }
            QSplitter::handle:horizontal {
                width: 1px;
            }
        """)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建水平布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建分割器
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        # 创建左侧工具列表（树形结构）
        self.tool_list_widget = QTreeWidget()
        self.tool_list_widget.setMinimumWidth(220)
        self.tool_list_widget.setMaximumWidth(300)
        self.tool_list_widget.setObjectName("toolList")
        self.tool_list_widget.setHeaderHidden(True)
        self.tool_list_widget.setStyleSheet("""
            QTreeWidget#toolList {
                background-color: #ffffff;
                border: none;
                border-right: 1px solid #d0d0d0;
                outline: none;
            }
            QTreeWidget#toolList::item {
                padding: 8px 15px;
                border-bottom: 1px solid #eee;
                font-size: 14px;
            }
            QTreeWidget#toolList::item:selected {
                background-color: #4a90e2;
                color: white;
            }
            QTreeWidget#toolList::item:hover {
                background-color: #e6f0fa;
            }
            QTreeWidget#toolList::item:selected:hover {
                background-color: #3a7bc8;
            }
            QTreeWidget#toolList QTreeWidgetItem {
                margin-bottom: 2px;
            }
        """)
        
        # 设置拖放功能
        self.tool_list_widget.setDragEnabled(True)
        self.tool_list_widget.setAcceptDrops(True)
        self.tool_list_widget.setDropIndicatorShown(True)
        self.tool_list_widget.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        
        self.splitter.addWidget(self.tool_list_widget)

        # 创建右侧工具使用界面容器
        self.tool_stack_widget = QStackedWidget()
        self.tool_stack_widget.setStyleSheet("""
            QStackedWidget {
                background-color: #fafafa;
            }
        """)
        self.splitter.addWidget(self.tool_stack_widget)

        # 设置分割器比例
        self.splitter.setSizes([220, 980])

        # 连接工具列表点击信号
        self.tool_list_widget.currentItemChanged.connect(self.on_tool_selected)
        
        # 连接右键菜单信号
        self.tool_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tool_list_widget.customContextMenuRequested.connect(self.show_context_menu)

        # 添加首页按钮和欢迎页面
        self._add_home_button()
        self._init_welcome_page()

    def _init_welcome_page(self):
        """初始化欢迎页面"""
        welcome_page = self._create_welcome_page()
        self.tool_stack_widget.addWidget(welcome_page)

    def _add_home_button(self):
        """添加首页按钮"""
        item = QTreeWidgetItem(["首页"])
        item.setFont(0, QFont("Microsoft YaHei", 10))
        item.setData(0, Qt.ItemDataRole.UserRole, {
            "type": "home"
        })
        self.tool_list_widget.addTopLevelItem(item)

    def _create_welcome_page(self):
        """创建欢迎页面"""
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setContentsMargins(60, 60, 60, 60)
        welcome_layout.setSpacing(20)

        # 标题
        title_label = QLabel("欢迎使用 X-Tool")
        title_font = QFont("Microsoft YaHei", 28, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #333;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(title_label)

        # 副标题
        subtitle_label = QLabel("多功能工具集合平台")
        subtitle_font = QFont("Microsoft YaHei", 16)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #666;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(subtitle_label)

        # 添加弹性空间
        welcome_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # 说明文字
        info_label = QLabel("请从左侧列表选择工具开始使用")
        info_font = QFont("Microsoft YaHei", 14)
        info_label.setFont(info_font)
        info_label.setStyleSheet("color: #888;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(info_label)

        # 添加弹性空间
        welcome_layout.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # 版本信息
        version_label = QLabel("版本 1.0.0")
        version_font = QFont("Microsoft YaHei", 11)
        version_label.setFont(version_font)
        version_label.setStyleSheet("color: #aaa;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(version_label)

        return welcome_widget

    def _add_welcome_page(self):
        """添加欢迎页面作为默认页面"""
        welcome_page = self._create_welcome_page()
        self.tool_stack_widget.addWidget(welcome_page)

    def _clear_welcome_page(self):
        """清除欢迎页面"""
        # 移除欢迎页面（索引0）
        if self.tool_stack_widget.count() > 0:
            welcome_page = self.tool_stack_widget.widget(0)
            self.tool_stack_widget.removeWidget(welcome_page)
            welcome_page.deleteLater()

    def add_tool(self, name, widget):
        """添加工具到列表和堆栈"""
        # 添加到工具列表（默认添加到根目录）
        item = QTreeWidgetItem([name])
        item.setFont(0, QFont("Microsoft YaHei", 10))
        item.setData(0, Qt.ItemDataRole.UserRole, {
            "type": "tool",
            "name": name
        })
        self.tool_list_widget.addTopLevelItem(item)

        # 保存插件与widget的映射
        self.plugin_widget_map[name] = widget

        # 添加到堆栈部件
        self.tool_stack_widget.addWidget(widget)

    def on_tool_selected(self, current_item, previous_item):
        """工具列表选择事件"""
        if not current_item:
            return
        
        item_data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not item_data:
            return
        
        item_type = item_data.get("type")
        if item_type == "home":
            # 首页显示欢迎页面
            self.tool_stack_widget.setCurrentIndex(0)
        elif item_type == "tool":
            # 工具页面
            tool_name = item_data.get("name")
            if tool_name in self.plugin_widget_map:
                widget = self.plugin_widget_map[tool_name]
                self.tool_stack_widget.setCurrentWidget(widget)
        elif item_type == "folder":
            # 文件夹，不切换页面
            pass

    def add_folder(self, folder_name, parent_item=None, folder_id=None):
        """添加文件夹到工具列表"""
        if parent_item:
            folder_item = QTreeWidgetItem(parent_item, [folder_name])
        else:
            folder_item = QTreeWidgetItem([folder_name])
            self.tool_list_widget.addTopLevelItem(folder_item)  # 显式添加到顶层
        
        folder_item.setFont(0, QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        folder_item.setData(0, Qt.ItemDataRole.UserRole, {
            "type": "folder",
            "name": folder_name,
            "folder_id": folder_id  # 直接将folder_id存储在UserRole中
        })
        folder_item.setExpanded(True)
        
        return folder_item

    def add_tool_to_folder(self, tool_name, widget, folder_item):
        """添加工具到指定文件夹"""
        # 添加到文件夹下
        item = QTreeWidgetItem(folder_item, [tool_name])
        item.setFont(0, QFont("Microsoft YaHei", 10))
        item.setData(0, Qt.ItemDataRole.UserRole, {
            "type": "tool",
            "name": tool_name
        })
        
        # 保存插件与widget的映射
        self.plugin_widget_map[tool_name] = widget
        
        # 添加到堆栈部件
        self.tool_stack_widget.addWidget(widget)
    
    def show_context_menu(self, position):
        """显示右键菜单"""
        item = self.tool_list_widget.itemAt(position)
        if not item:
            # 点击空白处，只显示创建文件夹选项
            self._show_empty_area_context_menu(position)
            return
        
        item_data = item.data(0, Qt.ItemDataRole.UserRole)
        if not item_data:
            return
        
        item_type = item_data.get("type")
        if item_type == "folder":
            # 文件夹右键菜单
            self._show_folder_context_menu(position, item)
        elif item_type == "tool":
            # 工具右键菜单
            self._show_tool_context_menu(position, item)
        elif item_type == "home":
            # 首页不显示右键菜单
            pass
    
    def _show_empty_area_context_menu(self, position):
        """空白处右键菜单"""
        menu = QMenu()
        
        # 创建文件夹选项
        create_folder_action = menu.addAction("创建文件夹")
        create_folder_action.triggered.connect(self._create_folder)
        
        menu.exec(self.tool_list_widget.mapToGlobal(position))
    
    def _show_folder_context_menu(self, position, folder_item):
        """文件夹右键菜单"""
        menu = QMenu()
        
        # 创建文件夹选项
        create_folder_action = menu.addAction("创建文件夹")
        create_folder_action.triggered.connect(lambda: self._create_folder(folder_item))
        
        # 编辑文件夹名称
        edit_folder_action = menu.addAction("编辑名称")
        edit_folder_action.triggered.connect(lambda: self._edit_folder_name(folder_item))
        
        # 删除文件夹选项
        delete_folder_action = menu.addAction("删除文件夹")
        delete_folder_action.triggered.connect(lambda: self._delete_folder(folder_item))
        
        menu.exec(self.tool_list_widget.mapToGlobal(position))
    
    def _show_tool_context_menu(self, position, tool_item):
        """工具右键菜单"""
        menu = QMenu()
        
        # 这里可以添加工具相关的右键菜单选项
        # 例如：移到文件夹、删除等
        
        menu.exec(self.tool_list_widget.mapToGlobal(position))
    
    def _create_folder(self, parent_item=None):
        """创建文件夹"""
        # 从数据库模块导入Database类
        from src.db.database import Database
        db = Database()
        
        # 获取文件夹名称
        folder_name, ok = QInputDialog.getText(self, "创建文件夹", "请输入文件夹名称:", text="新建文件夹")
        if not ok or not folder_name.strip():
            return
        folder_name = folder_name.strip()
        
        # 检查父文件夹ID
        parent_id = None
        if parent_item:
            parent_data = parent_item.data(0, Qt.ItemDataRole.UserRole)
            if parent_data and parent_data.get("type") == "folder":
                parent_id = parent_data.get("folder_id")
        
        try:
            # 添加到数据库
            folder_id = db.add_folder(folder_name, parent_id)
            
            # 添加到界面
            folder_item = self.add_folder(folder_name, parent_item, folder_id)
        except Exception as e:
            # 捕获数据库唯一性约束错误
            if "UNIQUE constraint failed" in str(e):
                QMessageBox.warning(self, "创建失败", f"同一目录下已存在名为 '{folder_name}' 的文件夹")
            else:
                QMessageBox.warning(self, "创建失败", f"创建文件夹失败: {e}")
            print(f"创建文件夹失败: {e}")
    
    def _edit_folder_name(self, folder_item):
        """编辑文件夹名称"""
        # 从数据库模块导入Database类
        from src.db.database import Database
        db = Database()
        
        # 获取当前文件夹名称
        current_name = folder_item.text(0)
        
        # 获取新文件夹名称
        new_name, ok = QInputDialog.getText(self, "编辑文件夹名称", "请输入新的文件夹名称:", text=current_name)
        if not ok or not new_name.strip():
            return
        new_name = new_name.strip()
        
        # 检查是否与原名称相同
        if new_name == current_name:
            return
        
        # 检查是否在数据库中
        item_data = folder_item.data(0, Qt.ItemDataRole.UserRole)
        if item_data and item_data.get("folder_id"):
            folder_id = item_data.get("folder_id")
            
            try:
                # 更新数据库
                db.update_folder_name(folder_id, new_name)
                
                # 更新界面
                folder_item.setText(0, new_name)
                
                # 更新用户数据
                item_data = folder_item.data(0, Qt.ItemDataRole.UserRole)
                if item_data:
                    item_data["name"] = new_name
                    folder_item.setData(0, Qt.ItemDataRole.UserRole, item_data)
            except Exception as e:
                # 捕获数据库唯一性约束错误
                if "UNIQUE constraint failed" in str(e):
                    QMessageBox.warning(self, "编辑失败", f"同一目录下已存在名为 '{new_name}' 的文件夹")
                else:
                    QMessageBox.warning(self, "编辑失败", f"更新文件夹名称失败: {e}")
                print(f"更新文件夹名称失败: {e}")
    
    def _delete_folder(self, folder_item):
        """删除文件夹"""
        # 检查文件夹是否为空
        if folder_item.childCount() > 0:
            # 文件夹不为空，不能删除
            return
        
        # 从数据库模块导入Database类
        from src.db.database import Database
        db = Database()
        
        try:
            # 检查是否在数据库中
            item_data = folder_item.data(0, Qt.ItemDataRole.UserRole)
            if item_data and item_data.get("folder_id"):
                folder_id = item_data.get("folder_id")
                
                # 从数据库中删除
                db.delete_folder(folder_id)
            
            # 从父项中移除
            parent = folder_item.parent()
            if parent:
                parent.removeChild(folder_item)
            else:
                index = self.tool_list_widget.indexOfTopLevelItem(folder_item)
                self.tool_list_widget.takeTopLevelItem(index)
            
            # 清理数据
            folder_item = None
        except Exception as e:
            print(f"删除文件夹失败: {e}")
    
    def dragEnterEvent(self, event):
        """拖动进入事件"""
        # 只接受内部移动
        if event.source() == self.tool_list_widget:
            event.accept()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        """拖动移动事件"""
        # 只接受工具到文件夹的拖动
        item = self.tool_list_widget.itemAt(event.pos())
        if not item:
            event.ignore()
            return
        
        item_data = item.data(0, Qt.ItemDataRole.UserRole)
        if not item_data:
            event.ignore()
            return
        
        # 只允许拖到文件夹上
        if item_data.get("type") == "folder":
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """放置事件"""
        # 获取拖动的项目
        dragged_item = self.tool_list_widget.currentItem()
        if not dragged_item:
            event.ignore()
            return
        
        dragged_data = dragged_item.data(0, Qt.ItemDataRole.UserRole)
        if not dragged_data or dragged_data.get("type") != "tool":
            event.ignore()
            return
        
        # 获取目标文件夹
        target_item = self.tool_list_widget.itemAt(event.pos())
        if not target_item:
            event.ignore()
            return
        
        target_data = target_item.data(0, Qt.ItemDataRole.UserRole)
        if not target_data or target_data.get("type") != "folder":
            event.ignore()
            return
        
        # 从数据库模块导入Database类
        from src.db.database import Database
        db = Database()
        
        try:
            # 获取工具名称和文件夹ID
            tool_name = dragged_data.get("name")
            target_data = target_item.data(0, Qt.ItemDataRole.UserRole)
            folder_id = target_data.get("folder_id") if target_data else None
            
            if folder_id:
                # 更新数据库关联
                db.associate_plugin_with_folder(tool_name, folder_id)
                
                # 更新插件文件夹映射
                self.plugin_folder_map[tool_name] = folder_id
            
            # 移动项目
            super().dropEvent(event)
            
        except Exception as e:
            print(f"拖放操作失败: {e}")
            event.ignore()
    
    def _load_folder_structure(self, db):
        """从数据库加载文件夹结构"""
        # 获取所有文件夹
        folders = db.get_all_folders()
        
        # 按parent_id分组
        folders_by_parent = {}
        for folder_id, name, parent_id in folders:
            if parent_id not in folders_by_parent:
                folders_by_parent[parent_id] = []
            folders_by_parent[parent_id].append((folder_id, name))
        
        # 递归创建文件夹结构
        def create_folder_tree(parent_id, parent_item=None):
            if parent_id not in folders_by_parent:
                return
            
            for folder_id, name in folders_by_parent[parent_id]:
                # 创建文件夹项
                folder_item = self.add_folder(name, parent_item, folder_id)
                
                # 递归创建子文件夹
                create_folder_tree(folder_id, folder_item)
        
        # 创建根目录文件夹
        create_folder_tree(None)
