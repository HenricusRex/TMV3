__author__ = 'Heinz'
from NeedfullThings import *
from DB_Handler_TPL3 import *
from DB_Handler_TDS3 import DatasetPlan
from Workbench import  Ticket
from datetime import datetime
from Protocol import Protocol
import configparser
logging.basicConfig(filename="TMV3log.txt",
                    level=logging.error,
                    format='%(asctime)s %(message)s',
                    datefmt='%m.%d.%Y %I:%M:%S')
class ImportZZ(QtGui.QDialog):
    def __init__(self, parent=None):
        super(QtGui.QDialog, self).__init__(parent)

        self.ui = uic.loadUi("ImportZZ.ui", self)

        self.centerOnScreen()
        self.inputFile = ""
        self.config = configparser.ConfigParser()
        self.config.read('TMV3.ini')
        self.signals = Signal()
        self.data = 0
        self.config = configparser.ConfigParser()
        self.config.read('TMV3.ini')
        self.workBenchDB = self.config['DataBases']['workbench']
        self.ui.BtnOk.clicked.connect(self.onBtnOk)
        self.ui.BtnCancel.clicked.connect(self.onBtnCancel)
        self.ui.BtnDir.clicked.connect(self.onBtnDir)
        self.dialogReturn = False
        self.dialogReturnText = ''


        pass
    def showDialog(self):
        self.showNormal()

    def onBtnOk(self):

        QtGui.QApplication.setOverrideCursor((QtGui.QCursor(Qt.WaitCursor)))
        fileTDS = Tpl3Files(self.workBenchDB,0)
        fileTDS.title = self.ui.leTitle.text()
        fileTDS.version = self.ui.leVersion.text()
        fileTDS.type = "Testplan"
        _d = datetime.now()
        _dA = datetime(_d.year,_d.month,_d.day,_d.hour,_d.minute,_d.second).isoformat(' ')
        fileTDS.data = self.data
        fileTDS.date = _dA
        ret = fileTDS.read(fileTDS.title,fileTDS.version)
        if ret:
            QtGui.QApplication.restoreOverrideCursor()
            _s = "Testplan {0} version {1} already exists".format(fileTDS.title,fileTDS.version)
            QtGui.QMessageBox.information(self, 'TMV3', _s, QtGui.QMessageBox.Ok)
            self.dialogReturn = False
            return
        ret = fileTDS.add()
        QtGui.QApplication.restoreOverrideCursor()

        if ret == 0:
            _s = 'unable to import TDS'
            QtGui.QMessageBox.information(self, 'TMV3', _s, QtGui.QMessageBox.Ok)
            self.dialogReturn = False
            return
        _s = 'TDS successfully imported'
        QtGui.QMessageBox.information(self, 'TMV3', _s, QtGui.QMessageBox.Ok)
        self.config['Current']['current_planid_zz'] = str(ret)
        with open('TMV3.ini','w')as configfile:
            self.config.write(configfile)

        self.dialogReturn = True
        self.close()

    def onBtnCancel(self):
        self.dialogReturn = False
        self.close()

    def onBtnDir(self):
        _ret = QtGui.QFileDialog.getOpenFileName(self, "Open Zone Approval Testplan TDS3", "", "TDS3 (*.TDS3)")
        if (_ret == ""): return
        self.ui.lePath.setText(_ret)
        self.loadTDS(_ret)

    def loadTDS(self,path):
        QtGui.QApplication.setOverrideCursor((QtGui.QCursor(Qt.WaitCursor)))
        try:
            with open(path, 'rb') as f:
                self.data = f.read()
                tds = DatasetPlan(path)
                tds.read()
                self.ui.leTitle.setText(tds.title)
                self.ui.leVersion.setText(tds.version)
                QtGui.QApplication.restoreOverrideCursor()
        except Exception as _err:
            QtGui.QApplication.restoreOverrideCursor()
            _s  = "unable to load TDS {0}, ".format(_err)
            QtGui.QMessageBox.information(self, 'TMV3', _s, QtGui.QMessageBox.Ok)
            logging.exception(_err)
            return 0



    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))