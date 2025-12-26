from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QTextEdit, QLabel, QMessageBox
from .base_tool import BaseTool
from .huitoukan_tool import WorkOrderBackTool

class WorkOrderTool(BaseTool):
    def __init__(self):
        super().__init__("回头看工单", "用于处理回头看工单的状态更新")
        
        # 初始化工具UI
        self.init_ui()
        
        # 初始化工单处理工具
        self.work_order_back_tool = WorkOrderBackTool(
            host="112.6.205.8",
            port=35403,
            user="root",
            password="$927%Nauk6C5@*J4qP",
            database="jiaoxinban"
        )
    
    def init_ui(self):
        # 创建状态选择下拉框
        status_layout = QHBoxLayout()
        status_label = QLabel("选择状态：")
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            "移到回头看待处理",
            "青岛已通过(弃用)",
            "青岛通过移出待处理",
            "移出回头看",
            "设置青岛已通过"
        ])
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_combo)
        self.layout.addLayout(status_layout)
        
        # 创建工单输入区域
        self.work_order_text = QTextEdit()
        self.work_order_text.setPlaceholderText("请输入工单，一行一个工单号")
        self.work_order_text.setMinimumHeight(200)
        self.layout.addWidget(self.work_order_text)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 创建更新按钮
        self.update_button = QPushButton("更新")
        self.update_button.clicked.connect(self.update_work_orders)
        button_layout.addWidget(self.update_button)
        
        # 创建重置按钮
        self.reset_button = QPushButton("重置")
        self.reset_button.clicked.connect(self.reset_work_orders)
        button_layout.addWidget(self.reset_button)
        
        self.layout.addLayout(button_layout)
    
    def update_work_orders(self):
        # 获取选择的状态
        selected_status = self.status_combo.currentIndex() + 1  # 状态从1开始
        
        # 获取输入的工单
        work_order_text = self.work_order_text.toPlainText()
        work_order_list = [wo.strip() for wo in work_order_text.splitlines() if wo.strip()]
        
        if not work_order_list:
            QMessageBox.warning(self, "警告", "请输入至少一个工单号")
            return
        
        try:
            # 根据选择的状态调用相应的方法
            if selected_status == 1:
                # 移到回头看待处理
                result = self.work_order_back_tool.huitoukan_to_handle(work_order_list)
            elif selected_status == 2:
                # 青岛已通过
                result = self.work_order_back_tool.huitoukan_qd_pass(work_order_list)
            elif selected_status == 3:
                # 青岛通过移出待处理
                result = self.work_order_back_tool.huitoukan_pass_remove(work_order_list)
            elif selected_status == 4:
                # 移出回头看
                result = self.work_order_back_tool.huitoukan_remove_2(work_order_list)
            elif selected_status == 5:
                # 青岛待审核设置青岛已通过
                result = self.work_order_back_tool.huitoukan_qd_pass2(work_order_list)
            else:
                QMessageBox.warning(self, "警告", "无效的状态选择")
                return
            
            # 处理结果
            if result["status"] == "success":
                QMessageBox.information(self, "成功", "工单状态更新成功")
            else:
                QMessageBox.critical(self, "错误", f"工单状态更新失败：{result['message']}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理工单时发生异常：{str(e)}")
    
    def reset_work_orders(self):
        # 清空输入区域
        self.work_order_text.clear()
        # 重置状态选择
        self.status_combo.setCurrentIndex(0)
