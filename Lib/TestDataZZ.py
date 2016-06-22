__author__ = 'Heinz'


from NeedfullThings import *
from DB_Handler_TPL3 import *
from Workbench import  Ticket
from datetime import datetime
from Protocol import Protocol
from GetSerialNo import GetSerialNo
import configparser



class TestDataZZ(QtGui.QWidget):
    signalDisplayUpdate = pyqtSignal()
    def __init__(self, parent=None):
        super(QtGui.QWidget, self).__init__(parent)
        self.test = self.ui = uic.loadUi("TestDataZZ.ui", self)
        self.ticket = Ticket()
        self.signals = Signal()
        self.config = configparser.ConfigParser()
        self.config.read('TMV3.ini')
        self.test = None

        self.GraphProcess = None
        self.GraphProcessList = []
        self.controllerStartTime = datetime.now()

        self.ui.BtnMarkAsFinal.clicked.connect(self.onBtnMarkAsFinal)
        self.ui.BtnMarkAsTryOut.clicked.connect(self.onBtnMarkAsTryOut)
        self.ui.BtnMarkAsReference.clicked.connect(self.onBtnMarkAsReference)
        self.ui.BtnReport.clicked.connect(self.onBtnReport)
        self.ui.BtnShowPlot.clicked.connect(self.onBtnShowPlot)
        self.ui.BtnFRwd.clicked.connect(self.onBtnFRwd)
        self.ui.BtnRwd.clicked.connect(self.onBtnRwd)
        self.ui.BtnFwd.clicked.connect(self.onBtnFwd)
        self.ui.BtnFFwd.clicked.connect(self.onBtnFFwd)
        self.ui.BtnExit.clicked.connect(self.onMnuExit)
        self.ui.BtnNewProject.clicked.connect(self.onBtnNewProject)
        self.ui.BtnSaveProject.clicked.connect(self.onBtnSaveProject)
        self.ui.BtnNewTestZZ.clicked.connect(self.onBtnNewTestZZ)
        self.ui.BtnNewTestZK.clicked.connect(self.onBtnNewTestZK)
        self.ui.BtnDelTest.clicked.connect(self.onBtnDelTest)
        self.ui.BtnDelPlot.clicked.connect(self.onBtnDelPlot)
        self.ui.twTest.doubleClicked.connect(self.onTestTableDClick)
        self.ui.twTest.clicked.connect(self.onTestTableClick)

        self.currentTest = TPL3Test('', int(self.config['Current']['current_testID_ZZ']))
        self.currentTestID = int(self.config['Current']['current_testID_ZZ'])
        self.currentProjectID = int(self.config['Current']['current_project_id'])
        self.currentProject = Tpl3Projects
        self.planID_ZZ = int (self.config['Current']['current_planID_ZZ'])
        self.planID_ZK = int (self.config['Current']['current_planID_ZK'])
        self.currentTDS = self.planID_ZZ
        self.lastTDS = ''
        self.currentTestSave = True
        self.masterID = 0
        self.masterTest = TPL3Test
        self.measTableModel = None
        self.testTableModel = None
        self.currentPlotNo = 0
        self.currentMeasNo = 0

        #get current Project
        self.ticket.data = self.currentProjectID
        dispatcher.send(self.signals.WB_GET_PROJECT, dispatcher.Anonymous, self.ticket)
        if self.ticket.data != None:
            self.currentProject = self.ticket.data
            self.currentProjectID = self.ticket.data.id
            self.ui.lbProject.setText(self.currentProject.title)
        self.ticket.testID = self.currentTestID
        self.ticket.data = 'ZZ'
        dispatcher.send(self.signals.WB_GET_TEST, dispatcher.Anonymous, self.ticket)
        if self.ticket.data != None:
            self.currentTest = self.ticket.data
        self.fillDialog()
    # def onLoadTest(self):
    #     if self.currentTestID != None:
    #         self.ticket.data = self.currentTestID
    #         dispatcher.send(self.signals.WB_GET_TEST, dispatcher.Anonymous,self.ticket)
    #         if self.ticket.data != None:
    #             self.currentTest = self.ticket.data
    #             self.fillDescription()

    def onBtnNewTestZZ(self):
        self.BtnNewTest('ZZ',self.planID_ZZ)

    def onBtnNewTestZK(self):
        self.BtnNewTest('ZKMV',self.planID_ZK)
        pass

    def BtnNewTest(self,type,tds):
        sDialog = GetSerialNo()
        sDialog.serialNo = self.currentTest.serial_no
        sDialog.modelNo = self.currentTest.model_no
        sDialog.modelName = self.currentTest.model_name
        sDialog.userField = self.currentTest.user_no
        sDialog.comment = self.currentTest.comment
        sDialog.fillDialog()
        sDialog.exec()
        if sDialog.ret ==  True:
            self.getNewTest(True, type)
            self.currentTDS = tds

            self.currentTest.serial_no = sDialog.serialNo
            self.currentTest.model_no = sDialog.modelNo
            self.currentTest.model_name = sDialog.modelName
            self.currentTest.user_no = sDialog.userField
            self.currentTest.comment = sDialog.comment

            self.ui.leSerialNo.setText(self.currentTest.serial_no)
            self.ui.leModelNo.setText(self.currentTest.model_no)
            self.ui.leModelName.setText(self.currentTest.model_name)
            self.ui.leUserNo.setText(self.currentTest.user_no)
            self.ui.lbProject.setText(self.currentProject.title)
            self.ui.lbTestNo.setText(self.currentTest.test_no)
            self.ui.pteComment.setPlainText(self.currentTest.comment)
            self.selectTest(self.currentTestID)
            self.onBtnSaveProject()
            self.signalDisplayUpdate.emit()

    def getNewTest(self, clone, category):
        if clone:
            self.ticket.data = self.currentTestID
            dispatcher.send(self.signals.WB_CLONE_TEST, dispatcher.Anonymous, self.ticket)
            self.currentTest = self.ticket.data
        else:
            dispatcher.send(self.signals.WB_GET_NEW_TEST, dispatcher.Anonymous, self.ticket)
            self.currentTest = self.ticket.data
            self.currentTest.company = self.config['Welcome']['company']
            self.currentTest.technician = self.config['Welcome']['name']
            self.currentTest.lab = self.config['Welcome']['lab']
            self.currentTest.company = self.config['Welcome']['company']
            self.currentTest.category = category
            self.currentTest.project_id = self.currentProjectID

        if category == 'ZZ':
            self.currentTest.procedure = 'ZONE KMV'
        else:
            self.currentTest.procedure = 'ZONE APP'

        self.currentTest.setup = 'Normal'
        self.currentTestSave = False
        self.currentMeasNo = 0
        self.currentPlotNo = 0
        self.currentTestID = self.currentTest.test_id


        self.currentProject.test_ids.append(self.currentTest.test_id)
        self.ticket.data = self.currentTest
        dispatcher.send(self.signals.WB_UPDATE_TEST, dispatcher.Anonymous, self.ticket)
        self.fillDialog()
        self.saveInitFile()

        # self.config['Current']['current_testID'] = str(self.currentTestID)
        # with open('TMV3.ini', 'w')as configfile:
        #     self.config.write(configfile)



    def loadCurrentTDS(self): # called if tab changed, triggered from controller
        _file =  Tpl3Files("", 0)
        _file.file_id = self.currentTDS
        _file.destination = '../WorkingDir/ActiveTestPlan.TDS3'
        self.ticket.data = _file
        dispatcher.send(self.signals.WB_EXPORT_TDS,dispatcher.Anonymous,self.ticket)
        dispatcher.send(self.signals.CTR_LOAD_TESTPLAN, dispatcher.Anonymous)
        pass

    def onBtnNewProject(self):
        dispatcher.send(self.signals.WB_GET_NEW_POJECT, dispatcher.Anonymous, self.ticket)
        if (self.ticket.data != None):
            self.currentProject = self.ticket.data
            self.currentProject.type = "ZONE_APP"
            self.currentProjectID = self.currentProject.id
            self.getNewTest(False, 'ZZ')
            self.onBtnReport()
            self.ui.leSerialNo.setText(self.currentTest.serial_no)
            self.ui.leModelNo.setText(self.currentTest.model_no)
            self.ui.leModelName.setText(self.currentTest.model_name)
            self.ui.leUserNo.setText(self.currentTest.user_no)
            self.ui.lbProject.setText(self.currentProject.title)
            self.ui.lbTestNo.setText(self.currentTest.test_no)
            self.ui.pteComment.setPlainText(self.currentTest.comment)

            self.fillDialog()
            self.saveInitFile()
        else:
            QtGui.QMessageBox.information(self, 'TMV3', 'could not generate new project', QtGui.QMessageBox.Ok)

        self.saveInitFile()

    def onBtnReport(self):
        proto = Protocol(self.currentTest,self.currentProject)
        proto.exec()
        if proto.ret:
            self.ticket.data = self.currentProject
            dispatcher.send(self.signals.WB_UPDATE_PROJECT, dispatcher.Anonymous,self.ticket)

            self.ticket.data = self.currentTest
            dispatcher.send(self.signals.WB_UPDATE_TEST, dispatcher.Anonymous,self.ticket)

    def cloneDescription(self):
        pass

    def clearTTTable(self):
        if self.testTableModel != None:
            _rows = self.testTableModel.rowCount()
            _idx = self.testTableModel.index(0, 0)
            self.testTableModel.removeRows(0, _rows, _idx)
        pass

    def clearTMTable(self):
        if self.measTableModel != None:
            _rows = self.measTableModel.rowCount()
            _idx = self.measTableModel.index(0, 0)
            self.measTableModel.removeRows(0, _rows, _idx)
        pass

    def onBtnSaveProject(self):
        self.currentTest.serial_no = self.ui.leSerialNo.text()
        self.currentTest.model_no = self.ui.leModelNo.text()
        self.currentTest.model_name = self.ui.leModelName.text()
        self.currentTest.user_no = self.ui.leUserNo.text()
        self.currentTest.comment = self.ui.pteComment.toPlainText()

        self.ticket.data = self.currentTest
        dispatcher.send(self.signals.WB_UPDATE_TEST, dispatcher.Anonymous, self.ticket)
        if self.ticket.data == None:
            QtGui.QMessageBox.information(self, 'TMV3', 'could not save current test', QtGui.QMessageBox.Ok)
        else:
            QtGui.QMessageBox.information(self, 'TMV3', 'save completed', QtGui.QMessageBox.Ok)


        self.fillDialog()

    def onBtnMarkAsReference(self):

        _tm = TableModel(['CertificationNo', 'EUT-Name', 'Date', 'ID'])

        _idx = self.ui.twTest.selectedIndexes()
        if len(_idx) == 0:
            return
        _ret = self.testTableModel.data(_idx[3], Qt.DisplayRole)
        if _ret == "ZKMV-Master":
            self.testTableModel.setData(_idx[3], "ZKMV")
        else:
            self.testTableModel.setData(_idx[3], "ZKMV-Master")
            _id = self.testTableModel.data(_idx[4], Qt.DisplayRole)
            _data = []
            _data.append(_id)
            _data.append('final')
            self.ticket.data = _data
        #    dispatcher.send(self.signals.WB_SET_GROUP, dispatcher.Anonymous, self.ticket)
            _d = self.currentTest.date_time
            _t = ('{}{}{}??{}{}?'.format(_d[2:4],_d[5:7],_d[8:10],_d[11:13],_d[14:16]))
            self.ui.leZNo.setText(_t)
            _text = 'please complete CertificationNo'
            QtGui.QMessageBox.information(self, 'TMV3',_text)

    def onBtnShowPlot(self):
        _idx = self.ui.twMeas.selectedIndexes()
        if len(_idx) == 0:
            return

        # draw selected plot
        _id = self.measTableModel.data(_idx[6], Qt.DisplayRole)

        dispatcher.send(self.signals.CTR_SHOW_PLOT,dispatcher.Anonymous, _id, self.masterID)

    def onBtnDelPlot(self):
        _idx = self.ui.twMeas.selectedIndexes()
        if len(_idx) == 0:
            return

        # draw selected plot
        _id = self.measTableModel.data(_idx[6], Qt.DisplayRole)
        self.ticket.plotID = _id
        dispatcher.send(self.signals.WB_DEL_PLOT,dispatcher.Anonymous, self.ticket)
        self.fillDialog2()

    def onBtnDelTest(self):
        _idx = self.ui.twTest.selectedIndexes()
        if len(_idx) == 0:
            return

        # draw selected plot
        _id = self.testTableModel.data(_idx[6], Qt.DisplayRole)
        self.ticket.testID = _id
        dispatcher.send(self.signals.WB_DEL_TEST,dispatcher.Anonymous, self.ticket)
        self.fillDialog()
    def onBtnMarkAsFinal(self):
        _idx = self.ui.twTest.selectedIndexes()
        if len(_idx) == 0:
            return
        self.testTableModel.setData(_idx[4], "final")

        # _id = self.measTableModel.data(_idx[6], Qt.DisplayRole)
        # _data = []
        # _data.append(_id)
        # _data.append('final')
        # self.ticket.data = _data
        # dispatcher.send(self.signals.WB_SET_GROUP, dispatcher.Anonymous, self.ticket)

        # self.measTableModel.updateView()
        #  s = self.measTableModel.data(_idx[5],Qt.DisplayRole)
        #  print (s)
        pass

    def onBtnMarkAsTryOut(self):
        _idx = self.ui.twTest.selectedIndexes()
        if len(_idx) == 0:
            return
        self.testTableModel.setData(_idx[4], "try out")

        # _id = self.measTableModel.data(_idx[6], Qt.DisplayRole)
        # _data = []
        # _data.append(_id)
        # _data.append('try out')
        # self.ticket.data = _data
        # dispatcher.send(self.signals.WB_SET_GROUP, dispatcher.Anonymous, self.ticket)
        # s = self.measTableModel.data(_idx[5],Qt.DisplayRole)
        # print (s)

    def onBtnFRwd(self):
        self.ticket.data = self.currentProjectID
        dispatcher.send(self.signals.WB_GET_PROJECT_FIRST, dispatcher.Anonymous, self.ticket)
        if self.ticket.data != None:
            self.currentProject = self.ticket.data
            self.currentProjectID = self.ticket.data.id
            self.ui.lbProject.setText(self.currentProject.title)
            self.fillDialog()
            self.saveInitFile()

        pass
    def onBtnRwd(self):
        self.ticket.data = self.currentProjectID
        dispatcher.send(self.signals.WB_GET_PROJECT_PREV, dispatcher.Anonymous, self.ticket)
        if self.ticket.data != None:
            self.currentProject = self.ticket.data
            self.currentProjectID = self.ticket.data.id
            self.ui.lbProject.setText(self.currentProject.title)
            self.fillDialog()
            self.saveInitFile()
    def onBtnFwd(self):
        self.ticket.data = self.currentProjectID
        dispatcher.send(self.signals.WB_GET_PROJECT_NEXT, dispatcher.Anonymous, self.ticket)
        if self.ticket.data != None:
            self.currentProject = self.ticket.data
            self.currentProjectID = self.ticket.data.id
            self.ui.lbProject.setText(self.currentProject.title)
            self.fillDialog()
            self.saveInitFile()

    def onBtnFFwd(self):
        self.ticket.data = self.currentProjectID
        dispatcher.send(self.signals.WB_GET_PROJECT_LAST, dispatcher.Anonymous, self.ticket)
        if self.ticket.data != None:
            self.currentProject = self.ticket.data
            self.currentProjectID = self.ticket.data.id
            self.ui.lbProject.setText(self.currentProject.title)
            self.fillDialog()
            self.saveInitFile()

    def fillDialog(self):

        if self.testTableModel == None:
            self.testTableModel = TableModel(['TestNo','SerialNo','ModelNo','Model Name','Date','TestPlan','ID'])
        else:
            self.clearTTTable()
        for _testID in self.currentProject.test_ids:
            self.ticket.testID = _testID
            self.ticket.data = 'ZZ'
            dispatcher.send(self.signals.WB_GET_TEST, dispatcher.Anonymous, self.ticket)
            if self.ticket.data != None:
                _test = self.ticket.data
                self.testTableModel.addData([_test.test_no,_test.serial_no, _test.model_no, _test.model_name,
                                             _test.date_time, _test.category, _test.test_id])

        self.ui.twTest.setModel(self.testTableModel)
        _header = self.ui.twTest.horizontalHeader()
        _header.setResizeMode(QtGui.QHeaderView.ResizeToContents)


        if not self.selectTest(self.currentTestID):
            return
        else:
            self.fillDialog2()

    def fillDialog2(self):
        self.ui.leSerialNo.setText(self.currentTest.serial_no)
        self.ui.leModelNo.setText(self.currentTest.model_no)
        self.ui.leModelName.setText(self.currentTest.model_name)
        self.ui.leUserNo.setText(self.currentTest.user_no)
        self.ui.lbProject.setText(self.currentProject.title)
        self.ui.lbTestNo.setText(self.currentTest.test_no)
        self.ui.pteComment.setPlainText(self.currentTest.comment)
            #show all plots of current test
        if self.measTableModel == None:
            self.measTableModel = TableModel(['MeasNo', 'PlotNo', 'PlotTitle', 'Result', 'Date', 'Group',
                                           'ID','Group','Image'])
            self.delegate = ImageDelegate(self)
            self.ui.twMeas.setItemDelegateForColumn(8,self.delegate)
            self.ui.twMeas.setColumnWidth(8,200)
        self.measTableModel.beginResetModel()
        self.measTableModel.removeRows(0,self.measTableModel.rowCount())
        self.ticket.testID= self.currentTestID
        self.ticket.data = self.currentTest.test_no
        dispatcher.send(self.signals.WB_GET_PLOT_INFO_IDS, dispatcher.Anonymous, self.ticket)
        _ids = self.ticket.data.ids
        _i = 0
        for _id in _ids:
             self.ticket.data = _id
             dispatcher.send(self.signals.WB_GET_PLOT_INFO, dispatcher.Anonymous, self.ticket)
             _plot = self.ticket.data
             self.measTableModel.addData([_plot.meas_no, _plot.plot_no, _plot.plot_title, _plot.result,
                                      _plot.date_time, _plot.group, _plot.plot_id, _plot.group,_plot.image])
             if _plot.meas_no > self.currentMeasNo:
                 self.currentMeasNo = _plot.meas_no
             self.ui.twMeas.setRowHeight(_i,110)
             _i += 1
        self.ui.twMeas.setModel(self.measTableModel)
        _header = self.ui.twMeas.horizontalHeader()
       # _header.setResizeMode(QtGui.QHeaderView.ResizeToContents)
        # self.ui.twMeas.setColumnHidden(6,True)
        self.ui.twMeas.setColumnWidth(8,200)
        self.ui.twMeas.setColumnWidth(0,40)
        self.ui.twMeas.setColumnWidth(1,40)
        self.ui.twMeas.setColumnWidth(3,70)
        self.ui.twMeas.setColumnHidden(7, True)
        self.ui.twMeas.scrollToBottom()
        self.measTableModel.endResetModel()

    def selectTest(self,id):
        rows = self.testTableModel.rowCount()

        for x in range (0, rows):
            if self.testTableModel.data(self.testTableModel.index(x,6),Qt.DisplayRole) == id:
                self.ui.twTest.selectRow(x)
                self.onTestTableDClick()
                return(True)

        return (False)

    def onTestTableClick(self):
        _idx = self.ui.twTest.selectedIndexes()
        if len(_idx) == 0:
            return
        self.currentTestID = self.testTableModel.data(_idx[6], Qt.DisplayRole)
        self.ticket.testID = self.currentTestID
        dispatcher.send(self.signals.WB_GET_TEST, dispatcher.Anonymous, self.ticket)
        self.currentTest = self.ticket.data
        self.fillDialog2()
    def onTestTableDClick(self):
        return
     #    _idx = self.ui.twTest.selectedIndexes()
     #    if len(_idx) == 0:
     #        return
     #    _id = self.testTableModel.data(_idx[6], Qt.DisplayRole)
     #    _no = self.testTableModel.data(_idx[0], Qt.DisplayRole)
     #    _plan = self.testTableModel.data(_idx[5],Qt.DisplayRole)
     #    _data = []
     #    self.ticket.data = _id
     #    self.currentTestID = _id
     #    dispatcher.send(self.signals.WB_GET_TEST, dispatcher.Anonymous, self.ticket)
     #    self.currentTest = self.ticket.data
     #
     # #   self.fillTableMeas()
     #    if _plan != "ZZ":
     #        self.currentTDS = self.planID_ZK
     #    else:
     #        self.currentTDS = self.planID_ZZ
     #
     #    if self.currentTest != None:
     #        self.ui.leSerialNo.setText(self.currentTest.serial_no)
     #        self.ui.leModelNo.setText(self.currentTest.model_no)
     #        self.ui.leModelName.setText(self.currentTest.model_name)
     #        self.ui.leUserNo.setText(self.currentTest.user_no)


    def onMnuExit(self):
        self.saveInitFile()
        dispatcher.send(self.signals.CTR_EXIT, dispatcher.Anonymous)

    def saveInitFile(self):
        self.config['Current']['current_testID'] = str(self.currentTestID)
        self.config['Current']['current_testid_zz'] = str(self.currentTestID)
        self.config['Current']['current_project_id']= str(self.currentProjectID)
        with open('TMV3.ini', 'w')as configfile:
            self.config.write(configfile)
        pass