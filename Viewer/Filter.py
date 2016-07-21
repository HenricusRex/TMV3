__author__ = 'heinz'


from PyQt4 import uic,QtGui,QtCore
from NeedfullThings import *
from pydispatch import dispatcher
from EngFormat import Format
import configparser
import ast
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from Workbench import Ticket
from DB_Handler_TPL3 import *

class Filter(QtGui.QDialog):
    signalShowMessage = pyqtSignal(str)

    def __init__(self):
        #global model
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("Filter.ui", self)
        sshFile = "../Templates/darkorange.css"
        with open (sshFile,"r") as fh:
            self.setStyleSheet(fh.read())
        self.centerOnScreen()
        self.signals = Signal()
        self.config = configparser.ConfigParser()
        self.config.read('../Lib/TMV3.ini')
        self.workBenchDB = self.config['DataBases']['workbench']
        self.viewTableModel = None
        self.viewTableModel2 = None
        self.selectString = ""
        self.ret = False
        self.sel = []
        #Buttons
        self.ui.BtnSave.clicked.connect(self.onBtnSave)
        self.ui.BtnOk.clicked.connect(self.onBtnOk)
        self.ui.BtnCancel.clicked.connect(self.onBtnCancel)
        self.ui.BtnApply.clicked.connect(self.onBtnApply)
        self.ui.BtnApply2.clicked.connect(self.onBtnApply2)

        self.ui.CBoxCompany.currentIndexChanged.connect(self.onBtnEnable)
        self.ui.CB_CompanyEnable.clicked.connect(self.onBtnEnable)
        self.ui.CB_GroupEnable.clicked.connect(self.onBtnEnable)
        self.ui.CBoxGroup.currentIndexChanged.connect(self.onBtnEnable)
        self.ui.CB_PlotTitleEnable.clicked.connect(self.onBtnEnable)
        self.ui.CBoxPlotTitle.currentIndexChanged.connect(self.onBtnEnable)
        self.ui.CB_RoutineEnable.clicked.connect(self.onBtnEnable)
        self.ui.CBoxRoutine.currentIndexChanged.connect(self.onBtnEnable)
        self.ui.CB_ProjectEnable.clicked.connect(self.onBtnEnable)
        self.ui.CBoxProject.currentIndexChanged.connect(self.onBtnEnable)
        self.ui.CB_DateEditEnable.clicked.connect(self.onBtnEnable)
        self.ui.dateEditFrom.dateChanged.connect(self.onBtnEnable)
        self.ui.dateEditTo.dateChanged.connect(self.onBtnEnable)
        self.ui.CB_ZNoEnable.clicked.connect(self.onBtnEnable)
        self.ui.CB_TestNoEnable.clicked.connect(self.onBtnEnable)
        self.ui.CB_IdEnable.clicked.connect(self.onBtnEnable)
        self.ui.CB_TextEnable.clicked.connect(self.onBtnEnable)
        self.ui.RB_And.clicked.connect(self.onBtnEnable)
        self.ui.RB_Or.clicked.connect(self.onBtnEnable)
        self.ui.CB_ZoneKMV.clicked.connect(self.onBtnEnableA)
        self.ui.CB_ZoneApp.clicked.connect(self.onBtnEnableA)
        self.ui.CB_LevelKMV.clicked.connect(self.onBtnEnableA)
        self.ui.CB_LevelApp.clicked.connect(self.onBtnEnableA)
        self.ui.CB_other.clicked.connect(self.onBtnEnableB)
        self.ui.EdZNo.editingFinished.connect(self.onBtnEnable)
        self.ui.EdTestNo.editingFinished.connect(self.onBtnEnable)
        self.ui.EdID.editingFinished.connect(self.onBtnEnable)
        self.ui.EdText.editingFinished.connect(self.onBtnEnable)

        self.signalShowMessage.connect(self.onShowMessage)
      #  self.ui.tableView_2.cellChanged.connect(self.onCellChanged)
        #self.ui.BtnLoadAndResume.clicked.connect(self.onBtnLoadAndResume)
        self.fillFilter()
       # self.show()
    def onShowMessage(self, text):
        QtGui.QMessageBox.information(self, 'TMV3', text, QtGui.QMessageBox.Ok)

        pass
    def fillFilter(self):
        dbPlot = Tpl3Plot(self.workBenchDB,0)
        ret = dbPlot.findGroups()
        if ret != 0:
            self.ui.CBoxGroup.addItems(ret)
        ret = dbPlot.findPlotTitle()
        if ret != 0:
            self.ui.CBoxPlotTitle.addItems(ret)

        dbTest = TPL3Test(self.workBenchDB,0)
        ret = dbTest.findCompany()
        if ret != 0:
            self.ui.CBoxCompany.addItems(ret)
#        ret = dbTest.findProject()
#        if ret != 0:
#            self.ui.CBoxProject.addItems(ret)
#        pass

        self.viewTableModel2 = TableModel(["Title", "Comment", "Date"])
        try:
            _con = lite.connect(self.workBenchDB)
           # _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            _cur.execute("SELECT Title, Comment, Date FROM [Filter]")
            _rows = _cur.fetchall()
            for _row in _rows:
                self.viewTableModel2.addData(_row)
            _con.close()
            self.ui.tableView_2.setModel(self.viewTableModel2)
            _header = self.ui.tableView_2.horizontalHeader()
            _header.setResizeMode(QtGui.QHeaderView.ResizeToContents)

        except  Exception as _err:
            txt = "SQL: \n\r " + str(_err)
            self.signalShowMessage.emit(txt)

            return 0

    def onBtnSave(self):

        if self.ui.lineEdit.text() == "View-Title" or self.ui.lineEdit.text() == "":
            self.onShowMessage("Please define Title of View")
            return

        filterSet = Tpl3Filter(self.workBenchDB,0)
        filterSet.title = self.ui.lineEdit.text()
        if filterSet.readTitle(self.ui.lineEdit.text()):
            self.onShowMessage("'{0}' already exists".format(self.ui.lineEdit.text()))
            return

        if self.ui.CB_ZoneKMV.isChecked(): filterSet.type = 'ZoneKMV'
        if self.ui.CB_LevelKMV.isChecked(): filterSet.type = 'LevelKMV'
        if self.ui.CB_ZoneApp.isChecked(): filterSet.type = 'ZoneApp'
        if self.ui.CB_LevelApp.isChecked(): filterSet.type = 'LevelApp'
        if self.ui.CB_other.isChecked(): filterSet.type = 'other'
        if self.ui.CB_CompanyEnable.isChecked(): filterSet.company = self.ui.CBoxCompany.currentText()
        if self.ui.CB_GroupEnable.isChecked(): filterSet.group = self.ui.CBoxGroup.currentText()
        if self.ui.CB_PlotTitleEnable.isChecked(): filterSet.plot_title = self.ui.CBoxPlotTitle.currentText()
        if self.ui.CB_RoutineEnable.isChecked(): filterSet.routine = self.ui.CBoxRoutine.currentText()
        if self.ui.CB_ProjectEnable.isChecked(): filterSet.project = self.ui.CBoxProject.currentText()
        if self.ui.CB_TextEnable.isChecked(): filterSet.text = self.ui.EdText.text()
        if self.ui.CB_ZNoEnable.isChecked(): filterSet.zuNo = self.ui.EdZNo.text()
        if self.ui.CB_TestNoEnable.isChecked(): filterSet.testNo = self.ui.EdTestNo.text()
        if self.ui.CB_IdEnable.isChecked(): filterSet.testID = self.ui.EdID.text()
        if self.ui.CB_DateEditEnable.isChecked():
            filterSet.dateFrom = self.ui.dateEditFrom.text()
            filterSet.dateTo = self.ui.dateEditTo.text()
        if self.ui.RB_And.isChecked(): filterSet.andor = True
        if self.ui.RB_Or.isChecked(): filterSet.andor = True
        filterSet.sql = self.selectString
        filterSet.comment = self.ui.lineEdit_Comment.text()
        filterSet.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        _ret = filterSet.add()
        if _ret != 0:
            self.onShowMessage("View {0} saved".format(self.ui.lineEdit.text()))

        pass

    def onBtnApply2(self):
        _sel = self.ui.tableView_2.selectionModel().selectedRows()
        if len(_sel) > 0:
            _viewTitle = self.viewTableModel2.data(_sel[0], Qt.DisplayRole)
            _filter = Tpl3Filter(self.workBenchDB,0)
            _filter.readTitle(_viewTitle)

            self.selectString = _filter.sql
           # print (self.selectString)
            self.ui.EdSearch.setPlainText(self.selectString)
            self.showResult()

    def onBtnApply(self):

        self.selectString = self.ui.EdSearch.toPlainText()
        self.showResult()

    def showResult(self):
        header=[]
        s0 = self.selectString.split('\n')
        s1 = s0[0].split(',')
        for x in s1:
            s2 = x.split('.')  #'SELECT [main].[Plot].[PlotID]'
            s3 = s2[len(s2)-1] #'[PlotID]'
            s4 = s3.replace('[','')
            s5 = s4.replace(']','')
            s6 = s5.lstrip(' ')
            header.append(s6)
        self.viewTableModel = TableModel(header)

        try:
            _con = lite.connect(self.workBenchDB)
           # _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            _cur.execute(self.selectString)
            _rows = _cur.fetchall()
            _hits = str(len(_rows)) + ' Hits'
            self.ui.lb_Count.setText(_hits)
            for _row in _rows:
                self.sel.append(_row[0])
                self.viewTableModel.addData(_row)
            _con.close()
            self.ui.tableView.setModel(self.viewTableModel)
            _header = self.ui.tableView.horizontalHeader()
            _header.setResizeMode(QtGui.QHeaderView.ResizeToContents)

        except  Exception as _err:
            txt = "SQL: \n\r " + str(_err)
            self.signalShowMessage.emit(txt)

            return 0
        pass

    def onBtnEnableA(self):
        self.ui.CB_other.setChecked(False)
        self.onBtnEnable()

    def onBtnEnableB(self):
        self.ui.CB_ZoneKMV.setChecked(False)
        self.ui.CB_LevelKMV.setChecked(False)
        self.ui.CB_ZoneApp.setChecked(False)
        self.ui.CB_LevelApp.setChecked(False)
        self.onBtnEnable()

    def onBtnEnable(self):

#       e.g.
#       SELECT [Plot].[PlotID]
#       FROM [tests]
#       INNER JOIN [Plot] ON [tests].[TestID] = [Plot].[TestID]
#       WHERE [Plot].[PlotTitle] = 'KMV_D_302_A' AND [tests].[Project] = 'TestProject2'
        _con = 'OR'
        if self.ui.RB_And.isChecked():
            _con = 'AND'

        _filterString = "SELECT [Plot].[PlotID], [Plot].[PlotTitle]\r\n"
        _filterString += "FROM [Tests]\r\n"
        _filterString += "   INNER JOIN [Plot] ON [Tests].[TestID] = [Plot].[TestID]\r\n"
        _filterString += "   INNER JOIN [Projects] ON [Tests].[ProjectID] = [Projects].[ProjectID]\r\n"
        _filterString += "WHERE "
        _whereString = ""

        _cat = ''
        if self.ui.CB_LevelKMV.isChecked():
            _cat += "'LK',"
        if self.ui.CB_ZoneKMV.isChecked():
            _cat += "'ZK',"
        if self.ui.CB_ZoneApp.isChecked():
            _cat += "'ZZ',"
        if self.ui.CB_LevelApp.isChecked():
            _cat += "'LZ',"
        if self.ui.CB_other.isChecked():
            _whereString += "\r\n\t{0} [Tests].[Category] NOT IN ('LK', 'LZ', 'ZK', 'ZZ')".format(_con)
        else:
            if _cat != '':
                _cat = _cat.rstrip(',')
                _whereString += "\r\n\t{0} [Tests].[Category] IN ({1})".format(_con,_cat)

        if self.ui.CB_CompanyEnable.isChecked():
            _dt = "\r\n\t{0} [Tests].[Company] = '{1}'".format(_con,self.ui.CBoxCompany.currentText())
            _whereString += _dt

        if self.ui.CB_GroupEnable.isChecked():
            _dt = "\r\n\t{0} [Plot].[Group] = '{1}'".format(_con,self.ui.CBoxGroup.currentText())
            _whereString += _dt

        if self.ui.CB_PlotTitleEnable.isChecked():
            _dt = "\r\n\t{0} [Plot].[PlotTitle] = '{1}'".format(_con,self.ui.CBoxPlotTitle.currentText())
            _whereString += _dt

        if self.ui.CB_RoutineEnable.isChecked():
            _dt = "\r\n\t{0} [Plot].[Routines] = '{1}'".format(_con,self.ui.CBoxRoutine.currentText())
            _whereString += _dt

        if self.ui.CB_ProjectEnable.isChecked():
            _dt = "\r\n\t{0} [Projects].[Title] = '{1}'".format(_con,self.ui.CBoxProject.currentText())
            _whereString += _dt

        if self.ui.CB_DateEditEnable.isChecked():
            _dt = "\r\n\t{0} [Tests].[DateTime] BETWEEN '{1}' AND '{2}'"\
                 .format(_con,self.ui.dateEditFrom.date().toPyDate(),self.ui.dateEditTo.date().toPyDate())
            _whereString += _dt

        if self.ui.CB_ZNoEnable.isChecked():
            _dt = "\r\n\t{0} [Tests].[TempestZNo] = '{1}'".format(_con,self.ui.EdZNo.text())
            _whereString += _dt

        if self.ui.CB_TestNoEnable.isChecked():
            _dt = "\r\n\t{0} [Tests].[TestNo] = '{1}'".format(_con,self.ui.EdTestNo.text())
            _whereString += _dt

        if self.ui.CB_IdEnable.isChecked():
            _dt = "\r\n\t{0} [Tests].[TestID] = '{1}'".format(_con,self.ui.EdID.text())
            _whereString += _dt

        if self.ui.CB_TextEnable.isChecked():
            _s = '%{0}%'.format(self.ui.EdText.text())
            _dt = "\r\n\t{0} [Plot].[Annotations] like '{1}'".format(_con,_s)
            _whereString += _dt

        if _con == 'OR':
            _whereString = _whereString[5:]
        else:
            _whereString = _whereString[6:]

        _filterString += _whereString
        self.ui.EdSearch.setPlainText(_filterString)
        self.selectString = _filterString

        pass

    def onCellChanged(self,x,y):
        pass
    def selectAll(self):
        topLeft = self.viewTableModel.index(0, 0)
#       bottomRight = self.viewTableModel.index(0, 0)(m->rowCount(parent)-1,
 #        model->columnCount(parent)-1, parent);
    def onBtnCancel(self):
        #print('onBtnCancel')
        self.ret = False
        self.close()

        pass

    def onBtnOk(self):
        if self.ui.tableView.selectionModel is not None:
            _sel = self.ui.tableView.selectionModel().selectedRows()
        if len(_sel) > 0:
             self.sel = []
             for row in _sel:
                 self.sel.append(self.viewTableModel.data(row, Qt.DisplayRole))
        self.ret = True
        self.close()


    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

