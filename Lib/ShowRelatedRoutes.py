__author__ = 'Heinz'
from PyQt4 import uic, QtGui, QtCore
from pydispatch import dispatcher
from Workbench import Ticket
from NeedfullThings import Signal
import DB_Handler_TPL3
import os
from DB_Handler_TDS3 import *
import logging

logging.basicConfig(filename="TMV3log.txt",
                    level=logging.error,
                    format='%(asctime)s %(message)s',
                    datefmt='%m.%d.%Y %I:%M:%S')

class ShowRelatedRoutes(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("ShowRelatedRoutes.ui", self)
        self.centerOnScreen()
        self.ticket = Ticket()
        self.signals = Signal()
        self.antennaIDs = []
        self.cableIDs = []
        self.routesList = []
        self.ds = ''

        self.ui.BtnOk.clicked.connect(self.onBtnOk)

       # self.loadRoutes()

    def showDialog(self):

        self.showNormal()

    def onBtnOk(self):
        self.close()
    def findRoutes(self):

        if self.ds.read():
            self.routesList.clear()
            try:
                for _member_plot in self.ds.db.plot_list:
                    for _member_routine in _member_plot.routine_list:
                        for _member_setting in _member_routine.setting_list:
                            assert isinstance(_member_setting, DatasetSetting)
                            if _member_setting.route != None:
                                self.ticket.data = _member_setting.route
                                self.routesList.append(_member_setting.route)
                                dispatcher.send(self.signals.WB_GET_ROUTE, dispatcher.Anonymous,self.ticket)
                                _route = self.ticket.data
                                if _route.id <= 0:
                                    aliasTitle = '?'
                                    antennaTitle = '?'
                                    cableTitle = '?'
                                    probeTitle = '?'
                                    matrixTitle = '?'
                                else:
                                    aliasTitle = _route.alias
                                    if _route.antennaID != -1:
                                        self.ticket.data = _route.antennaID
                                        dispatcher.send(self.signals.WB_GET_LINE, dispatcher.Anonymous,self.ticket)
                                        _antenna = self.ticket.data
                                        antennaTitle = _antenna.title
                                    else:
                                        antennaTitle = '?'

                                    if _route.cableID != -1:
                                        self.ticket.data = _route.cableID
                                        dispatcher.send(self.signals.WB_GET_LINE, dispatcher.Anonymous,self.ticket)
                                        _cable = self.ticket.data
                                        cableTitle = _cable.title
                                    else:
                                        cableTitle = '?'

                                    if _route.probeID != -1:
                                        self.ticket.data = _route.probeID
                                        dispatcher.send(self.signals.WB_GET_LINE, dispatcher.Anonymous,self.ticket)
                                        _probe = self.ticket.data
                                        probeTitle = _probe.title
                                    else:
                                        probeTitle = '?'

                                    #' add Relais-object to JobTable'
                                    if _route.relaisID != -1:
                                        self.ticket.data = _route.relaisID
                                        dispatcher.send(self.signals.WB_GET_RELAIS, dispatcher.Anonymous,self.ticket)
                                        _matrix = self.ticket.data
                                        matrixTitle = _matrix.title
                                    else:
                                        matrixTitle = '?'

                                self.addItem(_member_setting.title, _member_setting.route, aliasTitle, antennaTitle, cableTitle,
                                             probeTitle, matrixTitle)

            except Exception as err:
                print ('find Routes:',err)
                return False
        return True



    def addItem(self, setting, route, alias, antenna, cable, probe, matrix):

        _item1 = QtGui.QTableWidgetItem(setting)
        _item2 = QtGui.QTableWidgetItem(route)
        _item3 = QtGui.QTableWidgetItem(alias)
        _item4 = QtGui.QTableWidgetItem(antenna)
        _item5 = QtGui.QTableWidgetItem(cable)
        _item6 = QtGui.QTableWidgetItem(probe)
        _item7 = QtGui.QTableWidgetItem(matrix)

        _ret = self.ui.tableWidget.rowCount()
        _ret += 1
        self.ui.tableWidget.setRowCount(_ret)

        self.ui.tableWidget.setItem(_ret-1, 0, _item1)
        self.ui.tableWidget.setItem(_ret-1, 1, _item2)
        self.ui.tableWidget.setItem(_ret-1, 2, _item3)
        self.ui.tableWidget.setItem(_ret-1, 3, _item4)
        self.ui.tableWidget.setItem(_ret-1, 4, _item5)
        self.ui.tableWidget.setItem(_ret-1, 5, _item6)
        self.ui.tableWidget.setItem(_ret-1, 6, _item7)

    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))



