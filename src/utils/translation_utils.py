import sys
import os

from PyQt6.QtCore import QTranslator, QLocale, QCoreApplication
from src.utils.logger import logger


def setup_translation(app):
    """
    设置应用程序的翻译功能
    
    Args:
        app: QApplication实例
        
    Returns:
        bool: 是否成功加载翻译文件
    """
    # 设置应用程序语言环境为中文
    locale = QLocale(QLocale.Language.Chinese, QLocale.Country.China)
    QLocale.setDefault(locale)
    
    # 尝试获取翻译文件路径（适配开发环境和打包环境）
    qt_translations_path = None
    
    if getattr(sys, 'frozen', False):
        # 打包后的环境：使用 _MEIPASS 或相对于可执行文件的 Resources 目录
        if hasattr(sys, '_MEIPASS'):
            qt_translations_path = os.path.join(sys._MEIPASS, 'translations')
        else:
            # 兼容 macOS .app 结构
            base_path = os.path.dirname(sys.executable)
            qt_translations_path = os.path.join(os.path.dirname(base_path), 'Resources', 'translations')
        
        logger.debug(f"打包环境翻译文件路径: {qt_translations_path}")
    else:
        # 开发环境
        # 尝试从PyQt6安装目录获取翻译文件
        try:
            import PyQt6
            pyqt_path = os.path.dirname(PyQt6.__file__)
            qt_translations_path = os.path.join(pyqt_path, 'Qt6', 'translations')
            logger.debug(f"开发环境PyQt6路径: {pyqt_path}")
            logger.debug(f"开发环境翻译文件路径: {qt_translations_path}")
        except Exception as e:
            logger.warning(f"无法获取PyQt6安装路径: {e}")
    
    # 检查翻译文件路径是否存在
    if qt_translations_path:
        if os.path.exists(qt_translations_path):
            logger.debug(f"翻译文件目录存在: {qt_translations_path}")
            # 查看目录下的文件
            try:
                files = os.listdir(qt_translations_path)
                qm_files = [f for f in files if f.endswith('.qm')]
                logger.debug(f"翻译文件列表: {qm_files[:10]}")  # 只显示前10个文件
            except Exception as e:
                logger.warning(f"无法列出翻译文件目录: {e}")
        else:
            logger.warning(f"翻译文件目录不存在: {qt_translations_path}")
    
    # 尝试加载翻译文件
    if qt_translations_path and os.path.exists(qt_translations_path):
        app._translators = []
        
        # 定义需要加载的翻译文件列表
        # qt_zh_CN 包含大部分翻译，qtbase_zh_CN 包含基础组件翻译
        translators_to_load = ["qt_zh_CN", "qtbase_zh_CN"]
        
        for t_name in translators_to_load:
            translator = QTranslator()
            if translator.load(t_name, qt_translations_path):
                app.installTranslator(translator)
                app._translators.append(translator)
                logger.debug(f"成功加载翻译文件: {t_name}.qm")
                translation_loaded = True
            else:
                logger.warning(f"未能加载翻译文件: {t_name}.qm")
    
    # 确保应用程序菜单文本已更新
    if translation_loaded:
        # 强制更新所有翻译
        QCoreApplication.instance().setProperty("retranslate", True)
        logger.debug("已强制更新应用程序翻译")
    
    return translation_loaded
