import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
form_class = uic.loadUiType("./UI/mainUI_by_mainwindow.ui")[0]

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
