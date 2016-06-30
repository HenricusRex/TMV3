__author__ = 'heinz'


from PyQt4 import uic,QtGui,QtCore

class Instruction(QtGui.QDialog):


    def __init__(self,text,parent = None):
        #global model
        QtGui.QDialog.__init__(self,None,QtCore.Qt.WindowStaysOnTopHint)
        self.ui = uic.loadUi("Instruction.ui", self)
     #   self.centerOnScreen()
        self.ret = False
        self.ui.plainTextEdit.setPlainText(text)

        #Buttons
        self.ui.BtnOk.clicked.connect(self.onBtnOk)



    def onBtnOk(self):
        self.close()


    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

