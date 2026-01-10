from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QTreeWidgetItem, QMessageBox

from src.utils.logger import logger


class ToolManager:
    def __init__(self, main_window):
        self.main_window = main_window
    
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
        if sort_order is not None and sort_order < self.main_window.tool_list_widget.topLevelItemCount():
            self.main_window.tool_list_widget.addTopLevelItem(item)
            self.main_window.tool_list_widget.takeTopLevelItem(self.main_window.tool_list_widget.indexOfTopLevelItem(item))
            self.main_window.tool_list_widget.insertTopLevelItem(sort_order, item)
        else:
            self.main_window.tool_list_widget.addTopLevelItem(item)

        # 保存插件与widget的映射
        self.main_window.plugin_widget_map[name] = widget

        # 添加到堆栈部件
        self.main_window.tool_stack_widget.addWidget(widget)

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
            self.main_window.tool_stack_widget.setCurrentIndex(0)
        elif item_type == "tool":
            # 工具页面
            tool_name = item_data.get("name")
            if tool_name in self.main_window.plugin_widget_map:
                widget = self.main_window.plugin_widget_map[tool_name]
                self.main_window.tool_stack_widget.setCurrentWidget(widget)
        elif item_type == "folder":
            # 文件夹，不切换页面
            pass

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
        self.main_window.plugin_widget_map[tool_name] = widget
        
        # 添加到堆栈部件
        self.main_window.tool_stack_widget.addWidget(widget)

    def delete_plugin(self, tool_item, show_confirmation=True):
        """删除插件
        
        Args:
            tool_item: 要删除的工具项
            show_confirmation: 是否显示确认对话框，默认为True
        """
        item_data = tool_item.data(0, Qt.ItemDataRole.UserRole)
        if not item_data or item_data.get("type") != "tool":
            return
        
        tool_name = item_data.get("name")
        if not tool_name:
            return
        
        # 确认删除（仅当show_confirmation为True时）
        if show_confirmation:
            msg_box = QMessageBox(self.main_window)
            msg_box.setWindowTitle("确认删除")
            msg_box.setText(f"确定要删除插件 '{tool_name}' 吗？")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)
            
            # 修改按钮文本
            msg_box.button(QMessageBox.StandardButton.Yes).setText("确定")
            msg_box.button(QMessageBox.StandardButton.No).setText("取消")
            
            reply = msg_box.exec()
            
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # 执行删除操作
        try:
            # 从数据库中删除插件和关联
            from src.db.database import Database
            from src.plugins.plugin_loader import get_plugin_directory
            import os
            
            with Database() as db:
                # 获取插件文件名
                plugin_file_name = db.plugin_manager.get_plugin_file_name(tool_name)
                
                # 删除插件关联
                db.plugin_association_manager.remove_plugin_from_folder(tool_name)
                
                # 删除插件记录
                db.plugin_manager.delete_plugin(tool_name)
            
            # 从文件系统中删除插件文件
            if plugin_file_name:
                plugin_dir = get_plugin_directory()
                # 尝试删除.py和.pyc文件
                for ext in [".py", ".pyc"]:
                    file_path = os.path.join(plugin_dir, f"{plugin_file_name}{ext}")
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"成功删除插件文件: {file_path}")
                    else:
                        logger.info(f"插件文件不存在: {file_path}")
            else:
                logger.warning(f"无法获取插件文件名，插件名: {tool_name}")
                # 如果无法获取文件名，尝试通过插件名查找文件
                plugin_dir = get_plugin_directory()
                for item in os.listdir(plugin_dir):
                    if not item.startswith("__") and (item.endswith(".py") or item.endswith(".pyc")):
                        # 尝试加载插件文件，检查其名称是否匹配
                        try:
                            import importlib.util
                            from src.plugins.base_plugin import BasePlugin
                            file_path = os.path.join(plugin_dir, item)
                            module_name = os.path.splitext(item)[0]
                            spec = importlib.util.spec_from_file_location(module_name, file_path)
                            if spec and spec.loader:
                                module = importlib.util.module_from_spec(spec)
                                spec.loader.exec_module(module)
                                for attr_name in dir(module):
                                    attr = getattr(module, attr_name)
                                    if (isinstance(attr, type) and
                                        issubclass(attr, BasePlugin) and
                                        attr is not BasePlugin):
                                        plugin_instance = attr()
                                        if plugin_instance.name == tool_name:
                                            # 找到了匹配的插件文件，删除它
                                            os.remove(file_path)
                                            logger.info(f"成功删除插件文件: {file_path}")
                                            # 如果是.py文件，也删除对应的.pyc文件
                                            if item.endswith(".py"):
                                                pyc_path = os.path.join(plugin_dir, f"{module_name}.pyc")
                                                if os.path.exists(pyc_path):
                                                    os.remove(pyc_path)
                                                    logger.info(f"成功删除插件文件: {pyc_path}")
                                            break
                        except Exception as e:
                            logger.error(f"检查插件文件 {item} 失败: {e}")
            
            # 从工具列表中移除
            if tool_item.parent():
                tool_item.parent().removeChild(tool_item)
            else:
                self.main_window.tool_list_widget.takeTopLevelItem(
                    self.main_window.tool_list_widget.indexOfTopLevelItem(tool_item)
                )
            
            # 从插件映射中移除
            if tool_name in self.main_window.plugin_widget_map:
                widget = self.main_window.plugin_widget_map.pop(tool_name)
                # 从堆栈部件中移除
                if widget in [self.main_window.tool_stack_widget.widget(i) for i in range(self.main_window.tool_stack_widget.count())]:
                    self.main_window.tool_stack_widget.removeWidget(widget)
                    widget.deleteLater()
            
            # 显示删除成功消息（仅当show_confirmation为True时，避免删除文件夹时显示多个消息）
            if show_confirmation:
                msg_box = QMessageBox(self.main_window)
                msg_box.setWindowTitle("删除成功")
                msg_box.setText(f"插件 '{tool_name}' 已成功删除。")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
                msg_box.exec()
        except Exception as e:
            msg_box = QMessageBox(self.main_window)
            msg_box.setWindowTitle("删除失败")
            msg_box.setText(f"删除插件失败: {e}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
            msg_box.exec()
            logger.error(f"删除插件失败: {e}")

    def import_plugin_to_folder(self, folder_item):
        """将插件导入到指定文件夹"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from src.db.database import Database
        from src.plugins.plugin_loader import get_plugin_directory
        from src.plugins.plugin_manager import load_plugins
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
                    msg_box = QMessageBox(self.main_window)
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
                    logger.error(f"加载插件获取名称失败: {e}")
                    # 如果加载失败，回退到使用文件名作为插件名称
                    plugin_name = module_name
                
                # 保存插件与文件夹的关联关系
                try:
                    with Database() as db:
                        # 获取文件夹ID
                        folder_data = folder_item.data(0, Qt.ItemDataRole.UserRole)
                        folder_id = folder_data.get("folder_id")
                        
                        # 重新关联插件与文件夹
                        # associate_plugin_with_folder方法已经包含了先删除原有关联的逻辑
                        db.plugin_association_manager.associate_plugin_with_folder(plugin_name, folder_id)
                        
                        # 更新插件文件夹映射
                        self.main_window.plugin_folder_map[plugin_name] = folder_id
                except Exception as e:
                    logger.error(f"关联插件与文件夹失败: {e}")
                    raise
                
                # 刷新插件列表（与文件菜单的导入插件保持一致的逻辑）
                # 保存当前选中的项
                current_item = self.main_window.tool_list_widget.currentItem()
                current_item_type = None
                current_item_data = None
                if current_item:
                    current_item_data = current_item.data(0, Qt.ItemDataRole.UserRole)
                    if current_item_data:
                        current_item_type = current_item_data.get("type")
                
                # 清除所有工具项（保留首页）
                for i in range(self.main_window.tool_list_widget.topLevelItemCount() - 1, 0, -1):
                    item = self.main_window.tool_list_widget.topLevelItem(i)
                    self.main_window.tool_list_widget.takeTopLevelItem(i)
                
                # 清除堆栈部件中的所有工具页面（保留欢迎页面）
                for i in range(self.main_window.tool_stack_widget.count() - 1, 0, -1):
                    widget = self.main_window.tool_stack_widget.widget(i)
                    self.main_window.tool_stack_widget.removeWidget(widget)
                
                # 重新加载所有插件
                load_plugins(self.main_window)
                
                # 显示成功消息
                msg_box = QMessageBox(self.main_window)
                msg_box.setWindowTitle("导入成功")
                msg_box.setText(f"插件 '{plugin_name}' 已成功导入到文件夹中")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
                msg_box.exec()
                
            except Exception as e:
                msg_box = QMessageBox(self.main_window)
                msg_box.setWindowTitle("导入失败")
                msg_box.setText(f"导入插件时出错：{e}")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
                msg_box.exec()
                logger.error(f"导入插件失败: {e}")