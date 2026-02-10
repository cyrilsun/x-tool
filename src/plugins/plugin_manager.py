import json
import os
import sys
import shutil
import traceback
import zipfile
import tempfile
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from src.db.database import Database
from src.plugins.plugin_loader import PluginLoader, get_plugin_directory
from src.utils.path_utils import get_lib_directory
from src.utils.logger import logger


def load_plugins(window):
    """加载并注册所有插件"""
    plugin_dir = get_plugin_directory()
    loader = PluginLoader(plugin_dir)
    plugins = loader.load_all_plugins()
    
    # 先加载所有插件
    plugin_map = {}
    for plugin in plugins:
        try:
            plugin_map[plugin.name] = plugin
            
            plugin.setStyleSheet("""
                QWidget {
                    background-color: transparent;
                    color: #2f3640;
                    font-family: "Segoe UI", "Microsoft YaHei";
                    font-size: 14px;
                }
                QGroupBox {
                    font-size: 16px;
                    font-weight: bold;
                    color: #2c3e50;
                    border: 1px solid #dcdde1;
                    border-radius: 8px;
                    margin-top: 15px;
                    padding-top: 15px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 5px;
                }
                QLabel {
                    color: #636e72;
                }
                QLineEdit, QComboBox, QSpinBox, QTextEdit {
                    border: 1px solid #dcdde1;
                    border-radius: 4px;
                    padding: 6px 10px;
                    background-color: #ffffff;
                }
                QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {
                    border: 1px solid #3498db;
                }
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #1e3799;
                }
                QScrollArea {
                    border: none;
                    background-color: transparent;
                }
                QScrollBar:vertical {
                    border: none;
                    background: rgba(0, 0, 0, 0.05);
                    width: 8px;
                    margin: 0px;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical {
                    background: #95a5a6;
                    min-height: 20px;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #7f8c8d;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar:horizontal {
                    border: none;
                    background: rgba(0, 0, 0, 0.05);
                    height: 8px;
                    margin: 0px;
                    border-radius: 4px;
                }
                QScrollBar::handle:horizontal {
                    background: #95a5a6;
                    min-width: 20px;
                    border-radius: 4px;
                }
                QScrollBar::handle:horizontal:hover {
                    background: #7f8c8d;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    width: 0px;
                }
            """)

            try:
                plugin.on_activate()
            except Exception as e:
                logger.error(f"激活插件 {plugin.name} 失败: {e}")
                logger.error(traceback.format_exc())
                # 继续加载其他插件，不中断整个流程
        except Exception as e:
            logger.error(f"处理插件 {plugin.name} 失败: {e}")
            logger.error(traceback.format_exc())
            # 继续处理其他插件，不中断整个流程
    
    # 加载文件夹结构
    try:
        with Database() as db:
            window.folder_manager.load_folder_structure(db)
            
            # 获取所有插件的文件夹关联和排序顺序
            plugin_associations = db.plugin_association_manager.get_all_plugin_associations()
        
        # 按folder_id和sort_order分组
        plugins_by_folder = {}
        for plugin_name, folder_id, sort_order in plugin_associations:
            if folder_id not in plugins_by_folder:
                plugins_by_folder[folder_id] = []
            plugins_by_folder[folder_id].append((plugin_name, sort_order))
    except Exception as e:
        logger.error(f"加载文件夹结构和插件关联失败: {e}")
        logger.error(traceback.format_exc())
        # 创建默认的空结构，确保应用可以继续运行
        plugins_by_folder = {}
    
    # 按排序顺序加载根目录插件
    root_plugins = sorted(plugins_by_folder.get(None, []), key=lambda x: x[1])
    for plugin_name, sort_order in root_plugins:
        if plugin_name in plugin_map:
            try:
                window.tool_manager.add_tool(plugin_name, plugin_map[plugin_name], sort_order)
            except Exception as e:
                logger.error(f"为根目录添加工具 {plugin_name} 失败: {e}")
                logger.error(traceback.format_exc())
                # 继续添加其他工具，不中断整个流程
    
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
                    try:
                        window.tool_manager.add_tool_to_folder(plugin_name, plugin_map[plugin_name], folder_item, sort_order)
                    except Exception as e:
                        logger.error(f"为文件夹 {folder_id} 添加工具 {plugin_name} 失败: {e}")
                        logger.error(traceback.format_exc())
                        # 继续添加其他工具，不中断整个流程
        else:
            # 文件夹不存在，将插件添加到根目录
            for plugin_name, sort_order in plugin_list:
                if plugin_name in plugin_map:
                    try:
                        window.tool_manager.add_tool(plugin_name, plugin_map[plugin_name], sort_order)
                    except Exception as e:
                        logger.error(f"文件夹不存在时为根目录添加工具 {plugin_name} 失败: {e}")
                        logger.error(traceback.format_exc())
                        # 继续添加其他工具，不中断整个流程
    
    # 加载没有关联的插件
    for plugin_name, plugin in plugin_map.items():
        if not any(plugin_name == p[0] for folder_plugins in plugins_by_folder.values() for p in folder_plugins):
            try:
                window.tool_manager.add_tool(plugin_name, plugin)
            except Exception as e:
                logger.error(f"加载没有关联的插件 {plugin_name} 失败: {e}")
                logger.error(traceback.format_exc())
                # 继续添加其他工具，不中断整个流程
    
    # 调整首页位置
    with Database() as db:
        home_sort_order = db.config_manager.get_home_page_sort_order()
        
        # 获取当前首页位置
        current_home_index = -1
        for i in range(window.tool_list_widget.topLevelItemCount()):
            item = window.tool_list_widget.topLevelItem(i)
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            if item_data and item_data.get("type") == "home":
                current_home_index = i
                break
        
        # 如果首页存在且位置需要调整
        if current_home_index != -1 and current_home_index != home_sort_order:
            # 移除首页项
            home_item = window.tool_list_widget.takeTopLevelItem(current_home_index)
            # 在保存的位置插入首页项
            window.tool_list_widget.insertTopLevelItem(home_sort_order, home_item)
    
    return plugin_map


def import_plugin(window):
    """导入插件（支持 .py 和 .xpkg 格式）"""
    file_dialog = QFileDialog()
    file_dialog.setWindowTitle("选择插件文件")
    file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
    file_dialog.setNameFilter("插件文件 (*.py *.xpkg);;Python 文件 (*.py);插件包 (*.xpkg)")
    
    if not file_dialog.exec():
        return
    
    file_path = file_dialog.selectedFiles()[0]
    
    # 判断文件类型
    if file_path.endswith(".xpkg"):
        _import_xpkg_plugin(window, file_path)
    else:
        _import_py_plugin(window, file_path)


def _import_py_plugin(window, file_path):
    """导入 Python 插件文件"""
    # 获取插件目录
    plugin_dir = get_plugin_directory()
    
    # 获取文件名
    file_name = os.path.basename(file_path)
    destination_path = os.path.join(plugin_dir, file_name)
    
    try:
        # 检查文件是否已存在
        if os.path.exists(destination_path):
            # 询问是否覆盖
            msg_box = QMessageBox(window)
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
        
        # 检查是否是已存在的插件
        plugin_name_without_ext = os.path.splitext(file_name)[0]
        
        # 复制文件并打印调试信息
        logger.info(f"正在复制插件文件: {file_path} -> {destination_path}")
        shutil.copy2(file_path, destination_path)
        logger.info(f"插件文件复制成功，目标文件存在: {os.path.exists(destination_path)}")
        
        # 如果是覆盖现有插件，删除所有与该插件相关的关联关系
        with Database() as db:
            # 查找与该文件名相关的所有插件
            existing_plugin_names = db.plugin_manager.get_plugins_by_file_name(plugin_name_without_ext)
            
            # 删除这些插件的关联关系，使它们回到根目录
            for plugin_name in existing_plugin_names:
                db.plugin_association_manager.remove_plugin_from_folder(plugin_name)
        
        # 刷新插件
        _refresh_plugins(window)
        
        msg_box = QMessageBox(window)
        msg_box.setWindowTitle("导入成功")
        msg_box.setText(f"插件 '{file_name}' 已成功导入并刷新。")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
        msg_box.exec()
    except Exception as e:
        msg_box = QMessageBox(window)
        msg_box.setWindowTitle("导入失败")
        msg_box.setText(f"导入插件失败: {e}")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
        msg_box.exec()
        logger.error(f"导入插件失败: {e}")
        logger.error(traceback.format_exc())


def backup_plugins(window):
    """备份插件"""
    file_dialog = QFileDialog()
    file_dialog.setWindowTitle("选择备份目录")
    file_dialog.setFileMode(QFileDialog.FileMode.Directory)
    file_dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
    
    if file_dialog.exec():
        # 获取选择的备份目录
        backup_dir = file_dialog.selectedFiles()[0]
        # 获取插件目录、lib 目录和 data 目录
        plugin_dir = get_plugin_directory()
        lib_dir = get_lib_directory()
        from src.utils.path_utils import get_data_directory
        data_dir = get_data_directory()
        try:
            # 创建插件备份目录
            plugins_backup_dir = os.path.join(backup_dir, "plugins")
            if not os.path.exists(plugins_backup_dir):
                os.makedirs(plugins_backup_dir)
            
            # 创建 lib 备份目录
            lib_backup_dir = os.path.join(backup_dir, "lib")
            if not os.path.exists(lib_backup_dir):
                os.makedirs(lib_backup_dir)
            
            # 创建 data 备份目录
            data_backup_dir = os.path.join(backup_dir, "data")
            if not os.path.exists(data_backup_dir):
                os.makedirs(data_backup_dir)
            
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
            
            # 复制 lib 目录下的依赖
            lib_files_copied = 0
            if os.path.exists(lib_dir):
                for item in os.listdir(lib_dir):
                    source_path = os.path.join(lib_dir, item)
                    dest_path = os.path.join(lib_backup_dir, item)
                    if os.path.isdir(source_path):
                        if os.path.exists(dest_path):
                            shutil.rmtree(dest_path)
                        shutil.copytree(source_path, dest_path)
                    else:
                        shutil.copy2(source_path, dest_path)
                    lib_files_copied += 1
            
            # 复制 data 目录下的配置数据
            data_dirs_copied = 0
            if os.path.exists(data_dir):
                for item in os.listdir(data_dir):
                    # 跳过非插件目录（如数据库文件）
                    if item.endswith('.db') or item.startswith('.'):
                        continue
                    source_path = os.path.join(data_dir, item)
                    if os.path.isdir(source_path):
                        dest_path = os.path.join(data_backup_dir, item)
                        if os.path.exists(dest_path):
                            shutil.rmtree(dest_path)
                        shutil.copytree(source_path, dest_path)
                        data_dirs_copied += 1
                        logger.info(f"备份配置目录: {item}")
            
            # 导出数据库关联数据
            with Database() as db:
                # 导出插件文件夹
                folders = db.folder_manager.get_all_folders()
                
                # 导出插件关联
                plugin_associations = db.plugin_association_manager.get_all_plugin_associations()
            
            # 保存关联数据到JSON文件
            backup_data = {
                "folders": folders,
                "plugin_associations": plugin_associations
            }
            
            backup_data_path = os.path.join(backup_dir, "plugin_backup_data.json")
            with open(backup_data_path, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=4)
            
            msg_box = QMessageBox(window)
            msg_box.setWindowTitle("备份成功")
            msg_box.setText(f"成功备份 {plugin_files_copied} 个插件文件、{lib_files_copied} 个依赖项、{data_dirs_copied} 个配置目录和关联数据。")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
            msg_box.exec()
        except Exception as e:
            msg_box = QMessageBox(window)
            msg_box.setWindowTitle("备份失败")
            msg_box.setText(f"备份插件失败: {e}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
            msg_box.exec()
            logger.error(f"备份插件失败: {e}")
            logger.error(traceback.format_exc())


def restore_plugins(window):
    """恢复插件"""
    file_dialog = QFileDialog()
    file_dialog.setWindowTitle("选择备份目录")
    file_dialog.setFileMode(QFileDialog.FileMode.Directory)
    file_dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
    
    if file_dialog.exec():
        # 获取选择的备份目录
        backup_dir = file_dialog.selectedFiles()[0]
        
        # 检查备份目录是否有效
        plugins_backup_dir = os.path.join(backup_dir, "plugins")
        lib_backup_dir = os.path.join(backup_dir, "lib")
        backup_data_path = os.path.join(backup_dir, "plugin_backup_data.json")
        
        if not os.path.exists(plugins_backup_dir) or not os.path.exists(backup_data_path):
            msg_box = QMessageBox(window)
            msg_box.setWindowTitle("备份无效")
            msg_box.setText("所选目录不是有效的插件备份目录。")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
            msg_box.exec()
            return
        # 获取插件目录、lib 目录和 data 目录
        plugin_dir = get_plugin_directory()
        lib_dir = get_lib_directory()
        from src.utils.path_utils import get_data_directory
        data_dir = get_data_directory()
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
                        msg_box = QMessageBox(window)
                        msg_box.setWindowTitle("文件已存在")
                        msg_box.setText(f"插件文件 '{item}' 已存在，是否覆盖？")
                        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
                        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
                        
                        # 修改按钮文本
                        msg_box.button(QMessageBox.StandardButton.Yes).setText("确定")
                        msg_box.button(QMessageBox.StandardButton.No).setText("取消")
                        msg_box.button(QMessageBox.StandardButton.Cancel).setText("取消")
                        
                        reply = msg_box.exec()
                        
                        if reply == QMessageBox.StandardButton.Cancel:
                            return
                        elif reply == QMessageBox.StandardButton.No:
                            continue
                    
                    shutil.copy2(source_path, dest_path)
                    plugin_files_restored += 1
            
            # 恢复 lib 目录下的依赖
            lib_files_restored = 0
            if os.path.exists(lib_backup_dir):
                for item in os.listdir(lib_backup_dir):
                    source_path = os.path.join(lib_backup_dir, item)
                    dest_path = os.path.join(lib_dir, item)
                    
                    if os.path.isdir(source_path):
                        if os.path.exists(dest_path):
                            shutil.rmtree(dest_path)
                        shutil.copytree(source_path, dest_path)
                    else:
                        shutil.copy2(source_path, dest_path)
                    lib_files_restored += 1
            
            # 恢复 data 目录下的配置数据
            data_backup_dir = os.path.join(backup_dir, "data")
            data_dirs_restored = 0
            if os.path.exists(data_backup_dir):
                for item in os.listdir(data_backup_dir):
                    source_path = os.path.join(data_backup_dir, item)
                    if os.path.isdir(source_path):
                        dest_path = os.path.join(data_dir, item)
                        if os.path.exists(dest_path):
                            shutil.rmtree(dest_path)
                        shutil.copytree(source_path, dest_path)
                        data_dirs_restored += 1
                        logger.info(f"恢复配置目录: {item}")
            
            # 导入数据库关联数据
            with open(backup_data_path, "r", encoding="utf-8") as f:
                backup_data = json.load(f)
            
            # 执行数据库操作
            with Database() as db:
                # 清空现有数据
                db.plugin_association_manager.clear_all_associations()
                db.folder_manager.clear_all_folders()
                
                # 导入插件文件夹
                folder_id_mapping = {}
                for folder_data in backup_data["folders"]:
                    old_id, name, parent_id, sort_order = folder_data
                    
                    # 转换父文件夹ID
                    new_parent_id = folder_id_mapping.get(parent_id, parent_id)
                    
                    # 插入文件夹
                    new_folder_id = db.folder_manager.insert_folder_with_sort_order(name, new_parent_id, sort_order)
                    
                    # 记录ID映射
                    folder_id_mapping[old_id] = new_folder_id
                
                # 导入插件关联
                for plugin_assoc_data in backup_data["plugin_associations"]:
                    plugin_name, folder_id, sort_order = plugin_assoc_data
                    
                    # 转换文件夹ID
                    new_folder_id = folder_id_mapping.get(folder_id, folder_id)
                    
                    # 插入插件关联
                    db.plugin_association_manager.insert_association(plugin_name, new_folder_id, sort_order)
            # 数据库操作结束
            
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
            
            msg_box = QMessageBox(window)
            msg_box.setWindowTitle("恢复成功")
            msg_box.setText(f"成功恢复 {plugin_files_restored} 个插件文件、{lib_files_restored} 个依赖项、{data_dirs_restored} 个配置目录和关联数据。")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
            msg_box.exec()
        
        except Exception as e:
            msg_box = QMessageBox(window)
            msg_box.setWindowTitle("恢复失败")
            msg_box.setText(f"恢复插件失败: {e}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
            msg_box.exec()
            logger.error(f"恢复插件失败: {e}")
            logger.error(traceback.format_exc())


def export_single_plugin(window, plugin_name):
    """导出单个插件为 .xpkg 文件"""
    try:
        # 验证插件名
        if not plugin_name:
            raise Exception("插件名为空，无法导出")
        
        # 选择保存位置
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle("导出插件")
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setNameFilter("插件包 (*.xpkg)")
        file_dialog.setDefaultSuffix("xpkg")
        
        # 设置默认目录为用户主目录
        import os
        default_dir = os.path.expanduser("~")
        file_dialog.setDirectory(default_dir)
        
        # 设置默认文件名
        safe_plugin_name = plugin_name.replace(" ", "_").replace("/", "_")
        default_filename = f"{safe_plugin_name}_{datetime.now().strftime('%Y%m%d')}.xpkg"
        file_dialog.selectFile(default_filename)
        
        if not file_dialog.exec():
            return
        
        export_path = file_dialog.selectedFiles()[0]
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 1. 复制插件文件
            plugin_dir = get_plugin_directory()
            
            # 从数据库获取插件文件名
            with Database() as db:
                plugin_file_name = db.plugin_manager.get_plugin_file_name(plugin_name)
            
            if not plugin_file_name:
                # 尝试通过插件名查找文件
                plugin_file_name = _find_plugin_file(plugin_dir, plugin_name)
            
            if not plugin_file_name:
                raise Exception(f"找不到插件文件：{plugin_name}")
            
            # 复制插件文件
            plugin_file_path = os.path.join(plugin_dir, f"{plugin_file_name}.py")
            if os.path.exists(plugin_file_path):
                shutil.copy2(plugin_file_path, os.path.join(temp_dir, "plugin.py"))
            else:
                raise Exception(f"插件文件不存在：{plugin_file_path}")
            
            # 2. 复制 lib 依赖（如果存在）
            lib_dir = get_lib_directory()
            has_lib = False
            if os.path.exists(lib_dir) and os.listdir(lib_dir):
                lib_temp_dir = os.path.join(temp_dir, "lib")
                os.makedirs(lib_temp_dir)
                
                # 复制所有 lib 内容
                for item in os.listdir(lib_dir):
                    if item.startswith('.') or item == '__pycache__':
                        continue
                    source_path = os.path.join(lib_dir, item)
                    dest_path = os.path.join(lib_temp_dir, item)
                    
                    if os.path.isdir(source_path):
                        shutil.copytree(source_path, dest_path)
                    else:
                        shutil.copy2(source_path, dest_path)
                    has_lib = True
            
            # 3. 复制插件数据（如果存在）
            from src.utils.path_utils import get_data_directory
            data_dir = get_data_directory()
            has_data = False

            # 统一规范：插件数据目录名 = file_name（插件文件名）
            # 这样导出和导入时保持一致
            plugin_data_dir = os.path.join(data_dir, plugin_file_name)
            
            if os.path.exists(plugin_data_dir) and os.path.isdir(plugin_data_dir):
                logger.info(f"找到配置数据目录: {plugin_data_dir}")
                data_temp_dir = os.path.join(temp_dir, "data")
                shutil.copytree(plugin_data_dir, data_temp_dir)
                has_data = True
            else:
                logger.info(f"未找到插件配置数据: {plugin_data_dir}")

            # 4. 生成 manifest.json
            manifest = {
                "plugin_name": plugin_name,
                "file_name": plugin_file_name,
                "version": "1.0",
                "export_date": datetime.now().isoformat(),
                "has_lib": has_lib,
                "has_data": has_data,
                "description": f"插件: {plugin_name}"
            }
            
            with open(os.path.join(temp_dir, "manifest.json"), "w", encoding="utf-8") as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)
            
            # 5. 打包为 ZIP
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    # 过滤系统文件
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                    
                    for file in files:
                        if file.startswith('.'):
                            continue
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
            
            msg_box = QMessageBox(window)
            msg_box.setWindowTitle("导出成功")

            # 构建详细信息
            export_info = []
            export_info.append(f"插件 '{plugin_name}' 已成功导出至：")
            export_info.append(export_path)
            export_info.append("")
            export_info.append("导出内容：")
            export_info.append("✓ 插件文件")
            
            if has_lib:
                export_info.append("✓ 依赖库 (lib)")
            else:
                export_info.append("✗ 依赖库 (无)")
            
            if has_data:
                export_info.append("✓ 配置数据 (data)")
            else:
                export_info.append("✗ 配置数据 (无)")
            
            msg_box.setText("\n".join(export_info))
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
            msg_box.exec()
            
    except Exception as e:
        msg_box = QMessageBox(window)
        msg_box.setWindowTitle("导出失败")
        msg_box.setText(f"导出插件失败: {e}")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
        msg_box.exec()
        logger.error(f"导出插件 {plugin_name} 失败: {e}")
        logger.error(traceback.format_exc())


def _refresh_plugins(window):
    """刷新插件列表"""
    # 关键修复:清除 Python 模块缓存，确保重新导入时能找到新的依赖
    # 删除所有已加载的插件模块和相关依赖模块，允许它们重新导入
    import importlib
    import importlib.util
    plugin_modules_to_remove = []
    dependency_modules_to_remove = []
    
    # 步骤 1: 删除 plugins 目录下所有 .pyc 文件，防止字节码缓存干扰
    plugin_dir = get_plugin_directory()
    try:
        for root, dirs, files in os.walk(plugin_dir):
            for file in files:
                if file.endswith('.pyc'):
                    pyc_path = os.path.join(root, file)
                    try:
                        os.remove(pyc_path)
                        logger.info(f"[刷新插件] 删除字节码缓存: {pyc_path}")
                    except Exception as e:
                        logger.warning(f"[刷新插件] 删除字节码失败: {pyc_path} - {e}")
            # 删除 __pycache__ 目录
            if '__pycache__' in dirs:
                pycache_dir = os.path.join(root, '__pycache__')
                try:
                    shutil.rmtree(pycache_dir)
                    logger.info(f"[刷新插件] 删除缓存目录: {pycache_dir}")
                except Exception as e:
                    logger.warning(f"[刷新插件] 删除缓存目录失败: {pycache_dir} - {e}")
    except Exception as e:
        logger.error(f"[刷新插件] 清理字节码缓存失败: {e}")
    
    # 步骤 2: 清除 sys.modules 中的模块缓存
    
    # 关键修复：由于 PluginLoader 使用 spec_from_file_location 动态加载
    # 插件模块可能不在 sys.modules 中，或者使用临时模块名
    # 因此我们采用更激进的策略：删除所有可能相关的模块
    for module_name in list(sys.modules.keys()):
        # 删除所有插件模块（更宽泛的匹配规则）
        # 匹配包含 plugin、speech_draft、uuid_generator 等关键词的模块
        # 但是！不能删除 src.plugins.base_plugin 和 src.plugins.plugin_loader，否则无法加载插件
        if ('speech_draft' in module_name.lower() or 
            'uuid_generator' in module_name.lower() or
            (module_name.endswith('_plugin') and not module_name.startswith('src.plugins.')) or
            # 匹配 plugins 目录下动态加载的模块（可能没有固定前缀）
            (module_name.startswith('__') and 'plugin' in module_name.lower())):
            plugin_modules_to_remove.append(module_name)
        # 删除可能失败的依赖模块及其子模块，让它们重新尝试导入
        # 清除 openai.*, requests.*, docx.* 等所有子模块
        elif (module_name.startswith('openai') or 
              module_name.startswith('requests') or 
              module_name.startswith('docx') or
              module_name == 'openai' or
              module_name == 'requests' or
              module_name == 'docx'):
            dependency_modules_to_remove.append(module_name)
    
    # 步骤 3: 强制使 importlib 的缓存失效
    importlib.invalidate_caches()
    
    # 清除插件模块
    for module_name in plugin_modules_to_remove:
        del sys.modules[module_name]
    
    # 清除依赖模块（如果之前导入失败）
    for module_name in dependency_modules_to_remove:
        del sys.modules[module_name]
    
    # 清空工具列表（保留首页）
    items_to_remove = []
    for i in range(window.tool_list_widget.topLevelItemCount()):
        item = window.tool_list_widget.topLevelItem(i)
        item_data = item.data(0, Qt.ItemDataRole.UserRole)
        # 保留首页，删除其他所有项（插件和文件夹）
        if not (item_data and item_data.get("type") == "home"):
            items_to_remove.append(i)
    
    # 从后往前删除，避免索引变化
    for i in reversed(items_to_remove):
        window.tool_list_widget.takeTopLevelItem(i)
    
    # 清除堆栈部件中的所有工具页面（保留欢迎页面）
    for i in range(window.tool_stack_widget.count() - 1, 0, -1):
        widget = window.tool_stack_widget.widget(i)
        window.tool_stack_widget.removeWidget(widget)
        widget.deleteLater()
    
    # 清空插件映射
    window.plugin_widget_map.clear()
    
    # 重新加载插件
    try:
        load_plugins(window)
    except Exception as e:
        logger.error(f"刷新插件失败: {e}")
        logger.error(traceback.format_exc())
    
    # 选择首页
    home_item = window.tool_list_widget.topLevelItem(0)
    if home_item:
        window.tool_list_widget.setCurrentItem(home_item)


def _import_xpkg_plugin(window, file_path):
    """导入 .xpkg 插件包"""
    try:
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 1. 解压 .xpkg 文件
            with zipfile.ZipFile(file_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # 2. 读取 manifest.json
            manifest_path = os.path.join(temp_dir, "manifest.json")
            if not os.path.exists(manifest_path):
                raise Exception("无效的插件包：缺少 manifest.json 文件")
            
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            
            plugin_name = manifest.get("plugin_name")
            file_name = manifest.get("file_name")
            has_lib = manifest.get("has_lib", False)
            has_data = manifest.get("has_data", False)
            
            if not plugin_name or not file_name:
                raise Exception("无效的插件包：manifest.json 缺少必要信息")
            
            # 3. 复制插件文件
            plugin_dir = get_plugin_directory()
            plugin_source = os.path.join(temp_dir, "plugin.py")
            plugin_dest = os.path.join(plugin_dir, f"{file_name}.py")
            
            if not os.path.exists(plugin_source):
                raise Exception("无效的插件包：缺少插件文件")
            
            # 检查插件文件是否已存在
            if os.path.exists(plugin_dest):
                msg_box = QMessageBox(window)
                msg_box.setWindowTitle("文件已存在")
                msg_box.setText(f"插件文件 '{file_name}.py' 已存在，是否覆盖？")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                msg_box.setDefaultButton(QMessageBox.StandardButton.No)
                msg_box.button(QMessageBox.StandardButton.Yes).setText("确定")
                msg_box.button(QMessageBox.StandardButton.No).setText("取消")
                
                reply = msg_box.exec()
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            # 复制插件文件
            shutil.copy2(plugin_source, plugin_dest)
            logger.info(f"已导入插件文件: {plugin_dest}")
            
            # 4. 复制 lib 依赖（如果存在）
            if has_lib:
                lib_dir = get_lib_directory()
                lib_source = os.path.join(temp_dir, "lib")
                
                if os.path.exists(lib_source):
                    # 确保 lib 目录存在
                    if not os.path.exists(lib_dir):
                        os.makedirs(lib_dir)
                        logger.info(f"[导入插件] 创建 lib 目录: {lib_dir}")
                    
                    # 复制所有 lib 内容
                    copied_count = 0
                    for item in os.listdir(lib_source):
                        if item.startswith('.') or item == '__pycache__':
                            continue
                        source_path = os.path.join(lib_source, item)
                        dest_path = os.path.join(lib_dir, item)
                        
                        if os.path.isdir(source_path):
                            if os.path.exists(dest_path):
                                shutil.rmtree(dest_path)
                            shutil.copytree(source_path, dest_path)
                        else:
                            shutil.copy2(source_path, dest_path)
                        copied_count += 1
                    
                    logger.info(f"已导入 {copied_count} 个依赖项到 lib 目录")
            
            # 5. 复制插件数据（如果存在）
            if has_data:
                from src.utils.path_utils import get_data_directory
                data_dir = get_data_directory()
                data_source = os.path.join(temp_dir, "data")
                
                if os.path.exists(data_source):
                    # 确保 data 目录存在
                    if not os.path.exists(data_dir):
                        os.makedirs(data_dir)
                    
                    # 创建插件数据目录
                    plugin_data_dir = os.path.join(data_dir, file_name)
                    if os.path.exists(plugin_data_dir):
                        shutil.rmtree(plugin_data_dir)
                    shutil.copytree(data_source, plugin_data_dir)
                    
                    logger.info(f"已导入插件数据到: {plugin_data_dir}")
            
            # 6. 删除该插件的关联关系（使其回到根目录）
            with Database() as db:
                db.plugin_association_manager.remove_plugin_from_folder(plugin_name)
            
            # 7. 刷新插件
            _refresh_plugins(window)
            
            # 显示成功消息
            msg_box = QMessageBox(window)
            msg_box.setWindowTitle("导入成功")
            msg_text = f"插件 '{plugin_name}' 已成功导入。"
            info_parts = []
            if has_lib:
                info_parts.append("包含依赖")
            if has_data:
                info_parts.append("包含插件数据")
            if info_parts:
                msg_box.setInformativeText("\n".join(info_parts))
            msg_box.setText(msg_text)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
            msg_box.exec()
            
    except Exception as e:
        msg_box = QMessageBox(window)
        msg_box.setWindowTitle("导入失败")
        msg_box.setText(f"导入插件包失败: {e}")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.button(QMessageBox.StandardButton.Ok).setText("确定")
        msg_box.exec()
        logger.error(f"导入 .xpkg 插件失败: {e}")
        logger.error(traceback.format_exc())


def _find_plugin_file(plugin_dir, plugin_name):
    """通过插件名查找插件文件"""
    import importlib.util
    from src.plugins.base_plugin import BasePlugin
    
    for item in os.listdir(plugin_dir):
        if not item.startswith("__") and item.endswith(".py"):
            try:
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
                            if plugin_instance.name == plugin_name:
                                return module_name
            except Exception as e:
                logger.error(f"检查插件文件 {item} 失败: {e}")
    
    return None
