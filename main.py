from PyQt5.QtWidgets import QApplication
from mainwindow import MainWindow
import os
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()  # Create an instance of MainWindow (the class you defined above)
    main_window.show()
    sys.exit(app.exec_())