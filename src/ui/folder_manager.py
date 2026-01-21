from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QTreeWidgetItem, QInputDialog, QMessageBox, QStyle

from src.db.database import Database
from src.utils.logger import logger


class FolderManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def add_folder(self, folder_name, parent_item=None, folder_id=None):
        """添加文件夹到树控件"""
        if parent_item:
            folder_item = QTreeWidgetItem(parent_item, [folder_name])
        else:
            folder_item = QTreeWidgetItem([folder_name])
            self.main_window.tool_list_widget.addTopLevelItem(folder_item)  # 显式添加到顶层

        # 设置文件夹样式
        folder_item.setFont(0, QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        folder_item.setForeground(0, Qt.GlobalColor.darkBlue)  # 文件夹名称使用深蓝色

        # 设置文件夹图标
        style = self.main_window.style()
        folder_item.setIcon(0, style.standardIcon(QStyle.StandardPixmap.SP_DirIcon))

        # 设置文件夹数据
        folder_item.setData(0, Qt.ItemDataRole.UserRole, {
            "type": "folder",
            "name": folder_name,
            "folder_id": folder_id  # 直接将folder_id存储在UserRole中
        })

        folder_item.setExpanded(True)
        return folder_item

    def create_folder(self, parent_item=None):
        """创建文件夹"""
        # 获取父文件夹ID
        parent_id = None
        if parent_item:
            parent_data = parent_item.data(0, Qt.ItemDataRole.UserRole)
            if parent_data and parent_data.get("type") == "folder":
                parent_id = parent_data.get("folder_id")

        # 显示输入对话框
        folder_name, ok = QInputDialog.getText(self.main_window, "创建文件夹", "请输入文件夹名称:", text="新建文件夹")
        if not ok or not folder_name.strip():
            return

        folder_name = folder_name.strip()

        # 检查是否重名
        if self._is_folder_name_exists(folder_name, parent_item):
            msg_box = QMessageBox(self.main_window)
            msg_box.setWindowTitle("错误")
            msg_box.setText(f"同一目录下已存在名为 '{folder_name}' 的文件夹")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
            msg_box.exec()
            return

        try:
            # 将文件夹信息保存到数据库
            with Database() as db:
                folder_id = db.folder_manager.add_folder(folder_name, parent_id)

            # 添加文件夹到树控件
            folder_item = self.add_folder(folder_name, parent_item, folder_id)

            # 保存排序顺序
            with Database() as db:
                self.save_folder_sort_order(db)

        except Exception as e:
            msg_box = QMessageBox(self.main_window)
            msg_box.setWindowTitle("错误")
            msg_box.setText(f"创建文件夹失败: {e}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
            msg_box.exec()
            logger.error(f"创建文件夹失败: {e}")

    def edit_folder_name(self, folder_item):
        """编辑文件夹名称"""
        current_name = folder_item.text(0)
        new_name, ok = QInputDialog.getText(self.main_window, "编辑文件夹名称", "请输入新的文件夹名称:", text=current_name)
        if not ok or not new_name.strip():
            return

        new_name = new_name.strip()

        # 检查是否重名
        parent_item = folder_item.parent()
        if self._is_folder_name_exists(new_name, parent_item, exclude_item=folder_item):
            msg_box = QMessageBox(self.main_window)
            msg_box.setWindowTitle("错误")
            msg_box.setText(f"同一目录下已存在名为 '{new_name}' 的文件夹")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
            msg_box.exec()
            return

        try:
            # 更新数据库中的文件夹名称
            item_data = folder_item.data(0, Qt.ItemDataRole.UserRole)
            if item_data and item_data.get("folder_id"):
                folder_id = item_data.get("folder_id")
                with Database() as db:
                    db.folder_manager.update_folder_name(folder_id, new_name)

                # 更新树控件中的文件夹名称
                folder_item.setText(0, new_name)

                # 更新UserRole中的文件夹名称
                item_data = folder_item.data(0, Qt.ItemDataRole.UserRole)
                if item_data:
                    item_data["name"] = new_name
                    folder_item.setData(0, Qt.ItemDataRole.UserRole, item_data)

        except Exception as e:
            msg_box = QMessageBox(self.main_window)
            msg_box.setWindowTitle("错误")
            msg_box.setText(f"编辑文件夹名称失败: {e}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
            msg_box.exec()
            logger.error(f"编辑文件夹名称失败: {e}")

    def delete_folder(self, folder_item):
        """删除文件夹"""
        # 检查文件夹是否为空
        if folder_item.childCount() > 0:
            msg_box = QMessageBox(self.main_window)
            msg_box.setWindowTitle("警告")
            msg_box.setText("文件夹不为空，删除将移除所有子项。是否继续？")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)
            msg_box.button(QMessageBox.StandardButton.Yes).setText("确定")
            msg_box.button(QMessageBox.StandardButton.No).setText("取消")
            reply = msg_box.exec()

            if reply != QMessageBox.StandardButton.Yes:
                return

        try:
            # 先删除文件夹中的所有插件
            # 从后往前删除，避免索引变化问题
            for i in range(folder_item.childCount() - 1, -1, -1):
                child_item = folder_item.child(i)
                child_data = child_item.data(0, Qt.ItemDataRole.UserRole)
                if child_data and child_data.get("type") == "tool":
                    # 调用tool_manager的delete_plugin方法删除插件，不显示确认对话框
                    self.main_window.tool_manager.delete_plugin(child_item, show_confirmation=False)

            # 从数据库中删除文件夹
            item_data = folder_item.data(0, Qt.ItemDataRole.UserRole)
            if item_data and item_data.get("folder_id"):
                folder_id = item_data.get("folder_id")
                with Database() as db:
                    db.folder_manager.delete_folder(folder_id)

            # 从树控件中移除文件夹
            parent = folder_item.parent()
            if parent:
                parent.removeChild(folder_item)
            else:
                index = self.main_window.tool_list_widget.indexOfTopLevelItem(folder_item)
                if index != -1:
                    self.main_window.tool_list_widget.takeTopLevelItem(index)

            # 清除引用
            folder_item = None

        except Exception as e:
            msg_box = QMessageBox(self.main_window)
            msg_box.setWindowTitle("错误")
            msg_box.setText(f"删除文件夹失败: {e}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
            msg_box.exec()
            logger.error(f"删除文件夹失败: {e}")

    def _is_folder_name_exists(self, folder_name, parent_item, exclude_item=None):
        """检查文件夹名称是否已存在"""
        # 检查同一父文件夹下是否有相同名称的文件夹
        items_to_check = []
        if parent_item:
            # 检查父文件夹下的子文件夹
            for i in range(parent_item.childCount()):
                child_item = parent_item.child(i)
                if child_item != exclude_item:
                    items_to_check.append(child_item)
        else:
            # 检查顶层文件夹
            for i in range(self.main_window.tool_list_widget.topLevelItemCount()):
                top_item = self.main_window.tool_list_widget.topLevelItem(i)
                if top_item != exclude_item:
                    items_to_check.append(top_item)

        # 遍历检查
        for item in items_to_check:
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            if item_data and item_data.get("type") == "folder" and item_data.get("name") == folder_name:
                return True
        return False

    def save_folder_sort_order(self, db):
        """保存文件夹排序顺序、顶层插件排序顺序和首页排序位置"""
        # 保存顶层项目排序（包括文件夹、顶层插件和首页）
        for i in range(self.main_window.tool_list_widget.topLevelItemCount()):
            item = self.main_window.tool_list_widget.topLevelItem(i)
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            
            if item_data.get("type") == "home":
                # 保存首页排序位置
                db.config_manager.set_home_page_sort_order(i)
            elif item_data.get("type") == "folder":
                folder_id = item_data.get("folder_id")
                if folder_id:
                    db.folder_manager.update_folder_sort_order(folder_id, i)
            elif item_data.get("type") == "tool":
                plugin_name = item_data.get("name")
                if plugin_name:
                    # 更新顶层插件的排序顺序（folder_id为None表示顶层插件）
                    db.plugin_association_manager.update_plugin_sort_order(plugin_name, i)
            
            # 保存子文件夹排序
            for j in range(item.childCount()):
                child_item = item.child(j)
                child_data = child_item.data(0, Qt.ItemDataRole.UserRole)
                
                if child_data.get("type") == "folder":
                    child_folder_id = child_data.get("folder_id")
                    if child_folder_id:
                        db.folder_manager.update_folder_sort_order(child_folder_id, j)
                elif child_data.get("type") == "tool":
                    plugin_name = child_data.get("name")
                    if plugin_name:
                        # 更新文件夹内插件的排序顺序
                        db.plugin_association_manager.update_plugin_sort_order(plugin_name, j)

    def load_folder_structure(self, db):
        """加载文件夹结构"""
        # 获取所有文件夹
        folders = db.folder_manager.get_all_folders()
        
        # 按父ID分组
        folders_by_parent = {}
        for folder_id, name, parent_id, sort_order in folders:
            if parent_id not in folders_by_parent:
                folders_by_parent[parent_id] = []
            folders_by_parent[parent_id].append((folder_id, name, sort_order))
        
        # 递归创建文件夹结构
        def create_folder_tree(parent_id, parent_item=None):
            if parent_id not in folders_by_parent:
                return
            
            # 按排序顺序排序
            sorted_folders = sorted(folders_by_parent[parent_id], key=lambda x: x[2])
            
            for folder_id, name, sort_order in sorted_folders:
                folder_item = self.add_folder(name, parent_item, folder_id)
                create_folder_tree(folder_id, folder_item)
        
        # 从根目录开始创建
        create_folder_tree(None)
