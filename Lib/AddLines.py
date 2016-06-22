__author__ = 'Heinz'

from PyQt4 import uic, QtGui, QtCore
from NeedfullThings import *
from DB_Handler_TPL3 import Tpl3Lines
from Workbench import  Ticket
from pydispatch import dispatcher
import sqlite3
import configparser
import copy
import os
class AddLine(QtGui.QDialog):
    def __init__(self,lineType):
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("AddLines.ui", self)

        self.centerOnScreen()
        self.inputFile = ""
        self.outputFile = ""
        self.valueLists = []
        self.config = configparser.ConfigParser()
        self.config.read('TMV3.ini')
        self.ticket = Ticket()
        self.signals = Signal()
        self.tm = TableModel(['ID', 'Type','Title', 'Version','Date','exists'])
        self.ui.tableView.setModel(self.tm)
        self.tkrSource = ""

        self.ui.BtnImport.clicked.connect(self.onBtnImport)
        self.ui.BtnOk.clicked.connect(self.onBtnOk)
        self.ui.BtnCancel.clicked.connect(self.onBtnCancel)
        self.lineType = lineType

        if lineType == 'Corr':
            self.setWindowTitle('Import Corrections')
        if lineType == 'Limit':
            self.setWindowTitle('Import Limits')

        self.loadLines()
        pass

    def onBtnOk(self):
        self.close()

    def onBtnCancel(self):
        self.close()

    def onBtnImport(self):
        _sel = self.ui.tableView.selectionModel().selectedRows()
        if len(_sel)== 0:
            QtGui.QMessageBox.information(self, 'TMV3', 'no lines selected', QtGui.QMessageBox.Ok)
            return

        _count = 0

        for _row in _sel:
            _ID = self.tm.data(_row,Qt.DisplayRole)
            if self.ui.checkBox.isChecked():
                _r = _row.row()
                _idx = self.tm.index(_r,5)
                _ret = self.tm.data(_idx,Qt.DisplayRole)
                if _ret == 'no':
                    self.importLine(_ID)
                    _count += 1
            else:
                self.importLine(_ID)
                _count += 1

        _text = '{0} Lines imported to Workbench'.format(str(_count))
        QtGui.QMessageBox.information(self, 'TMV3', _text, QtGui.QMessageBox.Ok)
        self.onBtnOk()
        return


    def importLine(self,id):
        _ticket = Ticket()
        _lineSource = Tpl3Lines(self.tkrSource,id)
        _lineSource.read()
        _lineSource.color = ''
        _lineSource.style = ''
        _lineSource.width = 0
        _ticket.data = _lineSource
        dispatcher.send(self.signals.WB_ADD_LINE, dispatcher.Anonymous,_ticket)
        pass
    def loadLines(self):

        if self.lineType == 'Limit':
            _ret = QtGui.QFileDialog.getOpenFileName(self, "Open TLM3", "", "TLM3 (*.Tlm3)")
        else:
            _ret = QtGui.QFileDialog.getOpenFileName(self, "Open TKR3", "", "TKR3 (*.Tkr3)")
        if (_ret == ""): return
        self.tkrSource = _ret
        self.ui.lineEdit.setText(self.tkrSource)

        _lineSource = Tpl3Lines(self.tkrSource,0)
        if self.lineType == "Corr":
            _ret = _lineSource.readCorrIDs()
        if self.lineType == "Limit":
            _ret = _lineSource.readLimitIDs()

        if _ret == False:
            return
        for _id in _lineSource.lineIDs:
            _lineSource.line_id = _id
            _ret = _lineSource.read()
            if _ret == False: return
            _lineDestination = copy.copy(_lineSource)
            _lineDestination.line_id = 0
            self.ticket.data = _lineDestination
            dispatcher.send(self.signals.WB_GET_LINE_EXISTS, dispatcher.Anonymous,self.ticket)
            _exists = 'yes'
            if _lineDestination.line_id == 0:
                _exists = 'no'

            self.tm.addData([_lineSource.line_id, _lineSource.type, _lineSource.title, _lineSource.version, _lineSource.date,_exists])



    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))