from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, \
    QStackedWidget, QLabel, QSpacerItem, QSizePolicy, QMenu, QInputDialog, QMessageBox, QStyle


# 自定义TreeWidget类，用于处理拖拽事件
class CustomTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
    
    def dropEvent(self, event):
        # 调用父类的dropEvent来处理实际的移动
        super().dropEvent(event)
        
        # 通知父窗口保存排序顺序
        if hasattr(self.parent_window, '_save_folder_sort_order'):
            from src.db.database import Database
            db = Database()
            try:
                self.parent_window._save_folder_sort_order(db)
            except Exception as e:
                print(f"保存文件夹排序失败: {e}")


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
        self.tool_list_widget = CustomTreeWidget(self)
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
            /* 优化文件夹展开/折叠指示器样式 */
            QTreeWidget#toolList::branch {
                background-color: white;
            }
            QTreeWidget#toolList::branch:has-siblings:!adjoins-item {
                border-image: none;
                background-color: white;
            }
            QTreeWidget#toolList::branch:has-siblings:adjoins-item {
                border-image: none;
                background-color: white;
            }
            QTreeWidget#toolList::branch:!has-children:!has-siblings:adjoins-item {
                border-image: none;
                background-color: white;
            }
            /* 展开指示器颜色 */
            QTreeWidget#toolList::branch:open {
                background-color: white;
            }
            QTreeWidget#toolList::branch:closed {
                background-color: white;
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

    def add_tool(self, name, widget, sort_order=None):
        """添加工具到列表和堆栈"""
        # 添加到工具列表（默认添加到根目录）
        item = QTreeWidgetItem([name])
        item.setFont(0, QFont("Microsoft YaHei", 10))
        
        # 直接显示插件名称，不使用图标
        item.setText(0, name)
        
        item.setData(0, Qt.ItemDataRole.UserRole, {
            "type": "tool",
            "name": name
        })
        
        # 如果指定了排序顺序，调整项目位置
        if sort_order is not None and sort_order < self.tool_list_widget.topLevelItemCount():
            self.tool_list_widget.addTopLevelItem(item)
            self.tool_list_widget.takeTopLevelItem(self.tool_list_widget.indexOfTopLevelItem(item))
            self.tool_list_widget.insertTopLevelItem(sort_order, item)
        else:
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
        
        # 设置文件夹样式
        folder_item.setFont(0, QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        folder_item.setForeground(0, Qt.GlobalColor.darkBlue)  # 文件夹名称使用深蓝色
        
        # 使用Qt内置的文件夹图标
        style = self.style()
        folder_item.setIcon(0, style.standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        
        folder_item.setData(0, Qt.ItemDataRole.UserRole, {
            "type": "folder",
            "name": folder_name,
            "folder_id": folder_id  # 直接将folder_id存储在UserRole中
        })
        folder_item.setExpanded(True)
        
        return folder_item

    def add_tool_to_folder(self, tool_name, widget, folder_item, sort_order=None):
        """添加工具到指定文件夹"""
        # 添加到文件夹下
        item = QTreeWidgetItem(folder_item, [tool_name])
        item.setFont(0, QFont("Microsoft YaHei", 10))
        
        # 直接显示插件名称，不使用图标
        item.setText(0, tool_name)
        
        item.setData(0, Qt.ItemDataRole.UserRole, {
            "type": "tool",
            "name": tool_name
        })
        
        # 如果指定了排序顺序，调整项目位置
        if sort_order is not None and sort_order < folder_item.childCount():
            folder_item.removeChild(item)
            folder_item.insertChild(sort_order, item)
        
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
        
        # 导入插件选项
        import_plugin_action = menu.addAction("导入插件")
        import_plugin_action.triggered.connect(lambda: self._import_plugin_to_folder(folder_item))
        
        menu.exec(self.tool_list_widget.mapToGlobal(position))
    
    def _show_tool_context_menu(self, position, tool_item):
        """工具右键菜单"""
        menu = QMenu()
        
        # 添加删除插件选项
        delete_plugin_action = menu.addAction("删除插件")
        delete_plugin_action.triggered.connect(lambda: self._delete_plugin(tool_item))
        
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
                
                # 更新界面文本
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
    
    def _import_plugin_to_folder(self, folder_item):
        """将插件导入到指定文件夹"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from src.db.database import Database
        from src.plugins.plugin_loader import get_plugin_directory
        from main import load_plugins
        import shutil
        import os
        import sys
        import importlib.util
        from src.plugins.base_plugin import BasePlugin
        
        # 打开文件选择对话框
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle("选择插件文件")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Python Files (*.py *.pyc)")
        
        if file_dialog.exec():
            # 获取选择的文件路径
            file_path = file_dialog.selectedFiles()[0]
            
            # 获取插件目录
            plugin_dir = get_plugin_directory()
            
            # 获取文件名
            file_name = os.path.basename(file_path)
            destination_path = os.path.join(plugin_dir, file_name)
            
            try:
                # 检查文件是否已存在
                if os.path.exists(destination_path):
                    # 询问是否覆盖
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("文件已存在")
                    msg_box.setText(f"插件文件 '{file_name}' 已存在，是否覆盖？")
                    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    msg_box.setDefaultButton(QMessageBox.StandardButton.No)
                    
                    # 修改按钮文本
                    msg_box.button(QMessageBox.StandardButton.Yes).setText("确定")
                    msg_box.button(QMessageBox.StandardButton.No).setText("取消")
                    
                    reply = msg_box.exec()
                    
                    if reply != QMessageBox.StandardButton.Yes:
                        return
                
                # 复制文件到插件目录
                shutil.copy2(file_path, destination_path)
                
                # 获取真实的插件名称（从插件类的name属性获取）
                plugin_name = None
                module_name = os.path.splitext(file_name)[0]
                
                # 尝试加载插件，获取其真实名称
                try:
                    # 动态加载插件模块
                    spec = importlib.util.spec_from_file_location(module_name, destination_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[module_name] = module
                        spec.loader.exec_module(module)
                        
                        # 查找插件类
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (isinstance(attr, type) and
                                issubclass(attr, BasePlugin) and
                                attr is not BasePlugin):
                                # 创建插件实例并获取名称
                                plugin_instance = attr()
                                plugin_name = plugin_instance.name
                                break
                except Exception as e:
                    print(f"加载插件获取名称失败: {e}")
                    # 如果加载失败，回退到使用文件名作为插件名称
                    plugin_name = module_name
                
                # 保存插件与文件夹的关联关系
                with Database() as db:
                    # 获取文件夹ID
                    folder_data = folder_item.data(0, Qt.ItemDataRole.UserRole)
                    folder_id = folder_data.get("folder_id")
                    
                    # 先移除原有关联（如果存在）
                    cursor = db.get_connection().cursor()
                    cursor.execute("DELETE FROM plugin_folder_associations WHERE plugin_name = ?", (plugin_name,))
                    db.get_connection().commit()
                    
                    # 重新关联插件与文件夹
                    db.associate_plugin_with_folder(plugin_name, folder_id)
                    
                    # 更新插件文件夹映射
                    self.plugin_folder_map[plugin_name] = folder_id
                
                # 刷新插件列表（与文件菜单的导入插件保持一致的逻辑）
                # 保存当前选中的项
                current_item = self.tool_list_widget.currentItem()
                current_item_type = None
                current_item_data = None
                if current_item:
                    current_item_data = current_item.data(0, Qt.ItemDataRole.UserRole)
                    if current_item_data:
                        current_item_type = current_item_data.get("type")
                
                # 清除所有工具项（保留首页）
                for i in range(self.tool_list_widget.topLevelItemCount() - 1, 0, -1):
                    item = self.tool_list_widget.topLevelItem(i)
                    self.tool_list_widget.takeTopLevelItem(i)
                
                # 清除堆栈部件中的所有工具页面（保留欢迎页面）
                for i in range(self.tool_stack_widget.count() - 1, 0, -1):
                    widget = self.tool_stack_widget.widget(i)
                    self.tool_stack_widget.removeWidget(widget)
                
                # 清除插件映射
                self.plugin_widget_map.clear()
                
                # 重新加载所有插件
                load_plugins(self)
                
                QMessageBox.information(self, "导入成功", f"插件 '{file_name}' 已成功导入到文件夹中！")
                
            except Exception as e:
                QMessageBox.critical(self, "导入失败", f"导入插件时出错：{str(e)}")
    
    def _find_plugin_file(self, plugin_name, plugin_dir):
        """根据插件名称查找插件文件"""
        import os
        import sys
        import importlib.util
        from src.plugins.base_plugin import BasePlugin
        
        # 遍历插件目录中的所有.py和.pyc文件
        for item in os.listdir(plugin_dir):
            if item.startswith("__"):
                continue
                
            file_path = os.path.join(plugin_dir, item)
            if not (item.endswith(".py") or item.endswith(".pyc")):
                continue
                
            try:
                # 获取模块名称（不包含扩展名）
                module_name = item[:-3] if item.endswith(".py") else item[:-4]
                
                # 加载模块
                if item.endswith(".pyc"):
                    # 加载.pyc文件
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if spec is None:
                        continue
                    
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                else:
                    # 加载.py文件
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if spec is None:
                        continue
                    
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                
                # 查找插件类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and
                        issubclass(attr, BasePlugin) and
                        attr is not BasePlugin):
                        # 创建插件实例
                        plugin_instance = attr()
                        # 检查插件名称是否匹配
                        if plugin_instance.name == plugin_name:
                            return file_path
            except Exception as e:
                print(f"加载插件文件 '{item}' 失败: {e}")
                continue
        
        return None
    
    def _delete_plugin(self, tool_item):
        """删除插件"""
        # 获取插件信息
        item_data = tool_item.data(0, Qt.ItemDataRole.UserRole)
        if not item_data or item_data.get("type") != "tool":
            return
        
        plugin_name = item_data.get("name")
        if not plugin_name:
            return
        
        # 显示确认对话框
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("确认删除")
        msg_box.setText(f"确定要删除插件 '{plugin_name}' 吗？\n此操作无法撤销。")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        # 修改按钮文本
        msg_box.button(QMessageBox.StandardButton.Yes).setText("确定")
        msg_box.button(QMessageBox.StandardButton.No).setText("取消")
        
        reply = msg_box.exec()
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # 从数据库模块导入Database类
        from src.db.database import Database
        import os
        from src.plugins.plugin_loader import get_plugin_directory
        
        try:
            # 1. 从数据库中删除插件与文件夹的关联
            db = Database()
            db.remove_plugin_from_folder(plugin_name)
            
            # 2. 从插件文件夹中删除插件文件
            plugin_dir = get_plugin_directory()
            
            # 根据插件名称查找实际的插件文件
            plugin_file = self._find_plugin_file(plugin_name, plugin_dir)
            if plugin_file:
                # 删除找到的文件
                if os.path.exists(plugin_file):
                    os.remove(plugin_file)
                    print(f"已删除插件文件: {plugin_file}")
                    
                    # 也删除对应的.pyc或.py文件（如果存在）
                    if plugin_file.endswith(".py"):
                        pyc_file = plugin_file + "c"
                        if os.path.exists(pyc_file):
                            os.remove(pyc_file)
                            print(f"已删除插件文件: {pyc_file}")
                    else:  # .pyc文件
                        py_file = plugin_file[:-1]  # 去掉c扩展名
                        if os.path.exists(py_file):
                            os.remove(py_file)
                            print(f"已删除插件文件: {py_file}")
            else:
                print(f"未找到插件 '{plugin_name}' 对应的文件")
            
            # 3. 从界面中移除插件项
            parent = tool_item.parent()
            if parent:
                # 插件在文件夹中
                parent.removeChild(tool_item)
            else:
                # 插件在根目录
                index = self.tool_list_widget.indexOfTopLevelItem(tool_item)
                self.tool_list_widget.takeTopLevelItem(index)
            
            # 4. 清理插件与widget的映射
            if plugin_name in self.plugin_widget_map:
                # 5. 从堆栈部件中移除插件页面
                widget = self.plugin_widget_map[plugin_name]
                self.tool_stack_widget.removeWidget(widget)
                widget.deleteLater()
                
                # 删除映射
                del self.plugin_widget_map[plugin_name]
            
            # 6. 处理删除后的界面状态
            # 如果当前显示的是被删除的插件页面，切换到首页
            current_widget = self.tool_stack_widget.currentWidget()
            if not current_widget or current_widget not in self.plugin_widget_map.values():
                # 切换到首页
                home_item = self.tool_list_widget.topLevelItem(0)  # 首页是第一个项
                if home_item:
                    self.tool_list_widget.setCurrentItem(home_item)
            
            QMessageBox.information(self, "删除成功", f"插件 '{plugin_name}' 已成功删除")
            
        except Exception as e:
            QMessageBox.warning(self, "删除失败", f"删除插件失败: {e}")
            print(f"删除插件失败: {e}")
    
    def dragEnterEvent(self, event):
        """拖动进入事件"""
        # 只接受内部移动
        if event.source() == self.tool_list_widget:
            event.accept()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        """拖动移动事件"""
        # 允许文件夹之间的排序和工具到文件夹的拖动
        event.accept()
    
    def on_item_moved(self, item, old_parent, old_index, new_parent, new_index):
        """处理项目移动事件，保存文件夹排序顺序"""
        # 从数据库模块导入Database类
        from src.db.database import Database
        db = Database()
        
        try:
            # 更新所有文件夹的排序顺序
            self._save_folder_sort_order(db)
        except Exception as e:
            print(f"保存文件夹排序失败: {e}")
    
    def _update_plugin_folder_association(self, db, plugin_name, item):
        """更新插件与文件夹的关联"""
        parent = item.parent()
        if parent:
            # 插件在文件夹内
            parent_data = parent.data(0, Qt.ItemDataRole.UserRole)
            if parent_data and parent_data.get("type") == "folder":
                folder_id = parent_data.get("folder_id")
                if folder_id:
                    # 更新插件的文件夹关联和排序顺序
                    # 获取插件在新文件夹中的索引
                    sort_order = parent.indexOfChild(item)
                    print(f"插件 {plugin_name} 被拖拽到文件夹 {parent_data.get('name')}，新排序: {sort_order}")
                    # 更新数据库中的文件夹关联和排序顺序
                    conn = db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE plugin_folder_associations SET folder_id = ?, sort_order = ? WHERE plugin_name = ?",
                        (folder_id, sort_order, plugin_name)
                    )
                    conn.commit()
                    conn.close()
        else:
            # 插件在根目录
            # 更新插件排序顺序
            sort_order = self.tool_list_widget.indexOfTopLevelItem(item)
            if sort_order >= 0:
                # 先确保插件与根目录关联
                db.associate_plugin_with_folder(plugin_name, None)
                # 然后更新排序顺序
                db.update_plugin_sort_order(plugin_name, sort_order)

    def _save_folder_sort_order(self, db):
        """保存所有文件夹和工具的排序顺序到数据库"""
        print("开始保存文件夹和插件排序顺序...")
        
        # 遍历顶层项目，更新文件夹和工具的排序顺序
        for i in range(self.tool_list_widget.topLevelItemCount()):
            item = self.tool_list_widget.topLevelItem(i)
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            
            if item_data:
                if item_data.get("type") == "folder":
                    folder_id = item_data.get("folder_id")
                    if folder_id:
                        print(f"更新文件夹排序: {item_data.get('name')} (ID: {folder_id}) -> 排序: {i}")
                        db.update_folder_sort_order(folder_id, i)
                        
                        # 遍历文件夹内的项目，更新其排序顺序
                        for j in range(item.childCount()):
                            child_item = item.child(j)
                            child_data = child_item.data(0, Qt.ItemDataRole.UserRole)
                            
                            if child_data:
                                if child_data.get("type") == "folder":
                                    child_folder_id = child_data.get("folder_id")
                                    if child_folder_id:
                                        print(f"更新子文件夹排序: {child_data.get('name')} (ID: {child_folder_id}) -> 排序: {j}")
                                        db.update_folder_sort_order(child_folder_id, j)
                                elif child_data.get("type") == "tool":
                                    tool_name = child_data.get("name")
                                    if tool_name:
                                        print(f"更新文件夹内插件排序: {tool_name} -> 排序: {j}")
                                        db.update_plugin_sort_order(tool_name, j)
                                        
                                        # 更新插件的文件夹关联
                                        self._update_plugin_folder_association(db, tool_name, child_item)
                elif item_data.get("type") == "tool":
                    tool_name = item_data.get("name")
                    if tool_name:
                        print(f"更新根目录插件排序: {tool_name} -> 排序: {i}")
                        db.update_plugin_sort_order(tool_name, i)
                        
                        # 更新插件的文件夹关联
                        self._update_plugin_folder_association(db, tool_name, item)
        
        print("排序顺序保存完成!")
    
    def _load_folder_structure(self, db):
        """从数据库加载文件夹结构"""
        # 获取所有文件夹
        folders = db.get_all_folders()
        
        # 按parent_id分组
        folders_by_parent = {}
        for folder_id, name, parent_id, sort_order in folders:
            if parent_id not in folders_by_parent:
                folders_by_parent[parent_id] = []
            folders_by_parent[parent_id].append((folder_id, name, sort_order))
        
        # 递归创建文件夹结构
        def create_folder_tree(parent_id, parent_item=None):
            if parent_id not in folders_by_parent:
                return
            
            # 按sort_order排序文件夹
            sorted_folders = sorted(folders_by_parent[parent_id], key=lambda x: x[2])
            
            for folder_id, name, _ in sorted_folders:
                # 创建文件夹项
                folder_item = self.add_folder(name, parent_item, folder_id)
                
                # 递归创建子文件夹
                create_folder_tree(folder_id, folder_item)
        
        # 创建根目录文件夹
        create_folder_tree(None)