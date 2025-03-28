# 在main.py顶部添加路径处理
import sys
import os
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

def resource_path(relative_path):
    """获取打包后的资源绝对路径"""
    try:
        # PyInstaller创建的临时文件夹路径
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
    app = QApplication(sys.argv)
    
    # 加载样式表
    with open(resource_path("resources/style.qss"), "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()