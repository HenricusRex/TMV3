__author__ = 'Heinz'

from PyQt4 import uic, QtGui, QtCore
import pypyodbc
import sqlite3
import configparser
import os
class TLMtoTLM3(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("TLMtoTLM3.ui", self)
        self.centerOnScreen()
        self.inputFile = ""
        self.outputFile = ""
        self.tlmNo = 0
        self.tlmCount = 0
        self.valueLists = []
        self.config = configparser.ConfigParser()
        self.config.read('TMV3.ini')
        _ret = self.config['Limit']['LimitList']
        self.LimitList = _ret.split('\n')
        self.saveFlag = True

        self.ui.BtnFile.clicked.connect(self.loadTLM)
        self.ui.BtnDel.clicked.connect(self.onBtnDel)
        self.ui.BtnSave.clicked.connect(self.onBtnSave)
        self.ui.BtnOk.clicked.connect(self.onBtnOk)
        self.ui.BtnCancel.clicked.connect(self.onBtnCancel)
        self.ui.tableWidget.cellChanged.connect(self.onTableTouch)

        pass

    def onTableTouch(self):
        self.saveFlag = False

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
        self.tlmCount -= 1
        pass

    def onBtnSave(self):
        _rows = self.ui.tableWidget.rowCount()
        for _row in range (_rows):
            _ret = self.ui.tableWidget.item(_row,2).text()
            if _ret == '?':
                QtGui.QMessageBox.information(self, 'TMV3', "you have to set the Version", QtGui.QMessageBox.Ok)
                return
            _cD = self.ui.tableWidget.cellWidget(_row,3)
            _ret = _cD.date()
            if _ret == QtCore.QDate(2000,1,1):
                QtGui.QMessageBox.information(self, 'TMV3', "you have to set the Creation Date", QtGui.QMessageBox.Ok)
                return

        self.saveTLM3()
        return
    def saveTLM3(self):
        _conO = sqlite3.connect(self.outputFile)
        _curO = _conO.cursor()
        _curO.execute('CREATE TABLE [Limit] (Title, Version, Date, Comment, DataXY)')
        _title = ''
        _version = ''
        _date = ''
        _comment = ''
        _list = []
        _listCount = 0
        _rows = self.ui.tableWidget.rowCount()
        for _row in range (_rows):
            _cb = self.ui.tableWidget.cellWidget(_row,1)
            _title = str(_cb.currentText())
            _version = self.ui.tableWidget.item(_row,2).text()
            _cD = self.ui.tableWidget.cellWidget(_row,3)
            _date = _cD.date().toPyDate()
            _comment = self.ui.tableWidget.item(_row,4).text()
            _list = self.valueLists[_listCount]
            _curO.execute("INSERT INTO [Limit] (Title,Version,Date,Comment,DataXY) VALUES (?,?,?,?,?)",
                          (str(_title), str(_version), str(_date), str(_comment),str(_list)))
            _listCount += 1
            _conO.commit()

        _conO.close()
        _s = "new  " + self.outputFile + '  created'
        QtGui.QMessageBox.information(self, 'TMV3', _s, QtGui.QMessageBox.Ok)
        return

        pass
    def loadTLM(self):

        _ret = QtGui.QFileDialog.getOpenFileName(self, "Open TLM", "", "TLM (*.Tlm)")
        if (_ret == ""): return
        self.ui.lineEdit.setText(_ret)

        self.inputFile = _ret
        self.outputFile = self.inputFile+'3'
        if os.path.isfile(self.outputFile):
            _s = "new TLM3  " + self.outputFile + "  already exists"
            QtGui.QMessageBox.information(self, 'TMV3', _s, QtGui.QMessageBox.Ok)
            return

        _conI = pypyodbc.win_connect_mdb(self.inputFile)
        _curI = _conI.cursor()
        _curI.execute('SELECT [tTitle],[tComment],[lLimitID] from Limits')
        _ret = _curI.fetchall()
        print(_ret)
        self.tlmCount = 0
        for _f in _ret:
            self.addItem(self.tlmCount,_f[0],_f[1])
            _curI.execute('SELECT [dXValue],[dYValue] from LimitValues WHERE [lLimitID]={0}'.format(str(_f[2])))
            _list = _curI.fetchall()
            self.valueLists.append(_list)
            self.tlmCount +=1

        self.saveFlag = True

    def addItem(self,row,text2,text3):
        _item2 = QtGui.QTableWidgetItem(text2)
        _item3 = QtGui.QTableWidgetItem('?')
        _item5 = QtGui.QTableWidgetItem(text3)

        assert isinstance(self.ui.tableWidget,QtGui.QTableWidget)
        self.ui.tableWidget.insertRow(row)
        self.ui.tableWidget.setItem(row,0,_item2)
        self.ui.tableWidget.setItem(row,2,_item3)
        self.ui.tableWidget.setItem(row,4,_item5)

        _itemC = QtGui.QComboBox()
        _itemC.addItem(text2)
        _itemC.addItems(self.LimitList)
        self.ui.tableWidget.setCellWidget(row,1,_itemC)

        _itemD = QtGui.QDateEdit()
        self.ui.tableWidget.setCellWidget(row,3,_itemD)


    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))