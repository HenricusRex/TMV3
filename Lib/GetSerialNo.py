__author__ = 'heinz'


from PyQt4 import uic,QtGui

class GetSerialNo(QtGui.QDialog):


    def __init__(self):
        #global model
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("GetSerialNo.ui", self)
        self.centerOnScreen()
        self.ret = False
        self.serialNo = ''
        self.modelNo = ''
        self.modelName = ''
        self.userField = ''
        self.comment = ''

        #Buttons
        self.ui.BtnOk.clicked.connect(self.onBtnOk)
        self.ui.BtnCancel.clicked.connect(self.onBtnCancel)

    def fillDialog(self):
        self.ui.leSerialNo.setText(self.serialNo)
        self.ui.leModelNo.setText(self.modelNo)
        self.ui.leModelName.setText(self.modelName)
        self.ui.leUserNo.setText(self.userField)
        self.ui.pteComment.setPlainText(self.comment)

    def onBtnCancel(self):
        #print('onBtnCancel')
        self.ret = False
        self.close()

        pass

    def onBtnOk(self):
        self.ret = True
        self.serialNo = self.ui.leSerialNo.text()
        self.modelNo = self.ui.leModelNo.text()
        self.modelName = self.ui.leModelName.text()
        self.userField = self.ui.leUserNo.text()
        self.comment = self.ui.pteComment.toPlainText()
        self.close()


    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

