from NeedfullThings import *

class EditSQL(QtGui.QDialog):
    signalShowMessage = pyqtSignal(str)

    def __init__(self,selectString):
        #global model
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("EditSQL.ui", self)
        sshFile = "../Templates/darkorange.css"
        with open (sshFile,"r") as fh:
            self.setStyleSheet(fh.read())
        self.centerOnScreen()
        self.ret = 'Cancel'
        self.selString = selectString
        self.ui.BtnApply.clicked.connect(self.onBtnApply)
        self.ui.BtnCancel.clicked.connect(self.onBtnCancel)
        self.ui.BtnOk.clicked.connect(self.onBtnOk)
        self.ui.plainTextEdit.setPlainText(selectString)

    def onBtnApply(self):
        self.ret = 'Apply'
        self.selString = self.ui.plainTextEdit.toPlainText()

        self.close()
        pass

    def onBtnOk(self):
        self.ret = 'Ok'
        self.close()
        pass

    def onBtnCancel(self):
        self.close()
        pass

    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))


