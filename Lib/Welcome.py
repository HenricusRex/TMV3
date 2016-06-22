
from PyQt4 import uic, QtGui, QtCore
import configparser
import sys
import subprocess
import os

class Welcome(QtGui.QMainWindow):
    def __init__(self,parent=None):
        QtGui.QMainWindow.__init__(self)
     #   QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("Welcome.ui", self)
        self.centerOnScreen()
        self.config = configparser.ConfigParser()
        self.config.read('TMV3.ini')

        print(self.config['Welcome']['name'])

     #   self.ui.lineEdit.setText(self.config['Welcome']['lab'])
      #  self.ui.lineEdit_2.setText(self.config['Welcome']['lab'])

        _option = self.config['Welcome']['start_option']
        if _option == '1':
            self.ui.RBtnKMVZ.setChecked(True)
        if _option == '2':
            self.ui.RBtnKMVS.setChecked(True)
        if _option == '3':
            self.ui.RBtnZZ.setChecked(True)
        if _option == '4':
            self.ui.RBtnSZ.setChecked(True)

        self.ui.BtnOk.clicked.connect(self.onBtnOk)
        self.ui.BtnCancel.clicked.connect(self.onBtnCancel)

        pass
    def onBtnOk(self):
        if self.ui.RBtnKMVZ.isChecked():
            self.config['Welcome']['start_option'] = '1'
        if self.ui.RBtnKMVS.isChecked():
            self.config['Welcome']['start_option'] = '2'
        if self.ui.RBtnZZ.isChecked():
            self.config['Welcome']['start_option'] = '3'
        if self.ui.RBtnSZ.isChecked():
            self.config['Welcome']['start_option'] = '4'

        if self.ui.checkBox.isChecked():
            self.config['Welcome']['show_window'] = '0'
        else:
            self.config['Welcome']['show_window'] = '1'

        self.config['Welcome']['name'] = self.ui.lineEdit.text()
        self.config['Welcome']['lab'] = self.ui.lineEdit_2.text()

        with open('TMV3.ini','w')as configfile:
            self.config.write(configfile)

        subprocess.Popen([sys.executable,'Controller.py'],shell=False,close_fds=True)
        sys.exit(1)

    def onBtnCancel(self):
        self.close()

    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

def main():
    app = QtGui.QApplication(sys.argv)
    form = Welcome()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()