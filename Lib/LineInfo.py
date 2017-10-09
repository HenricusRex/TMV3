__author__ = 'heinz'


from PyQt4 import uic,QtGui,Qt

class LineInfo(QtGui.QDialog):


    def __init__(self,title,xy,data,parent=None):
        #global model
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("../Lib/LineInfo.ui", self)

        self.parent=parent
        self.centerOnScreen()
        self.ret = False
        self.ui.lbTitleValue.setText(title)
        self.ui.lbMouseValue.setText(xy)
        self.ui.lbDataValue.setText(data)

        #Buttons
        self.ui.BtnOk.clicked.connect(self.onBtnOk)

    def onBtnOk(self):
        self.close()


    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

