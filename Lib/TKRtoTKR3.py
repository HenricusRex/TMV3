__author__ = 'Heinz'

from PyQt4 import uic, QtGui, QtCore
from DB_Handler_TPL3 import Tpl3Lines
from Workbench import Ticket
from pydispatch import dispatcher
from NeedfullThings import Signal
import pypyodbc
import shutil
import configparser
import os
class TKRtoTKR3(QtGui.QDialog):
    def __init__(self, parent=None):
        super(QtGui.QDialog, self).__init__(parent)
        self.ui = uic.loadUi("TKRtoTKR3.ui", self)
        self.centerOnScreen()
        self.inputFile = ""
        self.outputFile = ""
        self.tkrNo = 0
        self.tkrCount = 0
        self.valueLists = []
        self.config = configparser.ConfigParser()
        self.config.read('TMV3.ini')
        _ret = self.config['Antenna']['AntennaList']
        self.AntennaList = _ret.split('\n')
        _ret = self.config['Cable']['CableList']
        self.CableList = _ret.split('\n')
        self.saveFlag = True
        self.ticket = Ticket()
        self.signals = Signal()

        self.ui.BtnFile.clicked.connect(self.loadTKR)
        self.ui.BtnDel.clicked.connect(self.onBtnDel)
        self.ui.BtnSave.clicked.connect(self.onBtnSave)
        self.ui.BtnOk.clicked.connect(self.onBtnOk)
        self.ui.BtnCancel.clicked.connect(self.onBtnCancel)
        self.ui.tableWidget.cellChanged.connect(self.onTableTouch)

        pass

    def onTableTouch(self):
        self.saveFlag = False
        pass

    def onBtnOk(self):
        if self.saveFlag:
            self.close()
            return

        _s = 'Please save before Ok or use Cancel'
        QtGui.QMessageBox.information(self, 'TMV3', _s, QtGui.QMessageBox.Ok)
    def onBtnCancel(self):
        self.close()

    def onBtnDel(self):
        _row = self.ui.tableWidget.currentRow()
        self.ui.tableWidget.removeRow(_row)
        self.valueLists.pop(_row)
        self.tkrCount -= 1
        pass

    def onBtnSave(self):
        _rows = self.ui.tableWidget.rowCount()
        for _row in range (_rows):
            _cb = self.ui.tableWidget.cellWidget(_row,2)
            _ret = str(_cb.currentText())
            if _ret == "":
                QtGui.QMessageBox.information(self, 'TMV3', "you have to set the new Titles", QtGui.QMessageBox.Ok)
                return
            _ret = self.ui.tableWidget.item(_row,3).text()
            if _ret == '?':
                QtGui.QMessageBox.information(self, 'TMV3', "you have to set the Serial Numbers", QtGui.QMessageBox.Ok)
                return
            _cD = self.ui.tableWidget.cellWidget(_row,4)
            _ret = _cD.date()
            if _ret == QtCore.QDate(2000,1,1):
                QtGui.QMessageBox.information(self, 'TMV3', "you have to set the Calibration Dates", QtGui.QMessageBox.Ok)
                return

        try:
            shutil.copy("../Templates/TMV3.TKR3",self.outputFile)
            self.saveTKR3()
        except Exception as _err:
            QtGui.QMessageBox.information(self, 'TMV3', str(_err), QtGui.QMessageBox.Ok)
        return

        self.saveTKR3()
        return

    def saveTKR3(self):

        _line = Tpl3Lines(self.outputFile,0)

        _rows = self.ui.tableWidget.rowCount()
        _listCount = 0
        for _row in range (_rows):
            _line.type = self.ui.tableWidget.item(_row,0).text()
            _cb = self.ui.tableWidget.cellWidget(_row,2)
            _line.title = str(_cb.currentText())
            _line.version = self.ui.tableWidget.item(_row,3).text()
            _cD = self.ui.tableWidget.cellWidget(_row,4)
            _line.date = _cD.date().toPyDate()
            _line._comment = self.ui.tableWidget.item(_row,5).text()
            _line.data_xy = self.valueLists[_listCount]
            _listCount += 1
            _line.add()

        _s = "new  " + self.outputFile + '  created'
        QtGui.QMessageBox.information(self, 'TMV3', _s, QtGui.QMessageBox.Ok)
        self.saveFlag = True
        self.saveFlag = True


    def loadTKR(self):

        _ret = QtGui.QFileDialog.getOpenFileName(self, "Open TKR", "I:\Datensätze\Wirtz", "TKR (*.Tkr)")
        if (_ret == ""): return
        self.ui.lineEdit.setText(_ret)

        self.inputFile = _ret
        self.outputFile = self.inputFile+'3'
        if os.path.isfile(self.outputFile):
            _s = "new TKR3  " + self.outputFile + "  already exists"
            QtGui.QMessageBox.information(self, 'TMV3', _s, QtGui.QMessageBox.Ok)
            return

        _conI = pypyodbc.win_connect_mdb(self.inputFile)
        _curI = _conI.cursor()
        _curI.execute('SELECT [tTitle],[tComment],[lAntennenKorrID] from AntennenKorr')
        _ret = _curI.fetchall()
        print(_ret)
        self.tkrCount = 0
        for _f in _ret:
            self.addItem(self.tkrCount,"Antenna",_f[0],_f[1])
            _curI.execute('SELECT [dXValue],[dYValue] from AntennenKorrValues WHERE [lAntennenKorrID]={0}'.format(str(_f[2])))
            _list = _curI.fetchall()
            self.valueLists.append(_list)
            self.tkrCount +=1

            pass

        _curI.execute('SELECT [tTitle],[tComment],[lKabelKorrID] from KabelKorr')
        _ret = _curI.fetchall()
        for _f in _ret:
            self.addItem(self.tkrCount,"Cable",_f[0],_f[1])
            _curI.execute('SELECT [dXValue],[dYValue] from KabelKorrValues WHERE [lKabelKorrID]={0}'.format(str(_f[2])))
            _list = _curI.fetchall()
            self.valueLists.append(_list)
            self.tkrCount +=1
            pass

        _curI.execute('SELECT [tTitle],[tComment],[lAdapterKorrID] from AdapterKorr')
        _ret = _curI.fetchall()

        for _f in _ret:
            self.addItem(self.tkrCount,"Adapter",_f[0],_f[1])
            _curI.execute('SELECT [dXValue],[dYValue] from AdapterKorrValues WHERE [lAdapterKorrID]={0}'.format(str(_f[2])))
            _list = _curI.fetchall()
            self.valueLists.append(_list)
            self.tkrCount +=1
            pass

        self.saveFlag = True

    def addItem(self,row,text1,text2,text3):
        _item1 = QtGui.QTableWidgetItem(text1)
        _item2 = QtGui.QTableWidgetItem(text2)
        _item3 = QtGui.QTableWidgetItem('?')
        _item5 = QtGui.QTableWidgetItem(text3)

        assert isinstance(self.ui.tableWidget,QtGui.QTableWidget)
        self.ui.tableWidget.insertRow(row)
        self.ui.tableWidget.setItem(row,0,_item1)
        self.ui.tableWidget.setItem(row,1,_item2)
        self.ui.tableWidget.setItem(row,3,_item3)
        self.ui.tableWidget.setItem(row,5,_item5)

        _itemC = QtGui.QComboBox()
        if text1 == 'Antenna':
            _itemC.addItems(self.AntennaList)
        if text1 == 'Cable':
            _itemC.addItems(self.CableList)
        self.ui.tableWidget.setCellWidget(row,2,_itemC)

        _itemD = QtGui.QDateEdit()
        self.ui.tableWidget.setCellWidget(row,4,_itemD)


    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))