__author__ = 'Heinz'

from PyQt4 import uic, QtGui, QtCore
from DB_Handler_TPL3 import Tpl3Lines
from Workbench import Ticket
from pydispatch import dispatcher
from NeedfullThings import Signal
import pypyodbc
import sqlite3
import configparser
import os
import shutil
from datetime import datetime

class TLMtoTLM3(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("TLMtoTLM3.ui", self)
        self.centerOnScreen()
        self.inputFile = ""
        self.outputFile = ""
        self.tkrNo = 0
        self.tkrCount = 0
        self.valueLists = []
        self.config = configparser.ConfigParser()
        self.config.read('TMV3.ini')
        _ret = self.config['Antenna']['AntennaList']
        self.saveFlag = True
        self.ticket = Ticket()
        self.signals = Signal()

        self.ui.BtnFile.clicked.connect(self.loadTLM)
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
            _ret = self.ui.tableWidget.cellWidget(_row,1)
            if _ret == "":
                QtGui.QMessageBox.information(self, 'TMV3', "you have to set the new Titles", QtGui.QMessageBox.Ok)
                return
        try:
            shutil.copy("../Templates/TMV3.TLM3",self.outputFile)
            self.saveTLM3()
        except Exception as _err:
            QtGui.QMessageBox.information(self, 'TMV3', str(_err), QtGui.QMessageBox.Ok)
        return

    def saveTLM3(self):

        _line = Tpl3Lines("",0)
        _d = datetime.now()
        _date_time = datetime(_d.year,_d.month,_d.day,_d.hour,_d.minute,_d.second).isoformat(' ')
        _rows = self.ui.tableWidget.rowCount()
        _listCount = 0
        _line.filename = self.outputFile
        for _row in range (_rows):
            _line.type ='Limit'
            _line.title = self.ui.tableWidget.item(_row,1).text()
            _line.version = self.ui.tableWidget.item(_row,2).text()
            _line.date = _date_time
            _line.comment = self.ui.tableWidget.item(_row,3).text()
            _line.data_xy = self.valueLists[_listCount]
            _line.color = 'red'
            _line.style = '-'
            _line.width = 3
            _line.used = 0
            _listCount += 1
            _line.add()


        _s = "new  " + self.outputFile + '  created'
        QtGui.QMessageBox.information(self, 'TMV3', _s, QtGui.QMessageBox.Ok)
        self.saveFlag = True


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
            self.addItem(self.tlmCount,_f[0],_f[0],'1.0',_f[1])
            _curI.execute('SELECT [dXValue],[dYValue] from LimitValues WHERE [lLimitID]={0}'.format(str(_f[2])))
            _list = _curI.fetchall()
            self.valueLists.append(_list)
            self.tlmCount +=1
            pass


        self.saveFlag = True

    def addItem(self,row,text1,text2,text3,text4):
        _item1 = QtGui.QTableWidgetItem(text1)
        _item2 = QtGui.QTableWidgetItem(text2)
        _item3 = QtGui.QTableWidgetItem(text3)
        _item4 = QtGui.QTableWidgetItem(text4)

        assert isinstance(self.ui.tableWidget,QtGui.QTableWidget)
        self.ui.tableWidget.insertRow(row)
        self.ui.tableWidget.setItem(row,0,_item1)
        self.ui.tableWidget.setItem(row,1,_item2)
        self.ui.tableWidget.setItem(row,2,_item3)
        self.ui.tableWidget.setItem(row,3,_item4)

#        _itemC = QtGui.QComboBox()
#        if text1 == 'Antenna':
#            _itemC.addItems(self.AntennaList)
#        if text1 == 'Cable':
#            _itemC.addItems(self.CableList)
#        self.ui.tableWidget.setCellWidget(row,2,_itemC)

  #      _itemD = QtGui.QDateEdit()
  #      self.ui.tableWidget.setCellWidget(row,4,_itemD)


    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))