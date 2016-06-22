__author__ = 'Heinz'

from PyQt4 import uic,QtGui,QtCore
from NeedfullThings import *
from pydispatch import dispatcher
from Workbench import Ticket
from DB_Handler_TPL3 import TPL3Test

class ExportTests(QtGui.QDialog):
    def __init__(self,startOption):
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("ExportTests.ui", self)
        self.centerOnScreen()
        self.signals = Signal()
        self.ticket = Ticket()
        self.tableModel = None
        self.startOption = startOption

        self.showTable()

        pass

    def showTable(self):
        if self.startOption == "ZK":
            self.tableModel = TableModel(['TestNo', 'EUT', 'SerialNo', 'Date','ID'])

            self.ticket.data = "ZKMV"
            dispatcher.send(self.signals.WB_GET_TEST_IDS, dispatcher.Anonymous,self.ticket)
            _ids = self.ticket.data.ids
            for _id in _ids:
                self.ticket.data = _id
                dispatcher.send(self.signals.WB_GET_TEST, dispatcher.Anonymous,self.ticket)
                _test = self.ticket.data
                self.tableModel.addData([_test.test_no, _test.eut, _test.serial_no, _test.date_time, _test.test_id])

        self.ui.tableView.setModel(self.tableModel)
        _header = self.ui.tableView.horizontalHeader()
        _header.setResizeMode(QtGui.QHeaderView.ResizeToContents)
       # self.ui.twMeas.setColumnHidden(6,True)
        #self.ui.twMeas.setColumnHidden(7,True)
        pass
    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))