# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:42:08 2013

@author: HS
"""
import subprocess
import signal
import os
import ctypes
import platform
import shutil
import time
import threading
import signal
import cProfile, pstats, io
from datetime import datetime
from Workbench import Ticket
from NeedfullThings import *
from DB_Handler_TDS3 import *
from DB_Handler_TPL3 import *
from Server import Server
from JobTables import JobTable
from DB_Handler_TPL3 import Tpl3Routes, Tpl3Lines
from ImportZZ import *
from ImportZKMV import *

import Line
import Routing
import Workbench
import TKRtoTKR3
import TLMtoTLM3
import TDStoTDS3
import AddLines
import ExportTests
import ImportMaster
import TestDataZK
import TestDataZZ
import ShowRelatedRoutes
import ServerGraph


logging.basicConfig(filename="TMV3log.txt",
                    level=logging.ERROR,
                    format='%(asctime)s %(message)s',
                    datefmt='%m.%d.%Y %I:%M:%S')


class MainForm(QtGui.QMainWindow):
    signalShowMessage = pyqtSignal(str)
    signalCollapseTreeview = pyqtSignal()
    signalWait = threading.Event()
    signalWaitForFinishedLastPlot = threading.Event()

    def __init__(self, parent=None):
        # global model

        self.testPyhtonRunning()
        QtGui.QMainWindow.__init__(self)
        self.ui = uic.loadUi("Controller.ui", self)
        self.pr = cProfile.Profile()
        #   self.controlTreeView = ControlTreeView.ControlTreeView(self)
        #   self.ui.tabWidget.addTab(self.controlTreeView,'xx')
        self.model = QtGui.QStandardItemModel()
        self.model.itemChanged.connect(self.onItemChanged)
        #self.treeview_item_list = []
        self.signalWaitForFinishedLastPlot.set()
        self.JTable = 0
        self.signals = Signal()

        self.Server = Server(self)

        self.MeasProcess = None
        self.GraphProcess = None
        self.GraphProcessList = []
        self.config = configparser.ConfigParser()
        self.routeFlag = True
        self.timer = threading.Timer(5, self.timeOutMeasurementStart)
        self.ds = 0  # dataset
        self.statusBar_label1 = QtGui.QLabel('')
        #  self.statusBar_label2 = QtGui.QLabel("")
        #self.statusBar_label.setStyleSheet('QLabel {color: red}')
        self.statusBar().addWidget(self.statusBar_label1)
        self.workBench = None
        self.workBenchDB = ''
        self.workingDir = ""
        self.currentTDS = ''
        self.initControl()
        self.col = QtGui.QColor
        self.ticket = Ticket()
        self.startOption = ""
        self.currentMode = 0
        self.startPosSet = False
        self.graphStarted = False
        self.controllerStartTime = datetime.now()
        self.uiWidth = 0
        self.uiHeight = 0
        self.planTitle = ""
        self.runningFlag = False
        # self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint)
        # self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMaximizeButtonHint)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint)
        self.testModul = None

        #Signals from Process Meas
        dispatcher.connect(self.onMeasStarted, signal=self.signals.MEAS_STARTED, sender=dispatcher.Any)
        dispatcher.connect(self.onJobComplete, self.signals.JOB_COMPLETE, dispatcher.Any)
        dispatcher.connect(self.onItemComplete, signal=self.signals.ITEM_COMPLETE, sender=dispatcher.Any)
        dispatcher.connect(self.onItemActive, signal=self.signals.ITEM_ACTIVE, sender=dispatcher.Any)
        dispatcher.connect(self.onLoadTDS, signal=self.signals.CTR_LOAD_TESTPLAN, sender=dispatcher.Any)
        dispatcher.connect(self.onMeasError, signal=self.signals.MEAS_ERROR, sender=dispatcher.Any)
        dispatcher.connect(self.onPlotComplete, signal=self.signals.MEAS_PLOT_COMPLETE, sender=dispatcher.Any)
        dispatcher.connect(self.onMeasResult, signal=self.signals.MEAS_RESULT, sender=dispatcher.Any)
        dispatcher.connect(self.onBtnShowPlot, signal=self.signals.CTR_SHOW_PLOT, sender=dispatcher.Any)

        dispatcher.connect(self.onMnuExit, signal=self.signals.CTR_EXIT)
     #   dispatcher.connect(self.onSetMasterID, signal=self.signals.CTR_SET_MASTER_ID)
        #Signals from Process Graph
        dispatcher.connect(self.onGraphStarted, signal=self.signals.GRAPH_STARTED, sender=dispatcher.Any)
        dispatcher.connect(self.onGraphStopped, self.signals.GRAPH_STOPPED, dispatcher.Any)
        dispatcher.connect(self.onGraphError, signal=self.signals.GRAPH_ERROR, sender=dispatcher.Any)
        dispatcher.connect(self.onGraphNewPlot, signal=self.signals.GRAPH_NEW_PLOT, sender=dispatcher.Any)
        dispatcher.connect(self.onGraphNewLine, signal=self.signals.GRAPH_NEW_LINE, sender=dispatcher.Any)
        dispatcher.connect(self.onGraphNewTrace, signal=self.signals.GRAPH_NEW_TRACE, sender=dispatcher.Any)
        dispatcher.connect(self.onPlotThumbnail, signal=self.signals.GRAPH_THUMBNAIL_READY, sender=dispatcher.Any)
        dispatcher.connect(self.onShowMessageA, signal=self.signals.ERROR_MESSAGE, sender=dispatcher.Any)
        dispatcher.connect(self.onShowMessageA, signal=self.signals.SHOW_MESSAGE, sender=dispatcher.Any)
        self.signalShowMessage.connect(self.onShowMessageB)
        self.signalCollapseTreeview.connect(self.collapseTreeView)

        #Signals from Workbench
        dispatcher.connect(self.onNewPlotID, signal=self.signals.WB_NEW_PLOT_ID, sender=dispatcher.Any)

        self.config.read('TMV3.ini')
        _ret = self.config['Const']['first_start']
        if _ret == 0:
            self.firstStart()

        self.workBenchDB = self.config['DataBases']['workbench']
        self.workingDir = self.config['Pathes']['workingdir']
        self.currentTDS = self.config['Current']['current_tds']
        self.startOption = self.config['Welcome']['start_option']

        # load Workbench
        print('load workbench')
        if not QtCore.QFile.exists(self.workBenchDB):
            print('no workbench')
            exit

        self.startWorkbench()

        if self.startOption == 'ZK':
            self.uiWidth = 1080
            self.uiHeight = 750
            self.resize(self.uiWidth, self.uiHeight)
            self.testModul = TestDataZK.TestDataZK()
            self.ui.tabWidget.addTab(self.testModul, "Zone KMV")
            self.ui.tabWidget.tabBar().moveTab(3, 0)

            self.ui.actionAddLimits.setVisible(False)
            self.ui.actionAddCorrections.setVisible(False)
            self.ui.actionAddTestPlan.setVisible(False)
            self.ui.actionExport_Master_KMV.setVisible(False)
            self.ui.actionUpdate_ZZ.setVisible(False)
            #    self.ui.width = 1080
            #   self.ui.height = 750


            #copy last TestPlan to ActiveTestPlan
            # self.currentTestID = int (self.config['Current']['current_testID_ZK'])
            #_planID = int(self.config['Current']['current_planID_ZK'])
            self.planTitle = "Zone KMV"

        if self.startOption == 'ZZ':
            self.uiWidth = 1120
            self.uiHeight = 920
            self.resize(self.uiWidth, self.uiHeight)
            self.testModul = TestDataZZ.TestDataZZ()
            self.ui.tabWidget.addTab(self.testModul, "Zone Zulassung")
            self.ui.tabWidget.tabBar().moveTab(3, 0)

            self.ui.actionAddLimits.setVisible(False)
            self.ui.actionAddTestPlan.setVisible(False)
            #copy last TestPlan to ActiveTestPlan
            #self.currentTestID = int (self.config['Current']['current_testID_ZZ'])
            #_planID = int(self.config['Current']['current_planID_ZZ'])
            self.planTitle = "Zone Approval"

        if self.startOption == 'SK':
            self.currentTestID = int(self.config['Current']['current_testID_SK'])
            #_planID = int(self.config['Current']['current_planID_SK'])

        if self.startOption == 'SZ':
            self.currentTestID = int(self.config['Current']['current_testID_SZ'])
            #_planID = int(self.config['Current']['current_planID_SZ'])




        #        self.ui.tabWidget.addTab(self.tabDescription,"Description")
        #        self.ui.tabWidget.tabBar().moveTab(3,0)

        self.ui.tabWidget.setCurrentIndex(0)

        #  dispatcher.send(self.signals.CTR_LOAD_TEST, dispatcher.Anonymous)

        self.JTable = JobTable()
        self.JTable.clean()

        # self.statusBar_label.repaint()

    #        if QtCore.QFile.exists(self.currentTDS):
    #            self.ui.setCursor(QtCore.Qt.BusyCursor)
    #            QtCore.QTimer.singleShot(100,self.onLoadTDS)
    def initControl(self):
        #Buttons
        self.ui.BtnSelAll.clicked.connect(self.onBtnSelAll)
        self.ui.BtnSelNone.clicked.connect(self.onBtnSelNone)
        self.ui.BtnStart.clicked.connect(self.onBtnStart)
        self.ui.BtnStop.clicked.connect(self.onBtnStop)
        self.ui.BtnPause.clicked.connect(self.onBtnPause)
        self.ui.BtnTraceRestart.clicked.connect(self.onBtnTraceRestart)
        self.ui.BtnTKRtoTKR3.clicked.connect(self.onBtnTKRtoTKR3)
        self.ui.BtnTLMtoTLM3.clicked.connect(self.onBtnTLMtoTLM3)
        self.ui.BtnTDStoTDS3.clicked.connect(self.onBtnTDStoTDS3)

        self.ui.BtnExit_3.clicked.connect(self.onMnuExit)
        self.ui.BtnExit_2.clicked.connect(self.onMnuExit)
        self.ui.BtnExit.clicked.connect(self.onMnuExit)
        self.ui.BtnBackupTPL.clicked.connect(self.onBtnBackupTPL)

        self.ui.BtnShowRelatedRoute.clicked.connect(self.onShowRelatedRoutes)
        self.ui.BtnSetRelatedRoute.clicked.connect(self.onSetRelatedRoutes)

        self.ui.tabWidget.currentChanged.connect(self.onTabChanged)

        #callbacks

        #   self.ui.actionOpen.triggered.connect(self.onMnuOpenTest)
        self.ui.actionLimits.triggered.connect(self.onMnuOpenLimits)
        # self.ui.actionOpenRoutes.triggered.connect(self.onMnuOpenRoutes)
        self.ui.actionRoutes.triggered.connect(self.onMnuRoutes)
        self.ui.actionAntenna.triggered.connect(self.onMnuAntenna)
        self.ui.actionCable.triggered.connect(self.onMnuCable)
        self.ui.actionProbe.triggered.connect(self.onMnuProbe)
        self.ui.actionExit.triggered.connect(self.onMnuExit)
        self.ui.actionAddCorrections.triggered.connect(self.onMnuAddCorrs)
        self.ui.actionAddLimits.triggered.connect(self.onMnuAddLimits)
        self.ui.actionAddTestPlan.triggered.connect(self.onMnuAddTestPlan)
        self.ui.actionExport_Tests.triggered.connect(self.onMnuExportTests)
        self.ui.actionImport_Master_KMV.triggered.connect(self.onMnuImportMaster)
        self.ui.actionUpdate_ZKMV.triggered.connect(self.onMnuUpdateZKMV)
        self.ui.actionUpdate_ZZ.triggered.connect(self.onMnuUpdateZZ)

    def disableFunctions(self):
        self.ui.tabWidget.setTabEnabled(0, False)
        self.ui.tabWidget.setTabEnabled(2, False)
        self.ui.tabWidget.setTabEnabled(3, False)
        self.ui.menubar.setEnabled(False)
        self.ui.BtnSetRelatedRoute.setEnabled(False)
        self.ui.BtnShowRelatedRoute.setEnabled(False)
        self.ui.BtnSelNone.setEnabled(False)
        self.ui.BtnSelAll.setEnabled(False)
        self.ui.BtnStart.setEnabled(False)
        pass

    def enableFunctions(self):
        self.ui.tabWidget.setTabEnabled(0, True)
        self.ui.tabWidget.setTabEnabled(2, True)
        self.ui.tabWidget.setTabEnabled(3, True)
        self.ui.menubar.setEnabled(True)
        self.ui.BtnSetRelatedRoute.setEnabled(True)
        self.ui.BtnShowRelatedRoute.setEnabled(True)
        self.ui.BtnSelNone.setEnabled(True)
        self.ui.BtnSelAll.setEnabled(True)
        self.ui.BtnStart.setEnabled(True)
        pass

    def onShowRelatedRoutes(self):
        sRR = ShowRelatedRoutes.ShowRelatedRoutes()
        sRR.ds = self.ds
        sRR.findRoutes()
        sRR.show()
        pass

    def onSetRelatedRoutes(self):
        addList = []
        sRR = ShowRelatedRoutes.ShowRelatedRoutes()
        sRR.ds = self.ds
        sRR.findRoutes()

        cR = Routing.Routing()
        cR.loadRoutes()

        for x in sRR.routesList:
            if x not in cR.routesList:
                if not x in addList:
                    addList.append(x)
                    cR.addEmptyRoute(x)

        cR.close()
        sRR.close()
        _mText = 'you have to complete the new routes: {0}'.format(addList)
        QtGui.QMessageBox.information(MainForm, 'TMV3', _mText, QtGui.QMessageBox.Ok)

        cR = Routing.Routing()
        cR.loadRoutes()
        cR.showDialog()

        pass

    def TestRelatedRoutes(self):
        addList = []
        sRR = ShowRelatedRoutes.ShowRelatedRoutes()
        sRR.ds = self.ds
        sRR.findRoutes()

        cR = Routing.Routing()
        cR.loadRoutes()

        for x in sRR.routesList:
            if x not in cR.routesList:
                if not x in addList:
                    addList.append(x)

        cR.close()
        sRR.close()
        if len(addList) > 0:
            _mText = 'following routes are not defined: {0}. \nRouting will be disabled !'.format(addList)
            QtGui.QMessageBox.information(MainForm, 'TMV3', _mText, QtGui.QMessageBox.Ok)
            self.routeFlag = False
            return False
        else:
            self.routeFlag = True
            return True
        pass

  #  def onSetMasterID(self, id):
   #     self.masterID = id

    def firstStart(self):
        if platform.system() == 'Linux':
            # TMV3 on Linux should be installed on Opt://TMV3
            pass
        else:
            pass

    def onShowMessageB(self, text):
        QtGui.QMessageBox.information(self, 'TMV3', text, QtGui.QMessageBox.Ok)

        pass

    def onShowMessageA(self, text):
        print('ShowMessageA')
        #Message from foreign thread => access gui via qt-signal
        if isinstance(text, bytes):  #may be text is packed
            stext = pickle.loads(text)

        else:
            stext = text
        self.signalShowMessage.emit(stext)
        pass

    def startServerGraph(self):
        self.serverGraph = ServerGraph.ServerGraph()
        self._sg = threading.Thread(target=self.serverGraph.start)
        self._sg.daemon = False
        self._sg.start()

    def startWorkbench(self):
        #        self.statusBar_label.setStyleSheet('QLabel {color: black}')
        #        self.statusBar_label.setText("WB: %s" %self.workBenchDB)

        #starting Workbench as background daemon to handle data base access
        self.workBench = Workbench.Workbench(self.workBenchDB)
        self._t = threading.Thread(target=self.workBench.start)
        self._t.daemon = True
        self._t.start()

        self.ui.actionOpen.setEnabled(True)
        self.ui.actionClose.setEnabled(True)

    def stopWorkbench(self):
        self.workBench.stop()
        try:
            self._t.join(1)
        except Exception as _err:
            logging.exception(_err)
            return 0
        return 1


    def on_context_menu_SetUps(self, point):
        self.popMenuSetUp.exec_(self.ui.tableWidget.mapToGlobal(point))

    def onTabChanged(self, idx):
        if idx == 0:
            self.resize(self.uiWidth, self.uiHeight)
            self.testModul.fillDialog()
        if idx == 1:
            #controller
            self.testModul.loadCurrentTDS()
            self.resize(350, 750)
        if idx == 2:
            self.resize(300, 700)
        if idx == 3:
            self.resize(300, 700)
        pass

    #
    #...Controller-Functions.........
    #
    def getPauseFlag(self):
        print('getPauseFlag')
        return False

    def onBtnStart(self):

        _mode = self.startOption

        if _mode == 'ZK' or _mode == 'SK':
            if self.testModul.masterID == 0:
                _ret = QtGui.QMessageBox.information(self, 'TMV3', 'no Master-KMV defined. Proceed ?',
                                                     QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                if _ret == QtGui.QMessageBox.No:
                    return

        if not self.startPosSet:
            self.move(0, 0)
            self.startPosSet = True

        self.changeColorTreeView('black')
        try:
            for proc in self.GraphProcessList:
                _data = []
                _data.append((self.signals.GRAPH_STOP))
                self.Server.writeGraph(_data)
                time.sleep(1)
                proc.kill()

            if self.MeasProcess is not None:
                _data = []
                _data.append((self.signals.MEAS_STOP))
                self.Server.writeMeas(_data)
                time.sleep(1)
                self.MeasProcess.kill()
        except Exception as _err:
            print(_err)

        self.MeasProcess = subprocess.Popen([sys.executable, "Measurement.py"], shell=False)
        self.testModul.currentMeasNo += 1
        self.testModul.currentPlotNo = 1
        self.runningFlag = True
        self.disableFunctions()


    def onBtnStop(self):
        # Stop Measurement
        _data = []
        _data.append((self.signals.MEAS_STOP))
        self.Server.writeMeas(_data)
        _data = []
        _data.append((self.signals.GRAPH_STOP))
        self.Server.writeGraph(_data)
        # dispatcher.send(self.signals.MEAS_STOP, dispatcher.Anonymous)
        #os.kill(self.MeasProcess.pid,signa=signal.)
        # psProcess = psutil.Process(pid=self.MeasProcess.pid)
        # psProcess.suspend()

        # self.MeasProcess.kill()
        # self.MeasProcess = None
        #        self.Server.stop()
        self.runningFlag = False
        self.enableFunctions()

    def onBtnPause(self):
        # Pause Measurement
        _data = []
        _data.append((self.signals.MEAS_PAUSE))
        self.Server.writeMeas(_data)
        pass

    def onBtnShowPlot(self, plotID, masterID):
        self.startGraph()
        # wait for new graph
        #
        self.signalWait.clear()
        _ret = self.signalWait.wait(10)
        if not _ret:
            self.onShowMessageA("Graphics did not start")
            self.onBtnStop()
        # draw selected plot
        self.ticket.data = plotID
        dispatcher.send(self.signals.WB_GET_PLOT, dispatcher.Anonymous, self.ticket)
        _plot = self.ticket.data
        self.ticket.data = plotID
        dispatcher.send(self.signals.WB_GET_PLOT_CORR_IDS, dispatcher.Anonymous, self.ticket)
        _corrList = self.ticket.data
        # draw Master
        if masterID != 0:
            #show Masterplot
            _masterPlot = Tpl3Plot('', 0)
            _masterPlot.test_id = masterID
            _masterPlot.plot_title = _plot.plot_title
            self.ticket.data = _masterPlot
            dispatcher.send(self.signals.WB_GET_MASTER_PLOT, dispatcher.Anonymous, self.ticket)
            self.ticket.data = _masterPlot.plot_id
            dispatcher.send(self.signals.WB_GET_PLOT_CORR_IDS, dispatcher.Anonymous, self.ticket)
            _corrListMaster = self.ticket.data

            if self.ticket.data != None:
                _command = []
                _command.append(self.signals.GRAPH_SHOW_PLOT)
                _command.append(_masterPlot)
                _command.append(_corrListMaster)
                _command.append('True')
                self.Server.writeGraph(_command)


        # draw selected plot
        _plot.image = None
        _command = []
        _command.append(self.signals.GRAPH_SHOW_PLOT)
        _command.append(_plot)
        _command.append(_corrList)
        _command.append('False')
        self.Server.writeGraph(_command)
        time.sleep(1)
        self.ticket.plotID = plotID
        # _command=[]
        # _command.append(self.signals.GRAPH_MAKE_THUMBNAIL)
        # _command.append(_plot)
        # _command.append('False')
        # self.Server.writeGraph(_command)

        _command = []
        _command.append(self.signals.GRAPH_STOP)
        self.Server.writeGraph(_command)
        pass

    def onBtnTDStoTDS3(self):
        pass

    def onBtnBackupTPL(self):
        try:
            _name, _ext = os.path.splitext(self.workBenchDB)
            _t = time.strftime("%Y_%m_%d %H_%M", time.gmtime())
            _name = '../Backup/TMV3Workbench ' + _t + _ext

            shutil.copy(self.workBenchDB, _name)
        except Exception as _err:
            self.onShowMessageA(str(_err))
            return

        _text = "Workbench copied to:\n\r {0}".format(_name)
        self.onShowMessageA(_text)

        pass

    def onBtnTKRtoTKR3(self):
        tkrTool = TKRtoTKR3.TKRtoTKR3()
        tkrTool.showNormal()

    def onBtnTLMtoTLM3(self):
        tlmTool = TLMtoTLM3.TLMtoTLM3()
        tlmTool.showNormal()

    def onBtnTDStoTDS3(self):
        tdsTool = TDStoTDS3.TDStoTDS3()
        tdsTool.showNormal()

    #... Menu Functions
    def onMnuExportTests(self):
        _eT = ExportTests.ExportTests(self.startOption)
        _eT.showNormal()

    def onMnuImportMaster(self):
        _iM = ImportMaster.ImportMaster(self.startOption)
        _iM.showNormal()

    def onMnuOpenLimits(self):
        _tm = TableModel(['ID', 'Title', 'Version', 'Date', 'Comment'])
        self.ticket.data = "Limit"
        dispatcher.send(self.signals.WB_GET_LINE_IDS, dispatcher.Anonymous, self.ticket)
        _ids = self.ticket.data.lineIDs
        for _id in _ids:
            self.ticket.data = _id
            dispatcher.send(self.signals.WB_GET_LINE, dispatcher.Anonymous, self.ticket)
            _line = self.ticket.data
            _tm.addData([_line.line_id, _line.title, _line.version, _line.date, _line.comment])

        choose = Choose(_tm,'Limit')

        choose.exec()
        if choose.ret:
            _ID = _tm.data(choose.sel[0], Qt.DisplayRole)
            editLimit = Line.Line(self, _ID, False)
            editLimit.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            editLimit.showNormal()

    def onMnuAntenna(self):
        _tm = TableModel(['ID', 'Title', 'Version', 'Date', 'Comment'])
        self.ticket.data = "Antenna"
        dispatcher.send(self.signals.WB_GET_LINE_IDS, dispatcher.Anonymous, self.ticket)
        _ids = self.ticket.data.lineIDs
        if len(_ids) == 0:
            QtGui.QMessageBox.information(MainForm, 'TMV3', 'no antennas found', QtGui.QMessageBox.Ok)
            return
        for _id in _ids:
            self.ticket.data = _id
            dispatcher.send(self.signals.WB_GET_LINE, dispatcher.Anonymous, self.ticket)
            _line = self.ticket.data
            _tm.addData([_line.line_id, _line.title, _line.version, _line.date, _line.comment])

        choose = Choose(_tm, 'Antenna')

        choose.exec()

        if choose.ret:
            _ID = _tm.data(choose.sel[0], Qt.DisplayRole)
            editLine = Line.Line(self, _ID, False)
            editLine.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            editLine.showNormal()


    def onMnuCable(self):
        _tm = TableModel(['ID', 'Title', 'Version', 'Date', 'Comment'])
        self.ticket.data = "Cable"
        dispatcher.send(self.signals.WB_GET_LINE_IDS, dispatcher.Anonymous, self.ticket)
        _ids = self.ticket.data.lineIDs
        if len(_ids) == 0:
            QtGui.QMessageBox.information(self, 'TMV3', 'no cables found', QtGui.QMessageBox.Ok)
            return
        for _id in _ids:
            self.ticket.data = _id
            dispatcher.send(self.signals.WB_GET_LINE, dispatcher.Anonymous, self.ticket)
            _line = self.ticket.data
            _tm.addData([_line.line_id, _line.title, _line.version, _line.date, _line.comment])

        choose = Choose(_tm, 'Cable')

        choose.exec()
        if choose.ret:
            _ID = _tm.data(choose.sel[0], Qt.DisplayRole)
            editLine = Line.Line(self, _ID, False)
            editLine.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            editLine.showNormal()
            # self.onMnuCable()


    def onMnuProbe(self):
        _tm = TableModel(['ID', 'Title', 'Version', 'Date', 'Comment'])
        self.ticket.data = "Probe"
        dispatcher.send(self.signals.WB_GET_LINE_IDS, dispatcher.Anonymous, self.ticket)
        _ids = self.ticket.data.lineIDs
        if len(_ids) == 0:
            QtGui.QMessageBox.information(self, 'TMV3', 'no probes found', QtGui.QMessageBox.Ok)
            return
        for _id in _ids:
            self.ticket.data = _id
            dispatcher.send(self.signals.WB_GET_LINE, dispatcher.Anonymous, self.ticket)
            _line = self.ticket.data
            if _line.masterID == 0:
                _tm.addData([_line.line_id, _line.title, _line.version, _line.date, _line.comment])

        choose = Choose(_tm, 'Probes')

        choose.exec()
        if choose.ret:
            _ID = _tm.data(choose.sel[0], Qt.DisplayRole)
            editLine = Line.Line(self, _ID, False)
            editLine.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            editLine.showNormal()


    def onMnuAddCorrs(self):
        addLine = AddLines.AddLine('Corr')
        addLine.showNormal()
        pass

    def onMnuAddLimits(self):
        addLine = AddLines.AddLine('Limit')
        addLine.showNormal()
        pass

    def onMnuAddTestPlan(self):
        pass

    def onMnuUpdateZZ(self):
        print("onMnuUpdateZZ")
        izz = ImportZZ()
        izz.showDialog()

    def onMnuUpdateZKMV(self):
        print("onMnuUpdateZKMV")
        izz = ImportZKMV()
        izz.showDialog()

    def onMnuRoutes(self):
        editRoutes = Routing.Routing()
        editRoutes.loadRoutes()
        editRoutes.showDialog()

    def onMnuExit(self):
        for proc in self.GraphProcessList:
            proc.kill()
        self.Server.stop()
        self.close()

    def openWorkbench(self, mode_new):
        if mode_new:
            pass
        else:
            _filename = QtGui.QFileDialog.getOpenFileName(self, "Open Workbench", "", "Workbench (*.tpl3)")
            if (not _filename == ""):
                if self.workBench != None:
                    if self.stopWorkbench() == 0:
                        return 0

                self.startWorkbench()



            #            testDescription = TestDescription.TestDescription(True)
            #            testDescription.showNormal()
        pass

    def onMnuOpenWorkbench(self):
        self.openWorkbench(False)
        pass

    def timeOutMeasurementStart(self):
        # Measurement not started => error
        logging.info("Measurement not started")
        self.FlagError = True
        self.onStop()

    def onPlotComplete(self):
        print('Plot Complete')
        _command = []
        _command.append(self.signals.GRAPH_MAKE_THUMBNAIL)
        _command.append(self.ticket.plotID)
        _command.append('False')
        self.Server.writeGraph(_command)
        # no direct access to ui via thread
        self.signalCollapseTreeview.emit()

    def collapseTreeView(self):
        self.ui.treeView.collapseAll()

    def onPlotThumbnail(self):
        print("Thumbnail ready")
        dispatcher.send(self.signals.WB_SET_IMAGE, dispatcher.Anonymous, self.ticket)

    def onGoOn(self):
        #1 Measurement complete, last action was writing thumbnail.
        # next one please
        _command = []
        _command.append(self.signals.MEAS_GOON)
        self.Server.writeMeas(_command)
        pass

    def onMeasResult(self, result):
        # dispatcher.send(self.signals.WB_GET_PLOT_INFO, dispatcher.Anonymous,self.ticket.plotID)
        _command = []
        _command.append(self.signals.GRAPH_RESULT)
        _command.append(result)
        self.Server.writeGraph(_command)

        _row = self.testModul.measTableModel.rowCount()
        _idx = self.testModul.measTableModel.index(_row - 1, 3)
        self.testModul.measTableModel.setData(_idx, result)
        self.ticket.data = result
        dispatcher.send(self.signals.WB_SET_RESULT, dispatcher.Anonymous, self.ticket)

        pass

    #...Tool-Functions .........................................................

    def onJobComplete(self):
        # Close process Measurement
        print("Controller: JobComplete")
        try:
            #self.MeasProcess.kill()
            self.ui.BtnStop.click()
            self.onShowMessageA('Job complete')
            # QtGui.QMessageBox.information(self.MainFrom, 'TMV3', 'Job complete', QtGui.QMessageBox.Ok)

        except Exception as _err:
            #loggin.information(self, 'TMV3','Cannot stop Measurement Subprocess', Ok.Ok)
            logging.exception(_err)
            return 0

    def onBtnTraceRestart(self):
        # Restart Sweep
        QtGui.QMessageBox.information(self, 'TMV3', 'sorry, not yet implemented', QtGui.QMessageBox.Ok)


    #--- Treeview Functions ----------------------------------------------------------------------
    #treeview functions are slow, because each check-change has a commit in job table as a consequence
    def initTreeView(self):
        if not self.routeFlag:
            _routeFlag = False
            self.ui.lbRouteStatus.setStyleSheet("QLabel {color: red}")
            self.ui.lbRouteStatus.setToolTip("routing disabled")
        else:
            _routeFlag = True
            self.ui.lbRouteStatus.setStyleSheet("QLabel {color: green}")
            self.ui.lbRouteStatus.setToolTip("routing enabled")

        try:
            self.model.clear()
            self.model.itemChanged.disconnect()
            _parent_item_plot = self.model.invisibleRootItem()
            _item = QtGui.QStandardItem(self.ds.db.title)
            _s = 'current Testplan:  ' + self.ds.db.title + ' ' + self.ds.db.version
            self.statusBar_label1.setText(_s)
            self.statusBar_label1.repaint()
            #y= ctypes.cast(id(item), ctypes.py_object).value

            # _item.setToolTip(self.dataSetFileName)
            self.model.setHorizontalHeaderItem(0, _item)

            for _member_plot in self.ds.db.plot_list:
                assert isinstance(_member_plot, DatasetPlot)
                _item = QtGui.QStandardItem(_member_plot.title)
                _item.setCheckable(True)
                #x = self.model.indexFromItem(_item)
                _item.setCheckState(QtCore.Qt.Checked)
                _parent_item_plot.appendRow(_item)
                _parent_item_routine = _item


                #' add Plot to JobTable'
                # _item.setIcon(QtGui.QIcon('TestIcon.png'))
                _item.setData(self.JTable.CurrentJob)
                self.JTable.addJob(1, 'Plot', id(_item), _member_plot.id_plot, _member_plot.title, _member_plot)
                #_plot_item = self.model.indexFromItem(_item)

                for _member_routine in _member_plot.routine_list:
                    assert isinstance(_member_routine, DatasetRoutine)
                    _item = QtGui.QStandardItem(_member_routine.title)
                    _item.setCheckable(True)
                    _item.setCheckState(QtCore.Qt.Checked)
                    _parent_item_routine.appendRow(_item)
                    _parent_item_setting = _item

                    #' add Routine to JobTable'
                    _item.setData(self.JTable.CurrentJob)
                    self.JTable.addJob(1, 'Routine', id(_item), _member_routine.id_routine, _member_routine.title,
                                       _member_routine)

                    if not (_member_routine.limits == None):
                        _limitLines = eval(_member_routine.limits)
                        for _member_line in _limitLines:
                            _item = QtGui.QStandardItem(_member_line[0])
                            _item.setCheckable(True)
                            _item.setCheckState(QtCore.Qt.Checked)
                            _parent_item_setting.appendRow(_item)

                            #' add Limit to JobTable'
                            _item.setData(self.JTable.CurrentJob)
                            _limit = Tpl3Lines("", 0)
                            _limit.type = 'Limit'
                            _limit.title = _member_line[0]
                            _limit.version = _member_line[1]
                            self.ticket.data = _limit
                            dispatcher.send(self.signals.WB_GET_LINE_EXISTS, dispatcher.Anonymous, self.ticket)
                            if _limit.line_id == 0:
                                _err = "Limit {0} not found".format(str(_member_line[0]))
                                QtGui.QMessageBox.information(self, 'TMV3', _err, QtGui.QMessageBox.Ok)
                                return
                            self.JTable.addJob(1, 'Limit', id(_item), 0, _member_line[0][0], _limit)

                    if not _member_routine.lines == None:
                        _lines = eval(_member_routine.lines)
                        for _member_line in _lines:
                            _item = QtGui.QStandardItem(_member_line[0])
                            _item.setCheckable(True)
                            _item.setCheckState(QtCore.Qt.Checked)
                            _parent_item_setting.appendRow(_item)

                            #' add Line to JobTable'
                            _item.setData(self.JTable.CurrentJob)
                            self.JTable.addJob(1, 'Line', id(_item), 0, _member_line[0], _member_line)

                    for _member_setting in _member_routine.setting_list:
                        assert isinstance(_member_setting, DatasetSetting)
                        _item = QtGui.QStandardItem(_member_setting.title)
                        _item.setCheckable(True)
                        _item.setCheckState(QtCore.Qt.Checked)
                        _parent_item_setting.appendRow(_item)
                        _parent_item_trace = _item

                        #' add Setting to JobTable'
                        _item.setData(self.JTable.CurrentJob)
                        self.JTable.addJob(1, 'Setting', id(_item), _member_setting.id_setting, _member_setting.title,
                                           _member_setting)

                        # add Route to JobTable
                        if _member_setting.route != None and _routeFlag:
                            self.ticket.data = _member_setting.route
                            dispatcher.send(self.signals.WB_GET_ROUTE, dispatcher.Anonymous, self.ticket)
                            route = self.ticket.data
                            if route.id <= 0:
                                _text = 'Setting {0} \r\nno such Route: {1} \r\nDisable routine ?'.format(
                                    _member_setting.title, route.alias)
                                #self.onShowMessageA(_text)
                                _ret = QtGui.QMessageBox.information(self, 'TMV3', _text,
                                                                     QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                                if _ret:
                                    self.ui.lbRouteStatus.setStyleSheet("QLabel {color: red}")
                                    self.ui.lbRouteStatus.setToolTip("routing disabled")
                                    _routeFlag = False
                            else:
                                assert isinstance(route, Tpl3Routes)
                                _item = QtGui.QStandardItem(route.alias)
                                _item.setCheckable(True)
                                _item.setCheckState(QtCore.Qt.Checked)
                                _parent_item_trace.appendRow(_item)

                                #' add route to JobTable'
                                _item.setData(self.JTable.CurrentJob)
                                self.JTable.addJob(1, 'Route', id(_item), route.id, route.alias, route)

                                #' add antenna-object to JobTable'
                                if route.antennaID != -1:
                                    self.ticket.data = route.antennaID
                                    dispatcher.send(self.signals.WB_GET_LINE, dispatcher.Anonymous, self.ticket)
                                    antenna = self.ticket.data
                                    self.JTable.addJob(1, 'Antenna', 0, antenna.line_id, antenna.title, antenna)

                                #' add cable-object to JobTable'
                                if route.cableID != -1:
                                    self.ticket.data = route.cableID
                                    dispatcher.send(self.signals.WB_GET_LINE, dispatcher.Anonymous, self.ticket)
                                    cable = self.ticket.data
                                    self.JTable.addJob(1, 'Cable', 0, cable.line_id, cable.title, cable)

                                #' add probe-object to JobTable'
                                if route.probeID != -1:
                                    self.ticket.data = route.probeID
                                    dispatcher.send(self.signals.WB_GET_LINE, dispatcher.Anonymous, self.ticket)
                                    probe = self.ticket.data
                                    self.JTable.addJob(1, 'Probe', 0, probe.line_id, probe.title, probe)

                                #' add Relais-object to JobTable'
                                if route.relaisID != -1:
                                    self.ticket.data = route.relaisID
                                    dispatcher.send(self.signals.WB_GET_RELAIS, dispatcher.Anonymous, self.ticket)
                                    matrix = self.ticket.data
                                    self.JTable.addJob(1, 'Matrix', 0, matrix.id, matrix.title, matrix)

                        for _member_trace in _member_setting.trace_list:
                            assert isinstance(_member_trace, DatasetTrace)
                            _item = QtGui.QStandardItem(_member_trace.title)
                            _item.setCheckable(True)
                            _item.setCheckState(QtCore.Qt.Checked)
                            _parent_item_trace.appendRow(_item)

                            #' add Trace to JobTable'
                            _item.setData(self.JTable.CurrentJob)
                            self.JTable.addJob(1, 'Trace', id(_item), _member_trace.id_trace, _member_trace.title,
                                               _member_trace)

            self.ui.treeView.setModel(self.model)
            self.model.itemChanged.connect(self.onItemChanged)
        except Exception as err:
            print(err)
            return False
        return True

    def setScrollBar(self):
        area = QtGui.QScrollArea(self.ui.treeView.parent())
        vbar = area.verticalScrollBar()
        vbar.setValue(vbar.maximum())

    def onBtnSelAll(self):
        self.model.itemChanged.disconnect()
        self.JTable.beginChangeJob()
        self.checkBranch(self.model.invisibleRootItem())
        self.JTable.endChangeJob()
        self.model.itemChanged.connect(self.onItemChanged)
        pass

    def onBtnSelNone(self):
        self.model.itemChanged.disconnect()
        self.JTable.beginChangeJob()
        self.uncheckBranch(self.model.invisibleRootItem())
        self.JTable.endChangeJob()
        self.model.itemChanged.connect(self.onItemChanged)
        pass

    def onItemChanged(self, item):
        # disable signal during updating the treeView
        self.model.itemChanged.disconnect()
        self.JTable.beginChangeJob()
        if item.checkState() == QtCore.Qt.Checked:
            self.JTable.activateJob(item.data())
            #set 'checked' for all parents
            temp_item = item
            while temp_item.parent() != None:
                temp_item = temp_item.parent()
                temp_item.setCheckState(QtCore.Qt.Checked)
                self.JTable.activateJob(temp_item.data())

            if item.hasChildren():
                self.checkBranch(item.child(0))
                #  self.JTable.activateJob(item.data())
        else:
            self.JTable.deactivateJob(item.data())
            if item.hasChildren():
                self.uncheckBranch(item.child(0))
                self.JTable.deactivateJob(item.data())
        self.JTable.endChangeJob()
        self.model.itemChanged.connect(self.onItemChanged)

    def uncheckBranch(self, item):
        if item == self.model.invisibleRootItem():
            parentItem = item
        else:
            parentItem = item.parent()
        ret = parentItem.rowCount()
        parentItem.setCheckState(QtCore.Qt.Unchecked)
        if parentItem != self.model.invisibleRootItem():
            self.JTable.deactivateJob(parentItem.data())

        for index in range(ret):
            childItem = parentItem.child(index)
            childItem.setCheckState(QtCore.Qt.Unchecked)
            self.JTable.deactivateJob(childItem.data())
            if childItem.hasChildren():
                self.uncheckBranch(childItem.child(0))

    def checkBranch(self, item):
        if item == self.model.invisibleRootItem():
            parentItem = item
        else:
            parentItem = item.parent()
        ret = parentItem.rowCount()
        parentItem.setCheckState(QtCore.Qt.Checked)
        if parentItem != self.model.invisibleRootItem():
            self.JTable.activateJob(parentItem.data())

        for index in range(ret):
            childItem = parentItem.child(index)
            childItem.setCheckState(QtCore.Qt.Checked)
            self.JTable.activateJob(childItem.data())
            if childItem.hasChildren():
                self.checkBranch(childItem.child(0))

    def changeColorTreeView(self, color):
        self.model.itemChanged.disconnect()
        _brush = QtGui.QBrush(color)
        _root_item = self.model.invisibleRootItem()

        if _root_item.hasChildren():
            _item = _root_item.child(0)
            _item.setForeground(_brush)
            if _item.hasChildren():
                self.changeColorTreeView2(_item.child(0), color)

        self.model.itemChanged.connect(self.onItemChanged)

    def changeColorTreeView2(self, item, color):
        #recursive handler for all items
        _brush = QtGui.QBrush(color)
        _parent_item = item.parent()
        _ret = _parent_item.rowCount()
        for _index in range(_ret):
            _item = _parent_item.child(_index)
            _item.setForeground(_brush)
            if _item.hasChildren():
                self.changeColorTreeView2(_item.child(0), color)

    def onItemComplete(self, idx):
        self.model.itemChanged.disconnect(self.onItemChanged)
        item = ctypes.cast(idx[1], ctypes.py_object).value
        Brush = QtGui.QBrush(QtGui.QColor('lime'))
        item.setForeground(Brush)
        self.model.itemChanged.connect(self.onItemChanged)

    def onItemActive(self, idx):
        self.model.itemChanged.disconnect(self.onItemChanged)
        assert isinstance(self.ui.treeView, QtGui.QTreeView)
        item = ctypes.cast(idx[1], ctypes.py_object).value
        Brush = QtGui.QBrush(QtGui.QColor('red'))
        item.setForeground(Brush)
        ditem = item.parent()
        while ditem != None:
            _index = self.model.indexFromItem(ditem)
            self.ui.treeView.expand(_index)
            ditem = ditem.parent()
            # self.ui.treeView.expandToDepth(self.depth(item))
        self.setScrollBar()
        self.model.itemChanged.connect(self.onItemChanged)

    def depth(self, item):
        depth = 0
        while item is not None:
            item = item.parent()
            depth += 1
        return depth

    def onMeasStarted(self):
        Kommando = []
        print("Server: Meas gestartet")
        self.timer.cancel()
        Kommando.append(self.signals.JOB_TABLE)

        self.Server.writeMeas(Kommando)

    def onMeasError(self):
        print("Meas Error")
        try:
            #self.MeasProcess.kill()
            self.ui.BtnStop.click()
            logging.error('Meas Error-Stop')
        except Exception as _err:
            #loggin.information(self, 'TMV3','Cannot stop Measurement Subprocess', Ok.Ok)
            logging.exception(_err)
            return 0

    def onLoadTDS(self):
        #-loads ActiveTestPlan to TreeView

        self.ds = Dataset(os.path.abspath(os.path.join(self.workingDir, 'ActiveTestPlan.TDS3')))
        if self.ds.read():
            # self.ds.filename
            #remember current dataset
            #self.config['ControllerDefaults']['current_TDS'] = "ActiveTestPlan.TDS3"
            #self.config['MeasurementDefaults']['job_table_path'] = 'jobTable.tjt3'

            #with open('../TMV3.ini','w')as configfile:
            #    self.config.write(configfile)
            self.TestRelatedRoutes()
            self.initTreeView()
            #            self.controlTreeView.onLoadTDS()
            self.ui.BtnStart.setEnabled(True)
            self.ui.BtnPause.setEnabled(True)
            self.ui.BtnStop.setEnabled(True)
            self.ui.BtnTraceRestart.setEnabled(True)
            #ret = self.config['MeasurementDefaults']['job_table_save_to_file']

            #if ret == "1":
            #with open(self.config['MeasurementDefaults']['job_table_path'],'wb') as f:
            #pickle.dump(self.JTable,f,pickle.HIGHEST_PROTOCOL)
        self.ui.setCursor(QtCore.Qt.ArrowCursor)

    # --- Graphic Functions -----------------------------------------------------------------------------------
    # ---
    def startGraph(self):

        if len(self.GraphProcessList) > 0:
            _command = []
            _command.append(self.signals.GRAPH_STOP)
            self.Server.writeGraph(_command)
        time.sleep(1)
        _offset = len(self.GraphProcessList) * 40
        _td = self.controllerStartTime - datetime.now()
        _tds = int(_td.total_seconds())
        _name = str(_tds)
        self.GraphProcess = subprocess.Popen([sys.executable, 'Graph.py', str(_offset), _name], shell=False)
        self.GraphProcessList.append(self.GraphProcess)

        self.Server.graphName = "Graph" + _name

    def setGraphScreenPosition(self):
        if not self.initGraphScreenPosition:
            resolution = QtGui.QDesktopWidget().screenGeometry()
            self.screenWidth = resolution.width()
            self.screenHeight = resolution.heigth()
            #self.graphWidth =
            self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                      (resolution.height() / 2) - (self.frameSize().height() / 2))
        pass

    def onGraphStarted(self):
        #self.signalWait.emit()
        self.graphStarted = True
        self.signalWait.set()
        pass

    def onGraphStopped(self):
        _command = []
        _command.append(self.signals.GRAPH_STOP)
        self.Server.writeGraph(_command)

        _command = []
        _command.append(self.signals.MEAS_GOON)
        self.Server.writeMeas(_command)

    pass

    def onGraphError(self):
        pass

    def onGraphNewPlot(self, data):
        #Measurement generates new Plot.
        #send info to Graphic
        #send data to Workbench


        self.graphStarted = False
        self.startGraph()

        #   while not self.graphStarted:
        #       time.sleep(1)
        self.signalWait.clear()
        #       _ret = self.signalWait.wait(5)
        _ret = self.signalWait.wait()
        if not _ret:
            self.onShowMessageA("Graphics did not start")
            self.onBtnStop()
            #  _ret =  dispatcher.send(self.signals.WB_GET_TICKET, dispatcher.Anonymous)[0]
            #  self.ticket = _ret[1]

        # draw Master
        _mode = self.startOption
        if (_mode == 'ZK' or _mode == 'SK') and self.testModul.masterID != 0:
            #show Masterplot
            _masterPlot = Tpl3Plot('', 0)
            _masterPlot.test_id = self.testModul.masterID
            _masterPlot.plot_title = data.plot_title
            self.ticket.data = _masterPlot
            dispatcher.send(self.signals.WB_GET_MASTER_PLOT, dispatcher.Anonymous, self.ticket)
            if self.ticket.data != None:
                _command = []
                _command.append(self.signals.GRAPH_SHOW_PLOT)
                _command.append(_masterPlot)
                _command.append('True')
                self.Server.writeGraph(_command)

        assert isinstance(data, Tpl3Plot)
        _d = datetime.now()
        data.date_time = datetime(_d.year, _d.month, _d.day, _d.hour, _d.minute, _d.second).isoformat(' ')

        data.eut = self.testModul.currentTest.eut
        data.serial_no = self.testModul.currentTest.serial_no
        data.user_no = self.testModul.currentTest.user_no
        data.technician = self.testModul.currentTest.technician
        data.company = self.testModul.currentTest.company
        data.model_no = self.testModul.currentTest.model_no
        data.model_name = self.testModul.currentTest.model_name
        data.meas_no = self.testModul.currentMeasNo
        data.plot_no = self.testModul.currentPlotNo
        data.test_id = self.testModul.currentTestID
        data.test_no = self.testModul.currentTest.test_no
        data.plan_title = self.planTitle
        data.tmv3_version = '1.0'
        data.result = '?'
        if self.testModul.ui.RBtnFinal.isChecked():
            data.group = "final"
        else:
            data.group = "try out"
        self.ticket.data = data
        dispatcher.send(self.signals.WB_NEW_PLOT, dispatcher.Anonymous, self.ticket)
        self.testModul.currentPlotNo += 1
        if self.testModul.masterID != 0:
            pass
        # data.plot_title

        self.testModul.measTableModel.addData([data.meas_no, data.plot_no, data.plot_title, data.result,
                                               data.date_time, data.group, '?'])

        _command = []
        _command.append(self.signals.GRAPH_NEW_PLOT)
        _command.append(data)
        self.Server.writeGraph(_command)
        pass

    def onNewPlotID(self, id):
        _row = self.testModul.measTableModel.rowCount()
        _idx = self.testModul.measTableModel.index(_row - 1, 6)
        self.testModul.measTableModel.setData(_idx, id)
        self.ticket.plotID = id
        self.testModul.ticket.plotID = id
        self.Server.resumeWorker()

    def onGraphNewLine(self, data):
        #Measurement generates new Line.
        #send info Graphic
        #send Line to Workbench
        _command = []
        _command.append(self.signals.GRAPH_NEW_LINE)
        _command.append(data)
        self.Server.writeGraph(_command)
        #new ticket prevents overwriting in pool
        _ticket = Ticket()
        _ticket.data = data
        _ticket.plotID = self.ticket.plotID

        #self.ticket.data = data
        #  print("Controller: NewLine {0}".format (str(self.ticket.plotID)))
        dispatcher.send(self.signals.WB_ADD_LINE, dispatcher.Anonymous, _ticket)

    def onGraphNewTrace(self, data):
        #Measurement generates new Trace.
        #send info to Workbench and Graphic
        _corList = data.corIDs
        for x in _corList:
            print('LineID', x)

        _command = []
        _command.append(self.signals.GRAPH_NEW_TRACE)
        _command.append(data)
        self.Server.writeGraph(_command)
        self.ticket.data = data
        dispatcher.send(self.signals.WB_ADD_TRACE, dispatcher.Anonymous, self.ticket)

    def closeEvent(self, event):
        #self.MServer.stop()
        #self.GServer.stop()
        #_ret = self.MeasProcess.poll()
        try:
            if not self.MeasProcess == None:
                self.MeasProcess.kill()
            self.stopWorkbench()



        #for _proc in self.GServerList:
        #    _proc.kill()


        except Exception as _err:
            print(_err)

    def testPyhtonRunning(self):
        #if another python process is running (may be from crash) => kill it
        _process_name = 'python.exe'
        _ownPID = os.getpid()
        # print('own',_ownPID)
        _running = [item.split()[1] for item in os.popen('tasklist').read().splitlines()[4:] if
                    _process_name in item.split()]
        if len(_running) > 1:
            for pid in _running:
                _ipid = int(pid)
                if _ipid != _ownPID:
                    #            print('kill',int(pid))
                    os.kill(_ipid, signal.SIGTERM)

    def prStat(self):
        # use of cProfile
        # ---------------
        # self.pr.enable()
        #  e.g.: self.uncheckBranch(self.model.invisibleRootItem())
        # self.pr.disable()
        # self.prStat()

        _s = io.StringIO()
        _sortBy = 'cumulative'
        _ps = pstats.Stats(self.pr, stream=_s).sort_stats(_sortBy)
        _ps.print_stats()
        pass


class Welcome(QtGui.QMainWindow):
    def __init__(self):

        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("Welcome.ui", self)
        self.centerOnScreen()
        self.config = configparser.ConfigParser()
        self.config.read('TMV3.ini')

        self.ui.lineEdit.setText(self.config['Welcome']['name'])
        self.ui.lineEdit_2.setText(self.config['Welcome']['lab'])

        _option = self.config['Welcome']['start_option']
        if _option == 'ZK':
            self.ui.RBtnKMVZ.setChecked(True)
        if _option == 'SK':
            self.ui.RBtnKMVS.setChecked(True)
        if _option == 'ZZ':
            self.ui.RBtnZZ.setChecked(True)
        if _option == 'SZ':
            self.ui.RBtnSZ.setChecked(True)

        self.ui.BtnOk.clicked.connect(self.onBtnOk)
        self.ui.BtnCancel.clicked.connect(self.onBtnCancel)

        pass

    def onBtnOk(self):
        if self.ui.RBtnKMVZ.isChecked():
            self.config['Welcome']['start_option'] = 'ZK'
        if self.ui.RBtnKMVS.isChecked():
            self.config['Welcome']['start_option'] = 'SK'
        if self.ui.RBtnZZ.isChecked():
            self.config['Welcome']['start_option'] = 'ZZ'
        if self.ui.RBtnSZ.isChecked():
            self.config['Welcome']['start_option'] = 'SZ'

        if self.ui.checkBox.isChecked():
            self.config['Welcome']['show_window'] = '0'
        else:
            self.config['Welcome']['show_window'] = '1'

        self.config['Welcome']['name'] = self.ui.lineEdit.text()
        self.config['Welcome']['lab'] = self.ui.lineEdit_2.text()

        with open('TMV3.ini', 'w')as configfile:
            self.config.write(configfile)

            # self.window2.closed.connect(self.show)
        self.window2 = MainForm(self)
        self.window2.show()
        self.hide()


    def onBtnCancel(self):

        self.close()

    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))


def main():
    config = configparser.ConfigParser()
    config.read('TMV3.ini')
    _ret = config['Welcome']['show_window']
    if (_ret == '1'):
        app = QtGui.QApplication(sys.argv)
        window1 = Welcome()
        window1.show()
        sshFile = "c:/tmv3/templates/darkorange.css"
        with open(sshFile, "r") as fh:
            app.setStyleSheet(fh.read())
        # QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('plastique')) # setting the style
        sys.exit(app.exec())
    else:
        app = QtGui.QApplication(sys.argv)
        window1 = MainForm()
        window1.show()
        # QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('plastique')) # setting the style
        sshFile = "c:/tmv3/templates/darkorange.css"
        with open(sshFile, "r") as fh:
            app.setStyleSheet(fh.read())
        sys.exit(app.exec())


if __name__ == "__main__":
    import sys

    main()



