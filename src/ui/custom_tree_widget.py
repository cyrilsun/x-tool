from PyQt6.QtWidgets import QTreeWidget


class CustomTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
    
    def dropEvent(self, event):
        # 获取拖拽的项目
        dragged_item = self.currentItem()
        
        # 保存移动前的信息
        old_parent = dragged_item.parent()
        if old_parent:
            old_index = old_parent.indexOfChild(dragged_item)
        else:
            old_index = self.indexOfTopLevelItem(dragged_item)
        
        # 调用父类的dropEvent来处理实际的移动
        super().dropEvent(event)
        
        # 保存移动后的信息
        moved_item = dragged_item  # 移动后项目引用不变
        new_parent = moved_item.parent()
        if new_parent:
            new_index = new_parent.indexOfChild(moved_item)
        else:
            new_index = self.indexOfTopLevelItem(moved_item)
        
        # 通知父窗口保存排序顺序和文件夹关联
        if hasattr(self.parent_window, 'on_item_moved'):
            self.parent_window.on_item_moved(moved_item, old_parent, old_index, new_parent, new_index)