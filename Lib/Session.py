__author__ = 'Heinz'
import threading
#import os.path

import os.path
import configparser
from PyQt4 import uic, QtGui , QtCore
from NeedfullThings import Signal,TableModel
from DB_Handler_TPL3 import Tpl3Sessions

class Session(QtGui.QDialog):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.config = configparser.ConfigParser()
        self.config.read('TMV3.ini')
        self.workBenchDB = self.config['DataBases']['workbench']
        self.ui = uic.loadUi("ViewSession.ui", self)
        sshFile = "c:/tmv3/templates/darkorange.css"
        with open (sshFile,"r") as fh:
            self.setStyleSheet(fh.read())
        self.ui.BtnNew.clicked.connect(self.onBtnNew)
        self.viewTableModel = TableModel(['ID','Title'])
        self.initTableView()
        self.sel = []
        self.ret = False
        self.new = False
        self.ui.show()
    def initTableView(self):
        db = Tpl3Sessions(self.workBenchDB,0)
        _ret = db.readIDs()
        print (_ret)
        if _ret != 0:
            for _row in db.idList:
                self.viewTableModel.addData(_row)

            self.ui.tableView.setModel(self.viewTableModel)
            _header = self.ui.tableView.horizontalHeader()
            _header.setResizeMode(QtGui.QHeaderView.ResizeToContents)

    def onBtnNew(self):
        self.ret = True
        self.new = True
        self.close()
        pass

    def onBtnCancel(self):
        #print('onBtnCancel')
        self.ret = False
        self.sel = []
        self.close()
        pass

    def onBtnOk(self):
        self.ret = True
        self.sel = self.ui.tableView.selectionModel().selectedRows()
        self.selIdx = self.ui.tableView.selectedIndexes()
        if self.sel == []:
            self.ret = False
        self.close()
