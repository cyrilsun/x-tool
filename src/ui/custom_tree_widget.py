from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTreeWidget


class CustomTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self._dragged_item = None
        self._old_parent = None
        self._old_index = -1
    
    def startDrag(self, supportedActions):
        """开始拖拽时保存被拖拽的项"""
        self._dragged_item = self.currentItem()
        if self._dragged_item:
            self._old_parent = self._dragged_item.parent()
            if self._old_parent:
                self._old_index = self._old_parent.indexOfChild(self._dragged_item)
            else:
                self._old_index = self.indexOfTopLevelItem(self._dragged_item)
        super().startDrag(supportedActions)
    
    def dropEvent(self, event):
        """处理放置事件"""
        from src.utils.logger import logger
        logger.info(f"[dropEvent] 开始处理放置事件, _dragged_item={self._dragged_item}")
        
        # 调用父类的dropEvent来处理实际的移动
        super().dropEvent(event)
        
        # 获取移动后的信息
        if self._dragged_item:
            moved_item = self._dragged_item
            new_parent = moved_item.parent()
            if new_parent:
                new_index = new_parent.indexOfChild(moved_item)
            else:
                new_index = self.indexOfTopLevelItem(moved_item)
            
            # 通知父窗口保存排序顺序和文件夹关联
            if hasattr(self.parent_window, 'on_item_moved'):
                logger.info(f"[dropEvent] 调用 on_item_moved: moved_item={moved_item.text(0)}, new_parent={new_parent.text(0) if new_parent else None}")
                self.parent_window.on_item_moved(
                    moved_item, 
                    self._old_parent, 
                    self._old_index, 
                    new_parent, 
                    new_index
                )
            else:
                logger.warning(f"[dropEvent] parent_window 没有 on_item_moved 方法")
        else:
            logger.warning(f"[dropEvent] _dragged_item 为空，不处理")
        
        # 重置状态
        self._dragged_item = None
        self._old_parent = None
        self._old_index = -1