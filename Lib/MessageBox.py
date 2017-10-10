import sys
from PyQt4 import QtGui  # imports the QtGui sub-module from the PyQt4 module
from PyQt4.QtGui import QMessageBox  # imports the QMessageBox class from the QtGui sub-module

# creates the application and takes arguments from the command line
import sys
from PyQt4 import QtGui


class MessageBox(QtGui.QWidget):
    def __init__(self):
        super(MessageBox, self).__init__()

        self.initUI()

    def initUI(self):

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Message box')
        self.show()

    def closeEvent(self, event):

        reply = QtGui.QMessageBox.question(self, 'Message',
                                           "Are you sure to quit?", QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

