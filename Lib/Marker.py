__author__ = 'heinz'


from PyQt4 import uic,QtGui

class MarkerText(QtGui.QDialog):


    def __init__(self,parent = None):
        #global model
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("../Lib/Marker.ui", self)
        self.centerOnScreen()
        self.ret = False
        self.text = ''

        #Buttons
        self.ui.BtnOk.clicked.connect(self.onBtnOk)
        self.ui.BtnCancel.clicked.connect(self.onBtnCancel)

    def onBtnOk(self):
        self.ret = True
        self.text = self.ui.lineEdit.text()
        self.close()

    def onBtnCancel(self):
        self.ret = False
        self.text = ""
        self.close()


    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

