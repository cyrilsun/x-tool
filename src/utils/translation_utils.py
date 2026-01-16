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
        # 打包后的环境
        base_path = os.path.dirname(sys.executable)
        qt_translations_path = os.path.join(base_path, 'translations')
        logger.info(f"打包环境翻译文件路径: {qt_translations_path}")
    else:
        # 开发环境
        # 尝试从PyQt6安装目录获取翻译文件
        try:
            import PyQt6
            pyqt_path = os.path.dirname(PyQt6.__file__)
            qt_translations_path = os.path.join(pyqt_path, 'Qt6', 'translations')
            logger.info(f"开发环境PyQt6路径: {pyqt_path}")
            logger.info(f"开发环境翻译文件路径: {qt_translations_path}")
        except Exception as e:
            logger.warning(f"无法获取PyQt6安装路径: {e}")
    
    # 检查翻译文件路径是否存在
    if qt_translations_path:
        if os.path.exists(qt_translations_path):
            logger.info(f"翻译文件目录存在: {qt_translations_path}")
            # 查看目录下的文件
            try:
                files = os.listdir(qt_translations_path)
                qm_files = [f for f in files if f.endswith('.qm')]
                logger.info(f"翻译文件列表: {qm_files[:10]}")  # 只显示前10个文件
            except Exception as e:
                logger.warning(f"无法列出翻译文件目录: {e}")
        else:
            logger.warning(f"翻译文件目录不存在: {qt_translations_path}")
    
    # 尝试加载翻译文件，使用更灵活的方式
    translation_loaded = False
    
    if qt_translations_path and os.path.exists(qt_translations_path):
        # 创建翻译器实例并存储到app对象中，防止被垃圾回收
        app._translators = []
        
        # 尝试加载qt_zh_CN.qm
        translator = QTranslator()
        if translator.load("qt_zh_CN", qt_translations_path):
            app.installTranslator(translator)
            app._translators.append(translator)
            logger.info("已加载qt_zh_CN.qm翻译文件")
            translation_loaded = True
        else:
            logger.warning("未能加载qt_zh_CN.qm翻译文件")
            
            # 尝试加载qtbase_zh_CN.qm（可能需要同时加载这两个文件）
            translator_base = QTranslator()
            if translator_base.load("qtbase_zh_CN", qt_translations_path):
                app.installTranslator(translator_base)
                app._translators.append(translator_base)
                logger.info("已加载qtbase_zh_CN.qm翻译文件")
                translation_loaded = True
            else:
                logger.warning("未能加载qtbase_zh_CN.qm翻译文件")
    
    # 确保应用程序菜单文本已更新
    if translation_loaded:
        # 强制更新所有翻译
        QCoreApplication.instance().setProperty("retranslate", True)
        logger.info("已强制更新应用程序翻译")
    
    return translation_loaded
