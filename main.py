import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show_sessions()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()