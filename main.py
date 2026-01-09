import sys
import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFileDialog

from src.plugins.plugin_loader import PluginLoader, get_plugin_directory
from src.ui.main_window import MainWindow

VERSION = "1.0.0"
VERSION_INFO = """
技术支持：如有问题请联系管理员
"""


def show_about_dialog(parent):
    """显示关于对话框"""
    dialog = QDialog(parent)
    dialog.setWindowTitle("关于 X-Tool")
    dialog.setFixedSize(400, 300)

    layout = QVBoxLayout(dialog)

    title_label = QLabel("X-Tool")
    title_label.setFont(QFont("Microsoft YaHei", 24, QFont.Weight.Bold))
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title_label)

    version_label = QLabel(f"版本: {VERSION}")
    version_label.setFont(QFont("Microsoft YaHei", 14))
    version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(version_label)

    info_label = QLabel(VERSION_INFO)
    info_label.setFont(QFont("Microsoft YaHei", 12))
    info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    info_label.setStyleSheet("color: #666;")
    layout.addWidget(info_label)

    close_btn = QPushButton("确定")
    close_btn.setFont(QFont("Microsoft YaHei", 12))
    close_btn.setFixedWidth(100)
    close_btn.clicked.connect(dialog.accept)

    btn_layout = QHBoxLayout()
    btn_layout.addStretch()
    btn_layout.addWidget(close_btn)
    btn_layout.addStretch()
    layout.addLayout(btn_layout)

    dialog.exec()


def check_update(parent):
    """检查更新"""
    QMessageBox.information(parent, "检查更新", f"当前版本: {VERSION}\n\n已是最新版本，无需更新。")


def load_plugins(window: MainWindow):
    """加载并注册所有插件"""
    from src.db.database import Database
    db = Database()
    
    plugin_dir = get_plugin_directory()
    loader = PluginLoader(plugin_dir)
    plugins = loader.load_all_plugins()
    
    # 先加载所有插件
    plugin_map = {}
    for plugin in plugins:
        plugin_map[plugin.name] = plugin
        
        plugin.setStyleSheet("""
            QWidget {
                font-size: 16px;
            }
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
            }
            QLabel {
                font-size: 16px;
            }
            QComboBox {
                font-size: 16px;
                padding: 8px;
            }
            QTextEdit {
                font-size: 16px;
            }
            QPushButton {
                font-size: 16px;
                font-weight: bold;
            }
        """)

        plugin.on_activate()
    
    # 加载文件夹结构
    window._load_folder_structure(db)
    
    # 获取所有插件的文件夹关联和排序顺序
    conn = db.get_connection()
    cursor = conn.cursor()
    plugin_associations = cursor.execute(
        "SELECT plugin_name, folder_id, sort_order FROM plugin_folder_associations"
    ).fetchall()
    conn.close()
    
    # 按folder_id和sort_order分组
    plugins_by_folder = {}
    for plugin_name, folder_id, sort_order in plugin_associations:
        if folder_id not in plugins_by_folder:
            plugins_by_folder[folder_id] = []
        plugins_by_folder[folder_id].append((plugin_name, sort_order))
    
    # 按排序顺序加载根目录插件
    root_plugins = sorted(plugins_by_folder.get(None, []), key=lambda x: x[1])
    for plugin_name, sort_order in root_plugins:
        if plugin_name in plugin_map:
            window.add_tool(plugin_name, plugin_map[plugin_name], sort_order)
    
    # 按排序顺序加载文件夹内的插件
    for folder_id, plugin_list in plugins_by_folder.items():
        if folder_id is None:
            continue  # 根目录插件已经处理过了
        
        # 找到对应的文件夹项
        folder_item = None
        
        # 递归遍历所有项，查找匹配的folder_id
        def find_folder_item(item):
            nonlocal folder_item
            if not item or folder_item:
                return
            
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            if item_data and item_data.get("type") == "folder" and item_data.get("folder_id") == folder_id:
                folder_item = item
                return
            
            for i in range(item.childCount()):
                find_folder_item(item.child(i))
        
        # 先检查顶层项
        for i in range(window.tool_list_widget.topLevelItemCount()):
            find_folder_item(window.tool_list_widget.topLevelItem(i))
        
        if folder_item:
            # 按排序顺序添加插件到文件夹中
            sorted_plugins = sorted(plugin_list, key=lambda x: x[1])
            for plugin_name, sort_order in sorted_plugins:
                if plugin_name in plugin_map:
                    window.add_tool_to_folder(plugin_name, plugin_map[plugin_name], folder_item, sort_order)
        else:
            # 文件夹不存在，将插件添加到根目录
            for plugin_name, sort_order in plugin_list:
                if plugin_name in plugin_map:
                    window.add_tool(plugin_name, plugin_map[plugin_name], sort_order)
    
    # 加载没有关联的插件
    for plugin_name, plugin in plugin_map.items():
        if not any(plugin_name == p[0] for folder_plugins in plugins_by_folder.values() for p in folder_plugins):
            window.add_tool(plugin_name, plugin)
    
    # 默认显示欢迎页面
    # window.on_tool_selected(-1)  # 不再需要手动调用，首页按钮已默认选中
    
    return plugin_map


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setApplicationName("X-Tool")
    app.setApplicationDisplayName("X-Tool")
    app.setDesktopFileName("com.xtool.app")
    
    window = MainWindow()
    window.setWindowTitle(f"X-Tool v{VERSION}")

    menubar = window.menuBar()
    
    # 添加文件菜单，位于帮助菜单之前
    file_menu = menubar.addMenu("文件")
    
    # 添加新建子菜单
    new_menu = file_menu.addMenu("新建")
    
    # 添加新建文件夹功能
    new_folder_action = new_menu.addAction("文件夹")
    new_folder_action.triggered.connect(lambda: window._create_folder())
    
    # 添加分隔符
    file_menu.addSeparator()
    
    # 添加导入插件功能
    import_plugin_action = file_menu.addAction("导入插件")
    
    def import_plugin():
        """导入插件"""
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle("选择插件文件")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Python Files (*.py *.pyc)")
        
        if file_dialog.exec():
            # 获取选择的文件路径
            file_path = file_dialog.selectedFiles()[0]
            
            # 获取插件目录
            plugin_dir = get_plugin_directory()
            
            # 复制文件到插件目录
            import shutil
            import os
            
            # 获取文件名
            file_name = os.path.basename(file_path)
            destination_path = os.path.join(plugin_dir, file_name)
            
            try:
                # 检查文件是否已存在
                if os.path.exists(destination_path):
                    # 询问是否覆盖
                    reply = QMessageBox.question(
                        window, "文件已存在", 
                        f"插件文件 '{file_name}' 已存在，是否覆盖？",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    
                    if reply != QMessageBox.StandardButton.Yes:
                        return
                
                # 复制文件
                shutil.copy2(file_path, destination_path)
                
                # 刷新插件
                # 1. 清除现有的插件
                # 保存当前选中的项
                current_item = window.tool_list_widget.currentItem()
                current_item_type = None
                current_item_data = None
                if current_item:
                    current_item_data = current_item.data(0, Qt.ItemDataRole.UserRole)
                    if current_item_data:
                        current_item_type = current_item_data.get("type")
                
                # 清除所有工具项（保留首页）
                for i in range(window.tool_list_widget.topLevelItemCount() - 1, 0, -1):
                    item = window.tool_list_widget.topLevelItem(i)
                    window.tool_list_widget.takeTopLevelItem(i)
                
                # 清除堆栈部件中的所有工具页面（保留欢迎页面）
                for i in range(window.tool_stack_widget.count() - 1, 0, -1):
                    widget = window.tool_stack_widget.widget(i)
                    window.tool_stack_widget.removeWidget(widget)
                    widget.deleteLater()
                
                # 清空插件映射
                window.plugin_widget_map.clear()
                
                # 2. 重新加载插件
                load_plugins(window)
                
                # 3. 选择之前的工具或首页
                if current_item_type == "home":
                    # 选择首页
                    home_item = window.tool_list_widget.topLevelItem(0)
                    if home_item:
                        window.tool_list_widget.setCurrentItem(home_item)
                elif current_item_type == "tool" and current_item_data:
                    # 尝试重新选择之前的工具
                    tool_name = current_item_data.get("name")
                    if tool_name:
                        for i in range(window.tool_list_widget.topLevelItemCount()):
                            item = window.tool_list_widget.topLevelItem(i)
                            if item:
                                item_data = item.data(0, Qt.ItemDataRole.UserRole)
                                if item_data and item_data.get("type") == "tool" and item_data.get("name") == tool_name:
                                    window.tool_list_widget.setCurrentItem(item)
                                    break
                
                QMessageBox.information(window, "导入成功", f"插件 '{file_name}' 已成功导入并刷新。")
            except Exception as e:
                QMessageBox.warning(window, "导入失败", f"导入插件失败: {e}")
                print(f"导入插件失败: {e}")
                import traceback
                traceback.print_exc()
    
    import_plugin_action.triggered.connect(import_plugin)
    
    # 添加备份插件功能
    backup_plugin_action = file_menu.addAction("备份插件")
    
    def backup_plugins():
        """备份插件"""
        import shutil
        import os
        import json
        
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle("选择备份目录")
        file_dialog.setFileMode(QFileDialog.FileMode.Directory)
        file_dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        
        if file_dialog.exec():
            # 获取选择的备份目录
            backup_dir = file_dialog.selectedFiles()[0]
            
            # 获取插件目录
            plugin_dir = get_plugin_directory()
            
            try:
                # 创建插件备份目录
                plugins_backup_dir = os.path.join(backup_dir, "plugins")
                if not os.path.exists(plugins_backup_dir):
                    os.makedirs(plugins_backup_dir)
                
                # 复制所有插件文件
                plugin_files_copied = 0
                for item in os.listdir(plugin_dir):
                    if item.startswith("__"):
                        continue
                    if item.endswith(".py") or item.endswith(".pyc"):
                        source_path = os.path.join(plugin_dir, item)
                        dest_path = os.path.join(plugins_backup_dir, item)
                        shutil.copy2(source_path, dest_path)
                        plugin_files_copied += 1
                
                # 导出数据库关联数据
                from src.db.database import Database
                db = Database()
                conn = db.get_connection()
                cursor = conn.cursor()
                
                # 导出插件文件夹
                cursor.execute("SELECT id, name, parent_id, sort_order FROM plugin_folders ORDER BY parent_id, sort_order")
                folders = cursor.fetchall()
                
                # 导出插件关联
                cursor.execute("SELECT plugin_name, folder_id, sort_order FROM plugin_folder_associations")
                plugin_associations = cursor.fetchall()
                
                conn.close()
                
                # 保存关联数据到JSON文件
                backup_data = {
                    "folders": folders,
                    "plugin_associations": plugin_associations
                }
                
                backup_data_path = os.path.join(backup_dir, "plugin_backup_data.json")
                with open(backup_data_path, "w", encoding="utf-8") as f:
                    json.dump(backup_data, f, ensure_ascii=False, indent=4)
                
                QMessageBox.information(window, "备份成功", f"成功备份 {plugin_files_copied} 个插件文件和关联数据。")
            except Exception as e:
                QMessageBox.warning(window, "备份失败", f"备份插件失败: {e}")
                print(f"备份插件失败: {e}")
                import traceback
                traceback.print_exc()
    
    backup_plugin_action.triggered.connect(backup_plugins)
    
    # 添加恢复插件功能
    restore_plugin_action = file_menu.addAction("恢复插件")
    
    def restore_plugins():
        """恢复插件"""
        import shutil
        import os
        import json
        
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle("选择备份目录")
        file_dialog.setFileMode(QFileDialog.FileMode.Directory)
        file_dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        
        if file_dialog.exec():
            # 获取选择的备份目录
            backup_dir = file_dialog.selectedFiles()[0]
            
            # 检查备份目录是否有效
            plugins_backup_dir = os.path.join(backup_dir, "plugins")
            backup_data_path = os.path.join(backup_dir, "plugin_backup_data.json")
            
            if not os.path.exists(plugins_backup_dir) or not os.path.exists(backup_data_path):
                QMessageBox.warning(window, "备份无效", "所选目录不是有效的插件备份目录。")
                return
            
            # 获取插件目录
            plugin_dir = get_plugin_directory()
            
            try:
                # 复制所有插件文件
                plugin_files_restored = 0
                for item in os.listdir(plugins_backup_dir):
                    if item.startswith("__"):
                        continue
                    if item.endswith(".py") or item.endswith(".pyc"):
                        source_path = os.path.join(plugins_backup_dir, item)
                        dest_path = os.path.join(plugin_dir, item)
                        
                        # 检查文件是否已存在
                        if os.path.exists(dest_path):
                            # 询问是否覆盖
                            reply = QMessageBox.question(
                                window, "文件已存在", 
                                f"插件文件 '{item}' 已存在，是否覆盖？",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                                QMessageBox.StandardButton.No
                            )
                            
                            if reply == QMessageBox.StandardButton.Cancel:
                                return
                            elif reply == QMessageBox.StandardButton.No:
                                continue
                        
                        shutil.copy2(source_path, dest_path)
                        plugin_files_restored += 1
                
                # 导入数据库关联数据
                with open(backup_data_path, "r", encoding="utf-8") as f:
                    backup_data = json.load(f)
                
                from src.db.database import Database
                db = Database()
                conn = db.get_connection()
                cursor = conn.cursor()
                
                try:
                    # 开始事务
                    conn.execute("BEGIN TRANSACTION")
                    
                    # 清空现有数据
                    cursor.execute("DELETE FROM plugin_folder_associations")
                    cursor.execute("DELETE FROM plugin_folders")
                    
                    # 导入插件文件夹
                    folder_id_mapping = {}
                    for folder_data in backup_data["folders"]:
                        old_id, name, parent_id, sort_order = folder_data
                        
                        # 转换父文件夹ID
                        new_parent_id = folder_id_mapping.get(parent_id, parent_id)
                        
                        # 插入文件夹
                        cursor.execute(
                            "INSERT INTO plugin_folders (name, parent_id, sort_order) VALUES (?, ?, ?)",
                            (name, new_parent_id, sort_order)
                        )
                        
                        # 记录ID映射
                        folder_id_mapping[old_id] = cursor.lastrowid
                    
                    # 导入插件关联
                    for plugin_assoc_data in backup_data["plugin_associations"]:
                        plugin_name, folder_id, sort_order = plugin_assoc_data
                        
                        # 转换文件夹ID
                        new_folder_id = folder_id_mapping.get(folder_id, folder_id)
                        
                        # 插入插件关联
                        cursor.execute(
                            "INSERT INTO plugin_folder_associations (plugin_name, folder_id, sort_order) VALUES (?, ?, ?)",
                            (plugin_name, new_folder_id, sort_order)
                        )
                    
                    # 提交事务
                    conn.commit()
                    
                    # 刷新插件
                    # 1. 清除现有的插件
                    # 保存当前选中的项
                    current_item = window.tool_list_widget.currentItem()
                    current_item_type = None
                    current_item_data = None
                    if current_item:
                        current_item_data = current_item.data(0, Qt.ItemDataRole.UserRole)
                        if current_item_data:
                            current_item_type = current_item_data.get("type")
                    
                    # 清除所有工具项（保留首页）
                    for i in range(window.tool_list_widget.topLevelItemCount() - 1, 0, -1):
                        item = window.tool_list_widget.topLevelItem(i)
                        window.tool_list_widget.takeTopLevelItem(i)
                    
                    # 清除堆栈部件中的所有工具页面（保留欢迎页面）
                    for i in range(window.tool_stack_widget.count() - 1, 0, -1):
                        widget = window.tool_stack_widget.widget(i)
                        window.tool_stack_widget.removeWidget(widget)
                        widget.deleteLater()
                    
                    # 清空插件映射
                    window.plugin_widget_map.clear()
                    
                    # 2. 重新加载插件
                    load_plugins(window)
                    
                    # 3. 选择首页
                    home_item = window.tool_list_widget.topLevelItem(0)  # 首页是第一个顶层项
                    if home_item:
                        window.tool_list_widget.setCurrentItem(home_item)
                    
                    QMessageBox.information(window, "恢复成功", f"成功恢复 {plugin_files_restored} 个插件文件和关联数据。")
                    
                except Exception as e:
                    # 回滚事务
                    conn.rollback()
                    raise
                finally:
                    conn.close()
                
            except Exception as e:
                QMessageBox.warning(window, "恢复失败", f"恢复插件失败: {e}")
                print(f"恢复插件失败: {e}")
                import traceback
                traceback.print_exc()
    
    restore_plugin_action.triggered.connect(restore_plugins)

    # 添加帮助菜单
    help_menu = menubar.addMenu("帮助")

    about_action = help_menu.addAction("关于")
    about_action.triggered.connect(lambda: show_about_dialog(window))

    load_plugins(window)

    # 默认选中首页
    # 获取首页项
    home_item = window.tool_list_widget.topLevelItem(0)  # 首页是第一个顶层项
    if home_item:
        window.tool_list_widget.setCurrentItem(home_item)

    window.show()

    sys.exit(app.exec())
