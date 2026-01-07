import sys

from PyQt6.QtWidgets import QApplication

from src.tools.work_order_tool import WorkOrderTool
from src.ui.main_window import MainWindow

if __name__ == "__main__":
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 创建主窗口实例
    window = MainWindow()
    
    # 添加工具
    # window.add_tool("计算器", CalculatorTool())
    # window.add_tool("笔记", NoteTool())
    
    # 添加回头看工单工具并设置样式
    work_order_tool = WorkOrderTool()
    work_order_tool.setStyleSheet("""
        QWidget {
            font-size: 18px;
        }
        QGroupBox {
            font-size: 18px;
            font-weight: bold;
        }
        QLabel {
            font-size: 18px;
        }
        QComboBox {
            font-size: 18px;
            padding: 8px;
        }
        QTextEdit {
            font-size: 18px;
        }
        QPushButton {
            font-size: 18px;
            font-weight: bold;
        }
    """)
    window.add_tool("回头看工单", work_order_tool)
    
    # 显示主窗口
    window.show()
    
    # 运行应用程序事件循环
    sys.exit(app.exec())
