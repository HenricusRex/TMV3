__author__ = 'Heinz'

from PyQt4 import uic, QtGui, QtCore
from pydispatch import dispatcher
from Workbench import Ticket
from NeedfullThings import Signal
import sys

sys.path.append('../DeviceDriver')
import subprocess
import DB_Handler_TPL3
import DD_Relais
import DD_Analyzer
import ast
import sqlite3
import configparser
import os
import logging
import pickle
logging.basicConfig(filename="TMV3log.txt",
                    level=logging.error,
                    format='%(asctime)s %(message)s',
                    datefmt='%m.%d.%Y %I:%M:%S')

class Router(object):
    def __init__(self,parent = None):
        self.parent = parent
        self.cutFreqX1 = 0
        self.cutFreqX2 = 0
        self.signals = Signal()
        pass

    def setRoute(self,saDeviceDriver,alias,antenna,cable,probe,relais):
        _startFreq = [] # used for Receiver TransducerRange
        _stopFreq = []  # used for Receiver TransducerRange
        _setList = []   # used for Receiver TransducerSetting


        # switch Relais
        try:
            _deviceRelais = DD_Relais.Relais(relais.device)
            _ret = _deviceRelais.checkConnection()
            if  _ret == False:
                print("deviceRelais connecion canceled")
                _s = "Matrix {0} not connected. Proceed anyway?" .format(relais.device)
              #  self.MessageProcess = subprocess.Popen([sys.executable, "MessageBox.py", "TMV3", _s], shell=False)
               # self.MessageProcess.wait()
                ret = self.parent.parent.onShowMessageBox(_s, '1')
                if ret == QtGui.QMessageBox.No:
                    return False
            else:
                _deviceRelais.write(relais.command)
                print("deviceRelais connecion established")



            if type(saDeviceDriver) == str:
                sa = DD_Analyzer.SpectrumAnalyzer(saDeviceDriver)
            else:
                sa = saDeviceDriver

            _ret = sa.checkConnection()
            if  _ret == False:
                return False

            # _ret = sa.setup()
            # if  _ret == False:
            #     return False

        except Exception as _err:
            print("....................................................................")
            logging.exception(_err)

        try:
            #set Antenna Transducer
            if antenna != None:
                _data = ast.literal_eval(antenna.data_xy)
                _sdata = sorted(_data,key = lambda x: x[0])

                #if cutFreq given, then calculate exact Frequency-Range
                if self.cutFreqX1 != 0:
                    _sdata = self.cutRange(_sdata)

                _s = ""
                _startFreq.append(10e9)
                _stopFreq.append(0)
                for x, y in _sdata:
                    _s += "{0}HZ,{1},".format(str(x),str(y))
                    if x < _startFreq[0]: _startFreq[0] = x
                    if x > _stopFreq[0]: _stopFreq[0] = x
                _list = _s.rstrip(',')
                _ret = sa.set_Transducer(antenna.title,'DB',_list)
                if not _ret:
                    return False
                _setList.append(antenna.title)

            #set Cable Transducer
            if cable != None:
                _data = ast.literal_eval(cable.data_xy)
                _sdata = sorted(_data,key = lambda x: x[0])

                #if cutFreq given, then calculate exact Frequency-Range
                if self.cutFreqX1 != 0:
                    _sdata = self.cutRange(_sdata)

                _s = ""
                _startFreq.append(10e9)
                _stopFreq.append(0)
                for x,y in _sdata:
                    _s += "{0}HZ,{1},".format(str(x),str(y))
                    if x < _startFreq[1]: _startFreq[1] = x
                    if x > _stopFreq[1]: _stopFreq[1] = x

                _list = _s.rstrip(',')
                _ret = sa.set_Transducer(cable.title,'DB',_list)
                if not _ret:
                    return False
                _setList.append(cable.title)

            #set Probe Transducer
            if probe != None:
                _data = ast.literal_eval(probe.data_xy)
                _sdata = sorted(_data,key = lambda x: x[0])

                #if cutFreq given, then calculate exact Frequency-Range
                if self.cutFreqX1 != 0:
                    _sdata = self.cutRange(_sdata)

                _s = ""
                _startFreq.append(10e9)
                _stopFreq.append(0)
                for x,y in _sdata:
                    _s += "{0}HZ,{1},".format(str(x),str(y))
                    if x < _startFreq[2]: _startFreq[2] = x
                    if x > _stopFreq[2]: _stopFreq[2] = x

                _list = _s.rstrip(',')
                _ret = sa.set_Transducer(probe.title,'DB',_list)
                if not _ret: return False
                _setList.append(probe.title)

            # find the intersection of all Transducers
            _x1 = max(_startFreq)
            _x2 = min(_stopFreq)

            _ret = sa.set_TransducerSet(alias, _setList, 'DB', _x1, _x2)
            if not _ret: return False

            sa.closeSession()
        except Exception as _err:
            print ("Router: SetRoute: {0}".format(str(_err)))
            logging.exception(_err)
        return True

    def cutRange(self,data):
        _xa1 = [0,0]
        _xa2 = [0,0]
        _xe1 = [0,0]
        _xe2 = [0,0]
        _xaSet = False
        _xeSet = False


        try:
            #calc cut points
            for x in data:
                _xa1 = _xa2
                _xa2 = x
                if x[0] == self.cutFreqX1:
                    _xaSet = True
                    break
                if x[0] > self.cutFreqX1:
                    break

            for x in data:
                _xe1 = _xe2
                _xe2 = x
                if x[0] == self.cutFreqX2:
                    _xeSet = True
                    break
                if x[0] > self.cutFreqX2:
                    break

            if not _xaSet:
                _x1 = _xa1[0]
                _x2 = _xa2[0]
                _y1 = _xa1[1]
                _y2 = _xa2[1]

                _a = (_y2 - _y1) / (_x2 - _x1)
                _b = _y2- _x2 * _a
                _y = _a * self.cutFreqX1 + _b
                _y = round(_y, 1)
                data.append((self.cutFreqX1, _y))


            if not _xeSet:
                _x1 = _xe1[0]
                _x2 = _xe2[0]
                _y1 = _xe1[1]
                _y2 = _xe2[1]

                _a = (_y2 - _y1) / (_x2 - _x1)
                _b = _y2- _x2 * _a
                _y = _a * self.cutFreqX2 + _b
                _y = round(_y, 1)
                data.append((self.cutFreqX2, _y))

            _l1 = sorted(data,key = lambda x: x[0])

            _l2 = []
            for x in _l1:
                if (x[0] >= self.cutFreqX1) and (x[0] <= self.cutFreqX2):
                    _l2.append(x)

        except Exception as _err:
            print ("Router: curRange: {0}".format(str(_err)))
            logging.exception(_err)

        return _l2


    def showMessage(self,text):
        s = str(text).replace('\r','')
        s = s.replace('\n','')
        sdata = pickle.dumps(s)
        dispatcher.send(self.signals.SHOW_MESSAGE, dispatcher.Anonymous,sdata)

class Routing(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("../Lib/Routing.ui", self)
        self.centerOnScreen()
        self.saveFlag = True
        self.delFlag = False
        self.ticket = Ticket()
        self.signals = Signal()
        self.antennaIDs = []
        self.cableIDs = []
        self.route = 0
        self.routesList = []
        self.tableRow = -1
        self.delList = []

        self.ui.BtnNew.clicked.connect(self.onBtnNew)
        self.ui.BtnEdit.clicked.connect(self.onBtnEdit)
        self.ui.BtnAdd.clicked.connect(self.onBtnAdd)
        self.ui.BtnDel.clicked.connect(self.onBtnDel)
        self.ui.BtnRoute.clicked.connect(self.onBtnRoute)
        self.ui.BtnOk.clicked.connect(self.onBtnOk)
        self.ui.BtnCancel.clicked.connect(self.onBtnCancel)

        self.ui.tableWidget.doubleClicked.connect(self.onTableDoubleClick)
       # self.loadRoutes()

    def showDialog(self):

        self.showNormal()

    def addEmptyRoute(self,alias):
        _route  = DB_Handler_TPL3.Tpl3Routes("",0)
        _route.alias = alias
        _route.antennaID = -1
        _route.cableID = -1
        _route.probeID = -1
        _route.relaisID = -1

        self.ticket.data  = _route
        dispatcher.send(self.signals.WB_ADD_ROUTE, dispatcher.Anonymous,self.ticket)

    def onTableDoubleClick(self):
        self.onBtnEdit()
    def onBtnNew(self):

        self.ui.lineEdit.setText('?')

        _idx = self.ui.cbAntenna.findText('?')
        self.ui.cbAntenna.setCurrentIndex(_idx)

        _idx = self.ui.cbCable.findText('?')
        self.ui.cbCable.setCurrentIndex(_idx)

        _idx = self.ui.cbProbe.findText('?')
        self.ui.cbProbe.setCurrentIndex(_idx)

        _idx = self.ui.cbRelais.findText('?')
        self.ui.cbRelais.setCurrentIndex(_idx)

        self.tableRow = -1

    def onBtnEdit(self):

        _row = self.ui.tableWidget.currentRow()
        _item = self.ui.tableWidget.item(_row,0)
        _alias = _item.data(0)
        self.ui.lineEdit.setText(_alias)

        _item = self.ui.tableWidget.item(_row,1)
        _idx = self.ui.cbAntenna.findText(_item.data(0))
        self.ui.cbAntenna.setCurrentIndex(_idx)

        _item = self.ui.tableWidget.item(_row,2)
        _idx = self.ui.cbCable.findText(_item.data(0))
        self.ui.cbCable.setCurrentIndex(_idx)

        _item = self.ui.tableWidget.item(_row,3)
        _idx = self.ui.cbProbe.findText(_item.data(0))
        self.ui.cbProbe.setCurrentIndex(_idx)

        _item = self.ui.tableWidget.item(_row,4)
        _idx = self.ui.cbRelais.findText(_item.data(0))
        self.ui.cbRelais.setCurrentIndex(_idx)

        self.tableRow = _row

    def onBtnOk(self):

        if not self.saveFlag:
        #    dispatcher.send(self.signals.WB_DEL_ROUTE, dispatcher.Anonymous)
            for row in range(self.ui.tableWidget.rowCount()):
                _routeExists = False
               # _route  = DB_Handler_TPL3.Tpl3Routes("",0)
                #_route.alias = self.ui.tableWidget.item(row,0).data(0)
                self.ticket.data = self.ui.tableWidget.item(row,0).data(0)
                dispatcher.send(self.signals.WB_GET_ROUTE, dispatcher.Anonymous,self.ticket)
                if self.ticket.data != None:
                    _route = self.ticket.data
                    _routeExists = True
                else:
                    _route  = DB_Handler_TPL3.Tpl3Routes("",0)

                _route.alias = self.ui.tableWidget.item(row,0).data(0)
                _route.antennaID = self.ui.tableWidget.item(row,1).data(QtCore.Qt.UserRole)
                _route.cableID = self.ui.tableWidget.item(row,2).data(QtCore.Qt.UserRole)
                _route.probeID = self.ui.tableWidget.item(row,3).data(QtCore.Qt.UserRole)
                _route.relaisID = self.ui.tableWidget.item(row,4).data(QtCore.Qt.UserRole)
                self.ticket.data = _route
                if _routeExists:
                    _ret = dispatcher.send(self.signals.WB_UPDATE_ROUTE, dispatcher.Anonymous,self.ticket)
                else:
                    _ret = dispatcher.send(self.signals.WB_ADD_ROUTE, dispatcher.Anonymous,self.ticket)

        if self.delFlag:
            for x in self.delList:
                    self.ticket.data = x
                    print ('delete ',x)
                    dispatcher.send(self.signals.WB_DEL_ROUTE, dispatcher.Anonymous,self.ticket)


        self.close()
    def onBtnCancel(self):
        self.close()
    def onBtnAdd(self):
        self.saveFlag = False
        _alias = self.ui.lineEdit.text()
        if _alias ==  "":
            QtGui.QMessageBox.information(self, 'TMV3', "please choose name for 'alias'", QtGui.QMessageBox.Ok)
            return
        _antennaTitle = self.ui.cbAntenna.currentText()
        _id1 = self.ui.cbAntenna.itemData(self.ui.cbAntenna.currentIndex(),QtCore.Qt.UserRole)
        _cableTitle = self.ui.cbCable.currentText()
        _id2 = self.ui.cbCable.itemData(self.ui.cbCable.currentIndex(),QtCore.Qt.UserRole)
        _probeTitle = self.ui.cbProbe.currentText()
        _id3 = self.ui.cbProbe.itemData(self.ui.cbProbe.currentIndex(),QtCore.Qt.UserRole)
        _relaisTitle = self.ui.cbRelais.currentText()
        _id4 = self.ui.cbRelais.itemData(self.ui.cbRelais.currentIndex(),QtCore.Qt.UserRole)
        if _id1 == None:
            _id1 = -1
        if _id2 == None:
            _id2 = -1
        if _id3== None:
            _id3 = -1
        if _id4 == None:
            _id4 = -1

        if self.tableRow == -1:
            self.addItem(_alias,_antennaTitle,_id1,_cableTitle,_id2,_probeTitle,_id3,_relaisTitle,_id4)
        else:
            self.ui.tableWidget.item(self.tableRow,0).setText(_alias)
            self.ui.tableWidget.item(self.tableRow,1).setText(_antennaTitle)
            self.ui.tableWidget.item(self.tableRow,1).setData(QtCore.Qt.UserRole,_id1)
            self.ui.tableWidget.item(self.tableRow,2).setText(_cableTitle)
            self.ui.tableWidget.item(self.tableRow,2).setData(QtCore.Qt.UserRole,_id2)
            self.ui.tableWidget.item(self.tableRow,3).setText(_probeTitle)
            self.ui.tableWidget.item(self.tableRow,3).setData(QtCore.Qt.UserRole,_id3)
            self.ui.tableWidget.item(self.tableRow,4).setText(_relaisTitle)
            self.ui.tableWidget.item(self.tableRow,4).setData(QtCore.Qt.UserRole,_id4)



        pass

    def onBtnRoute(self):
        _row = self.ui.tableWidget.currentRow()
        _item = self.ui.tableWidget.item(_row,0)
        _alias = _item.data(0)
        _saDeviceDriver = self.ui.cBReceiver.currentText()
        self.testRoute(_alias, _saDeviceDriver)

    def testRoute(self,alias,saDeviceDriver):

        self.ticket.data = alias
        dispatcher.send(self.signals.WB_GET_ROUTE, dispatcher.Anonymous,self.ticket)
        _route = self.ticket.data
        assert isinstance(_route,DB_Handler_TPL3.Tpl3Routes)

        if _route.relaisID > 0:
            self.ticket.data = _route.relaisID
            dispatcher.send(self.signals.WB_GET_RELAIS, dispatcher.Anonymous,self.ticket)
            relais = self.ticket.data
        else:
            relais = None

        if _route.antennaID > 0:
            self.ticket.data = _route.antennaID
            dispatcher.send(self.signals.WB_GET_LINE, dispatcher.Anonymous,self.ticket)
            antenna = self.ticket.data
        else:
            antenna = None

        if _route.cableID > 0:
            self.ticket.data = _route.cableID
            dispatcher.send(self.signals.WB_GET_LINE, dispatcher.Anonymous,self.ticket)
            cable = self.ticket.data
        else:
            cable = None

        if _route.probeID > 0:
            self.ticket.data = _route.probeID
            dispatcher.send(self.signals.WB_GET_LINE, dispatcher.Anonymous,self.ticket)
            probe = self.ticket.data
        else:
            probe = None
        try:
            _router = Router()
            _router.setRoute(saDeviceDriver,alias,antenna,cable,probe,relais)
        except Exception as _err:
            print (_err)
        return True

    def onBtnDel(self):
        self.delFlag = True
        _row = self.ui.tableWidget.currentRow()
        _item = self.ui.tableWidget.item(_row,0)
        _alias = _item.data(0)
        self.delList.append(_alias)
        self.ui.tableWidget.removeRow(_row)
        pass

    def loadRoutes(self):
        #load all Routes
        dispatcher.send(self.signals.WB_GET_ROUTE_IDS, dispatcher.Anonymous,self.ticket)
        _route = self.ticket.data
        _aliasList = _route.alias_list
        self.routesList = _aliasList

        for alias in _aliasList:
            self.ticket.data = alias
            dispatcher.send(self.signals.WB_GET_ROUTE, dispatcher.Anonymous,self.ticket)
            _route = self.ticket.data

            if _route.antennaID > 0:
                self.ticket.data = _route.antennaID
                dispatcher.send(self.signals.WB_GET_LINE, dispatcher.Anonymous,self.ticket)
                _antennaTitle = self.ticket.data.title + '-' + self.ticket.data.version + "-" + self.ticket.data.date
            else:
                _antennaTitle = "?"

            if _route.cableID > 0:
                self.ticket.data = _route.cableID
                dispatcher.send(self.signals.WB_GET_LINE, dispatcher.Anonymous,self.ticket)
                _cableTitle = self.ticket.data.title + '-' + self.ticket.data.version + "-" + self.ticket.data.date
            else:
                _cableTitle = "?"

            if _route.probeID > 0:
                self.ticket.data = _route.probeID
                dispatcher.send(self.signals.WB_GET_LINE, dispatcher.Anonymous,self.ticket)
                _probeTitle = self.ticket.data.title + '-' + self.ticket.data.version + "-" + self.ticket.data.date
            else:
                _probeTitle="?"

            if _route.relaisID > 0:
                self.ticket.data = _route.relaisID
                dispatcher.send(self.signals.WB_GET_RELAIS, dispatcher.Anonymous,self.ticket)
                _relaisTitle = self.ticket.data.title
            else:
                _relaisTitle = "?"

            self.addItem(_route.alias,_antennaTitle,_route.antennaID,_cableTitle,_route.cableID,
                         _probeTitle,_route.probeID,_relaisTitle,_route.relaisID)




        #load all Antennas
        self.ticket.data = "Antenna"
        dispatcher.send(self.signals.WB_GET_LINE_IDS, dispatcher.Anonymous,self.ticket)
        _antennaList = self.ticket.data.lineIDs
        assert isinstance(self.ui.cbAntenna,QtGui.QComboBox)
        for _id in _antennaList:
            self.ticket.data = _id
            dispatcher.send(self.signals.WB_GET_LINE, dispatcher.Anonymous,self.ticket)
            _s = self.ticket.data.title + '-' + self.ticket.data.version + "-" + self.ticket.data.date
            self.ui.cbAntenna.addItem(_s,_id)
        self.ui.cbAntenna.addItem('?')

        #load all Cables
        self.ticket.data = "Cable"
        dispatcher.send(self.signals.WB_GET_LINE_IDS, dispatcher.Anonymous,self.ticket)
        _cableList = self.ticket.data.lineIDs
        assert isinstance(self.ui.cbAntenna,QtGui.QComboBox)
        for _id in _cableList:
            self.ticket.data = _id
            dispatcher.send(self.signals.WB_GET_LINE, dispatcher.Anonymous,self.ticket)
            _s = self.ticket.data.title + '-' + self.ticket.data.version + "-" + self.ticket.data.date
            self.ui.cbCable.addItem(_s,_id)
        self.ui.cbCable.addItem('?')

        #load all Probes
        self.ticket.data = "Probe"
        dispatcher.send(self.signals.WB_GET_LINE_IDS, dispatcher.Anonymous,self.ticket)
        _probeList = self.ticket.data.lineIDs
        for _id in _probeList:
            self.ticket.data = _id
            dispatcher.send(self.signals.WB_GET_LINE, dispatcher.Anonymous,self.ticket)
            _s = self.ticket.data.title + '-' + self.ticket.data.version + "-" + self.ticket.data.date
            self.ui.cbProbe.addItem(_s,_id)
        self.ui.cbProbe.addItem('?')

        #load all Matrix-Devices
        dispatcher.send(self.signals.WB_GET_RELAIS_IDS, dispatcher.Anonymous,self.ticket)
        _relaisList = self.ticket.data.relaisIDs
        for _id in _relaisList:
            self.ticket.data = _id
            dispatcher.send(self.signals.WB_GET_RELAIS, dispatcher.Anonymous,self.ticket)
            _s = self.ticket.data.title
            self.ui.cbRelais.addItem(_s, _id)
        self.ui.cbRelais.addItem('?')
        self.saveFlag = True

    def addItem(self, alias, antenna, ID1, cable, ID2, probe, ID3, matrix, ID4):
        _item1 = QtGui.QTableWidgetItem(alias)
        _item2 = QtGui.QTableWidgetItem(antenna)
        _item2.setData(QtCore.Qt.UserRole,ID1)
        _item3 = QtGui.QTableWidgetItem(cable, ID2)
        _item3.setData(QtCore.Qt.UserRole,ID2)
        _item4 = QtGui.QTableWidgetItem(probe, ID3)
        _item4.setData(QtCore.Qt.UserRole,ID3)
        _item5 = QtGui.QTableWidgetItem(matrix, ID4)
        _item5.setData(QtCore.Qt.UserRole,ID4)

        _ret = self.ui.tableWidget.rowCount()
        _ret += 1
        self.ui.tableWidget.setRowCount(_ret)

        self.ui.tableWidget.setItem(_ret-1, 0, _item1)
        self.ui.tableWidget.setItem(_ret-1, 1, _item2)
        self.ui.tableWidget.setItem(_ret-1, 2, _item3)
        self.ui.tableWidget.setItem(_ret-1, 3, _item4)
        self.ui.tableWidget.setItem(_ret-1, 4, _item5)

        # _itemC = QtGui.QComboBox()
        # if text1 == 'Antenna':
        #     _itemC.addItems(self.AntennaList)
        # if text1 == 'Cable':
        #     _itemC.addItems(self.CableList)
        # self.ui.tableWidget.setCellWidget(row,2,_itemC)
        #
        # _itemD = QtGui.QDateEdit()
        # self.ui.tableWidget.setCellWidget(row,4,_itemD)

    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))



    def showMessage(self,text):
        s = str(text).replace('\r','')
        s = s.replace('\n','')
        sdata = pickle.dumps(s)
        dispatcher.send(self.signals.SHOW_MESSAGE, dispatcher.Anonymous,sdata)
