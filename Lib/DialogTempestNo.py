from PyQt4.QtCore import *
from PyQt4 import QtGui,uic,QtCore
import configparser

class DialogTempestNo(QtGui.QDialog):

    def __init__(self) :
        #global model
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("DialogTempestNo.ui", self)
        self.centerOnScreen()
        self.ui.BtnOk.clicked.connect(self.onBtnOk)
        self.ui.BtnCancel.clicked.connect(self.onBtnCancel)
        self.ui.show()
        self.tempestNo = ""
        self.ret = False

    def onBtnCancel(self):
        #print('onBtnCancel')
        self.ret = False
        self.tempestNo = ''
        self.close()
        pass

    def onBtnOk(self):
        self.ret = True

        self.tempestNo = self.ui.lineEdit.text()
        self.close()


    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))




