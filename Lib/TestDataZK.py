__author__ = 'Heinz'

from NeedfullThings import *
from DB_Handler_TPL3 import *
from Workbench import  Ticket
from datetime import datetime
from Protocol import Protocol
import configparser



class TestDataZK(QtGui.QWidget):
    def __init__(self, parent=None):
        super(QtGui.QWidget, self).__init__(parent)
        self.ui = uic.loadUi("TestDataZK.ui", self)
        self.ticket = Ticket()
        self.signals = Signal()
        self.config = configparser.ConfigParser()
        self.config.read('TMV3.ini')
        self.test = None

        self.GraphProcess = None
        self.GraphProcessList = []
        self.controllerStartTime = datetime.now()

        self.ui.BtnNewDescription.clicked.connect(self.onBtnNewTest)
        self.ui.BtnCloneDescription.clicked.connect(self.onBtnCloneTest)
        self.ui.BtnSaveDescription.clicked.connect(self.onBtnSaveTest)
        self.ui.BtnProtocol.clicked.connect(self.onBtnProtocol)
        self.ui.BtnMarkAsFinal.clicked.connect(self.onBtnMarkAsFinal)
        self.ui.BtnMarkAsTryOut.clicked.connect(self.onBtnMarkAsTryOut)
        self.ui.BtnShowPlot.clicked.connect(self.onBtnShowPlot)
        self.ui.BtnFRwd.clicked.connect(self.onBtnFRwd)
        self.ui.BtnRwd.clicked.connect(self.onBtnRwd)
        self.ui.BtnFwd.clicked.connect(self.onBtnFwd)
        self.ui.BtnFFwd.clicked.connect(self.onBtnFFwd)
        self.ui.BtnExit.clicked.connect(self.onMnuExit)

        dispatcher.connect(self.onLoadTest, signal=self.signals.CTR_LOAD_TEST, sender=dispatcher.Any)

        self.currentTDS = self.config['Current']['current_tds']
        self.lastTDS = ''
        self.planID_ZK = int (self.config['Current']['current_planid_zk'])

        self.currentTestSave = True
        #self.currentTest = TPL3Test
        self.currentTest = None
        self.currentTestID = int (self.config['Current']['current_testid_zk'])
        self.masterID = 0
        self.masterTest = TPL3Test
        self.measTableModel = None
        self.currentPlotNo = 0
        self.currentMeasNo = 0.0

        self.onBtnFFwd()
        #self.onBtnNewTest()

    def loadCurrentTDS(self):
        if self.currentTDS != self.lastTDS:
            self.lastTDS = self.currentTDS
            _file =  Tpl3Files("", 0)
            _file.file_id = self.planID_ZK
            _file.destination = '../WorkingDir/ActiveTestPlan.TDS3'
            self.ticket.data = _file
            dispatcher.send(self.signals.WB_EXPORT_TDS,dispatcher.Anonymous,self.ticket)
            dispatcher.send(self.signals.CTR_LOAD_TESTPLAN, dispatcher.Anonymous)
        pass
    def onLoadTest(self):
        if self.currentTestID != None:
            self.ticket.testID = self.currentTestID
            self.ticket.data = 'ZK'
            dispatcher.send(self.signals.WB_GET_TEST, dispatcher.Anonymous,self.ticket)
            if self.ticket.data != None:
                self.currentTest = self.ticket.data
                self.fillDialog()

    def getNewTest(self, clone):
        dispatcher.send(self.signals.WB_GET_NEW_TEST, dispatcher.Anonymous, self.ticket)
        if not clone:
            if (self.ticket.data != None):
                self.currentTest = self.ticket.data
                self.currentTest.company = self.config['Welcome']['company']
                self.currentTest.technician = self.config['Welcome']['name']
                self.currentTest.lab = self.config['Welcome']['lab']
                self.currentTest.company = self.config['Welcome']['company']
                self.currentTest.category = 'ZK'
                self.currentTestSave = False
                self.currentMeasNo = 0
                self.currentPlotNo = 0
                self.currentTestID = self.currentTest.test_id
                self.fillDialog()
            else:
                QtGui.QMessageBox.information(self, 'TMV3', 'could not generate new test', QtGui.QMessageBox.Ok)
        else:
            if (self.ticket.data != None):
                self.currentTest.test_no = self.ticket.data.test_no
                self.currentTestID = self.ticket.data.test_id
                self.currentTest.test_id = self.ticket.data.test_id
                self.currentTest.date_time = self.ticket.data.date_time
                self.currentMeasNo = 0
                self.currentPlotNo = 0
                self.fillDialog()
            else:
                QtGui.QMessageBox.information(self, 'TMV3', 'could not generate new test', QtGui.QMessageBox.Ok)

        self.config['Current']['current_testID'] = str(self.currentTestID)
        with open('TMV3.ini', 'w')as configfile:
            self.config.write(configfile)
    def onBtnProtocol(self):
        proto = Protocol(self.currentTest)
        proto.exec()
        if proto.ret:
            self.ticket.data = self.currentTest
            dispatcher.send(self.signals.WB_UPDATE_TEST, dispatcher.Anonymous,self.ticket)
            self.fillDialog()


    def onBtnNewTest(self):
        self.getNewTest(False)
        self.onBtnMaster()
        self.onBtnProtocol()

    def onBtnCloneTest(self):
        _oldTest = self.currentTest
        self.getNewTest(True)
        self.onBtnProtocol()

    def onBtnSaveTest(self):

        self.ticket.data = self.currentTest
        dispatcher.send(self.signals.WB_UPDATE_TEST, dispatcher.Anonymous, self.ticket)
        if self.ticket.data == None:
            QtGui.QMessageBox.information(self, 'TMV3', 'could not save current test', QtGui.QMessageBox.Ok)
        else:
            QtGui.QMessageBox.information(self, 'TMV3', 'save completed', QtGui.QMessageBox.Ok)


    def onBtnMaster(self):
        _tm = TableModel(['TEMPEST Z-No', 'EUT-Name', 'Date', 'ID'])
        self.ticket.data = "ZKMV-Master"

        dispatcher.send(self.signals.WB_GET_MASTER_IDS, dispatcher.Anonymous, self.ticket)
        if self.ticket.data == None:
            QtGui.QMessageBox.information(self, 'TMV3', 'no masters found', QtGui.QMessageBox.Ok)
            return False

        _ids = self.ticket.data.ids
        print(_ids)
        for _id in _ids:
            self.ticket.data = _id
            dispatcher.send(self.signals.WB_GET_TEST, dispatcher.Anonymous, self.ticket)
            _test = self.ticket.data
            if _test != None:
                _tm.addData([_test.tempest_z_no, _test.eut, _test.date_time, _test.test_id])

        choose = Choose(_tm, 'Reference KM')

        choose.exec()
        if choose.ret:
            # print(choose.sel)
            # _id = _tm.data(choose.sel[0],Qt.DisplayRole)
            _text = _tm.data(choose.selIdx[0], Qt.DisplayRole)
            _id = _tm.data(choose.selIdx[3], Qt.DisplayRole)
            self.ui.lbTempestNo.setText(_text)
            self.masterID = _id
            self.ticket.data = _id
            dispatcher.send(self.signals.WB_GET_TEST, dispatcher.Anonymous, self.ticket)
            self.masterTest = self.ticket.data
            dispatcher.send(self.signals.CTR_SET_MASTER_ID,dispatcher.Anonymous,self.masterID)

            self.currentTest.project = self.masterTest.project
            self.currentTest.eut = self.masterTest.eut
            self.currentTest.environment = '?'
            if self.masterTest.environment != '?':
                enList = self.masterTest.environment.split(',')
                for a in enList[1::2]:
                        a = '?'
                enStr = ''
                for x in enList:
                    enStr += x
                    enStr += ','
                enStr.rstrip(',')

                self.currentTest.environment = enStr.rstrip(',')

            self.currentTest.setup = self.masterTest.setup
            self.currentTest.procedure = self.masterTest.procedure
            self.currentTest.tempest_z_no = self.masterTest.tempest_z_no
            self.currentTest.type_of_user = self.masterTest.type_of_user
            self.currentTest.type_of_test = self.masterTest.type_of_test
            self.currentTest.type_of_eut = self.masterTest.type_of_eut

    def onBtnMasterDel(self):
        self.masterID = 0
        self.ui.leCertificationNo.setText("")
        self.ui.leCertificationTestID.setText("")

    def onBtnShowPlot(self):
        _idx = self.ui.twMeas.selectedIndexes()
        if len(_idx) == 0:
            return

        # draw selected plot
        _id = self.measTableModel.data(_idx[7], Qt.DisplayRole)

        dispatcher.send(self.signals.CTR_SHOW_PLOT,dispatcher.Anonymous, _id, self.masterID)

    def onBtnMarkAsFinal(self):
        found = False
        for row in range(self.measTableModel.rowCount()):
            _idx = self.measTableModel.index(row,5)
            _data = self.measTableModel.data(_idx, Qt.DisplayRole)
            if _data == 'final':
                _text = 'Sorry, only 1 final Mesasuremt allowed'
                QtGui.QMessageBox.information(self, 'TMV3', _text, QtGui.QMessageBox.Ok)
                return

        _idx = self.ui.twMeas.selectedIndexes()
        if len(_idx) == 0:
            return
        self.measTableModel.setData(_idx[5], "final")

        _id = self.measTableModel.data(_idx[6], Qt.DisplayRole)
        _data = []
        _data.append(_id)
        _data.append('final')
        self.ticket.data = _data
        dispatcher.send(self.signals.WB_SET_GROUP, dispatcher.Anonymous, self.ticket)

        # self.measTableModel.updateView()
        #  s = self.measTableModel.data(_idx[5],Qt.DisplayRole)
        #  print (s)
        pass

    def onBtnMarkAsTryOut(self):
        _idx = self.ui.twMeas.selectedIndexes()
        if len(_idx) == 0:
            return
        self.measTableModel.setData(_idx[5], "try out")

        _id = self.measTableModel.data(_idx[6], Qt.DisplayRole)
        _data = []
        _data.append(_id)
        _data.append('try out')
        self.ticket.data = _data
        dispatcher.send(self.signals.WB_SET_GROUP, dispatcher.Anonymous, self.ticket)
        # s = self.measTableModel.data(_idx[5],Qt.DisplayRole)
        # print (s)

    def onBtnFRwd(self):
        print('BtnFRwd')
        self.ticket.data = "ZK"
        self.ticket.testID = self.currentTestID
        dispatcher.send(self.signals.WB_GET_TEST_FIRST, dispatcher.Anonymous, self.ticket)
        if self.ticket.data != None:
            self.currentTest = self.ticket.data
            self.currentTestID = self.ticket.data.test_id
            self.fillDialog()
        pass

    def onBtnRwd(self):
        print('BtnRwd')
        self.ticket.data = "ZK"
        self.ticket.testID = self.currentTestID
        dispatcher.send(self.signals.WB_GET_TEST_PREV, dispatcher.Anonymous, self.ticket)
        if self.ticket.data != None:
            self.currentTest = self.ticket.data
            self.currentTestID = self.ticket.data.test_id
            self.fillDialog()

    def onBtnFwd(self):
        print('BtnFwd')
        self.ticket.data = "ZK"
        self.ticket.testID = self.currentTestID
        dispatcher.send(self.signals.WB_GET_TEST_NEXT, dispatcher.Anonymous, self.ticket)
        if self.ticket.data != None:
            self.currentTest = self.ticket.data
            self.currentTestID = self.ticket.data.test_id
            self.fillDialog()

    def onBtnFFwd(self):
        print('BtnFFwd')
        self.ticket.data = "ZK"
        self.ticket.testID = self.currentTestID
        dispatcher.send(self.signals.WB_GET_TEST_LAST, dispatcher.Anonymous, self.ticket)
        if self.ticket.data != None:
            self.currentTest = self.ticket.data
            self.currentTestID = self.ticket.data.test_id
            self.fillDialog()

            # ...Tool-Functions .........................................................

    def fillDialog(self):

        if self.measTableModel == None:
            self.measTableModel = TableModel(['MeasNo', 'PlotNo', 'PlotTitle', 'Result', 'Date', 'Group',
                                              'ID','Group','Image'])
            self.delegate = ImageDelegate(self)
            self.ui.twMeas.setItemDelegateForColumn(8,self.delegate)
        self.ui.twMeas.setColumnWidth(8,200)
        self.ui.twMeas.setColumnWidth(0,40)
        self.ui.twMeas.setColumnWidth(1,40)
        self.ui.twMeas.setColumnWidth(3,70)
        self.measTableModel.beginResetModel()
        if self.currentTest != None:

            self.measTableModel.removeRows(0,self.measTableModel.rowCount())
            self.ticket.data = self.currentTest.test_no
            self.ticket.testID = self.currentTestID
            self.ui.lbTestNo.setText(self.currentTest.test_no)
            self.ui.lbTempestNo.setText(self.currentTest.tempest_z_no)

            dispatcher.send(self.signals.WB_GET_PLOT_INFO_IDS, dispatcher.Anonymous, self.ticket)
            _ids = self.ticket.data.ids
            _i = 0
            for _id in _ids:
                self.ticket.data = _id
                dispatcher.send(self.signals.WB_GET_PLOT_INFO, dispatcher.Anonymous, self.ticket)
                _plot = self.ticket.data
                assert isinstance(_plot, Tpl3PlotInfo)
                self.measTableModel.addData([_plot.meas_no, _plot.plot_no, _plot.plot_title, _plot.result,
                                             _plot.date_time, _plot.group, _plot.plot_id,_plot.group,_plot.image])
                if _plot.meas_no > self.currentMeasNo:
                    self.currentMeasNo = _plot.meas_no
                self.ui.twMeas.setRowHeight(_i,110)
                _i += 1

        self.ui.twMeas.setModel(self.measTableModel)
        _header = self.ui.twMeas.horizontalHeader()
        _header.setResizeMode(QtGui.QHeaderView.Fixed)

        # self.ui.twMeas.setColumnHidden(6,True)
        self.ui.twMeas.setColumnHidden(7, True)
        self.ui.twMeas.scrollToBottom()
        self.measTableModel.endResetModel()

    def onMnuExit(self):
        dispatcher.send(self.signals.CTR_EXIT, dispatcher.Anonymous)
