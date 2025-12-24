import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.tools.calculator_tool import CalculatorTool
from src.tools.note_tool import NoteTool

if __name__ == "__main__":
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 创建主窗口实例
    window = MainWindow()
    
    # 添加工具
    window.add_tool("计算器", CalculatorTool())
    window.add_tool("笔记", NoteTool())
    
    # 显示主窗口
    window.show()
    
    # 运行应用程序事件循环
    sys.exit(app.exec())
