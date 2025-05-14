import sys
from src.key_monitor import MainWindow
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(500, 200)
    window.show()  # 启动时不显示主窗口
    sys.exit(app.exec_()) 