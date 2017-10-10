# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:42:08 2013

@author: HS
"""


from DB_Handler_TDS3 import *
from DB_Handler_TPL3 import *
from pydispatch import dispatcher
from NeedfullThings import *
from EngFormat import Format
from EditTraces import EditTraces
from EditCommands import EditCommands
from EditTools import *
from Line import *
from Routing import *
from EditSelectDataset import *
import shutil
import glob



class contextMenu(QtGui.QMenu):
    def __init__(self, parent=None):
        QtGui.QMenu.__init__(self, parent)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)




class ProxyModel(QtGui.QIdentityProxyModel):
    def __init__(self, parent=None):
        super(ProxyModel, self).__init__(parent)
        self._columnsReadOnly = set()
        self._columnsDisabled = set()

    def columnReadOnly(self, column):
        return column in self._columnsReadOnly

    def setColumnReadOnly(self, column, readonly=True):
        if readonly:
            if not column in self._columnsReadOnly:
                self._columnsReadOnly.add(column)
        else:
            self._columnsReadOnly.discard(column)

    def columnDisable(self, column):
        return column in self._columnsDisabled

    def setColumnDisable(self, column, disable=True):
        if disable:
            if not column in self._columnsDisabled:
                self._columnsDisabled.add(column)
        else:
            self._columnsDisabled.discard(column)

    def flags(self, index):
        flags = super(ProxyModel, self).flags(index)
        if self.columnReadOnly(index.column()):
            flags &= ~QtCore.Qt.ItemIsEditable
            flags &= ~QtCore.Qt.ItemIsSelectable
        if self.columnDisable(index.column()):
        #    flags &= ~QtCore.Qt.ItemIsEnabled
            flags &= ~QtCore.Qt.ItemIsEditable
            flags &= ~QtCore.Qt.ItemIsSelectable
        return flags



PLAN_TYPE, PLOT_TYPE, ROUTINE_TYPE, LIMIT_TYPE, SETTING_TYPE, TRACE_TYPE, ROUTE_TYPE = range(1001, 1008)
class MainForm(QtGui.QMainWindow):


    def __init__(self,edit_current=False,parent=None):
        QtGui.QMainWindow.__init__(self)
        self.ui = uic.loadUi("../Editor/EditorMainDB.ui", self)
      #  self.ui.setWindowState(QtCore.Qt.WindowMaximized)
        self.ui.BtnSave.clicked.connect(self.onBtnSave)
        self.ui.BtnExit.clicked.connect(self.onBtnExit)

        self.ui.BtnExpandAll.clicked.connect(self.onBtnExpandAll)
        self.ui.BtnCollapseAll.clicked.connect(self.onBtnCollapseAll)
        self.ui.BtnAddPlot.clicked.connect(self.onAddPlot)
        self.ui.BtnAddRoutine.clicked.connect(self.onAddRoutine)
        self.ui.BtnAddSetting.clicked.connect(self.onAddSetting)
        self.ui.treeWidget.itemSelectionChanged.connect(self.onSelectionChanged)
        self.ui.treeWidget.copied.connect(self.onCopied)
     #   self.ui.treeWidget.itemDoubleClicked.connect(self.onItemDClicked)

        self.ui.actionNew.triggered.connect(self.onMnuNew)
        self.ui.actionOpen_from_Workbench.triggered.connect(self.onMnuOpenFromWorkbench)
        self.ui.actionOpen_from_File.triggered.connect(self.onMnuOpenFromFile)
        self.ui.actionSave.triggered.connect(self.onMnuSave)
        self.ui.actionSave_as.triggered.connect(self.onMnuSaveAs)
        self.ui.actionCommit.triggered.connect(self.onMnuCommit)
        self.id = 1
        self.dataSetFileName = ''
        self.ds = None
        self.saveFunction = ''
        self.signals = Signal()
        self.filename = ''
        self.viewTableModel = None
        self.ui.tableView.customContextMenuRequested.connect(self.contextMenuEvent)
        self.config = configparser.ConfigParser()
        self.config.read('../Lib/TMV3.ini')
        self.workBenchDB = self.config['DataBases']['workbench']
        self.noContext = False
        self.changeFlag = False
        self.openFromWbFlag = False
        self.tdsFileName = ''
        if len(sys.argv) > 1:
            self.tdsFileName = 'ActiveTestPlan.TDS3'
            self.onLoadTDS('../WorkingDir/ActiveTestPlan.TDS3')
            self.openFromWbFlag = True

        # self.openTDS3()
        # self.onBtnExpandAll()
        # self.ui.BtnAddPlot.setEnabled(True)
        # self.ui.BtnAddRoutine.setEnabled(False)
        # self.ui.BtnAddSetting.setEnabled(False)
        # self.editPlan()

    def onMnuNew(self):

        if os.path.exists("../WorkingDir/EditTDS.tds3"):
            os.remove("../WorkingDir/EditTDS.tds3")
        shutil.copy("../Templates/TMV3.TDS3","../WorkingDir/EditTDS.tds3")
        _tds = Dataset("../WorkingDir/EditTDS.tds3")
        _tds.read()
        _d = datetime.now()
        _tds.date = datetime(_d.year, _d.month, _d.day, _d.hour, _d.minute, _d.second).isoformat(' ')
        _tds.db.date = _tds.date
        _tds.db.update()
        self.onLoadTDS("../WorkingDir/EditTDS.tds3")

        pass

    def onMnuOpenFromWorkbench(self):
        sel = SelectWBDS()
        if sel.exec_() :
            _file = Tpl3Files(self.workBenchDB, sel.ret)
            _file.destination = '../WorkingDir/EditTDS.TDS3'
            _file.export()
            self.onLoadTDS('../WorkingDir/EditTDS.TDS3')
            self.openFromWbFlag = True
            return True
        return 0

    def onMnuOpenFromFile(self):
        self.openTDS3()
        self.onBtnExpandAll()
        self.ui.BtnAddPlot.setEnabled(True)
        self.ui.BtnAddRoutine.setEnabled(False)
        self.ui.BtnAddSetting.setEnabled(False)
        self.editPlan()
        pass

    def onMnuSave(self,msgFlag = True):

        if self.changeFlag:
            self.saveToEditTDS()

        #copy EditTds to file with title given by testplan
        filename = "../WorkingDir/" + self.ds.db.title + ".tds3"
        if os.path.exists(filename):
            os.remove(filename)
        shutil.copy("../WorkingDir/EditTDS.tds3", filename)
        if msgFlag:
            _text = 'Testplan written to file {0}'.format(filename)
            self.messageInfo(_text)
        pass

    def onMnuSaveAs(self):
        if not self.changeFlag:
            _text = 'nothing to save'
            self.messageInfo(_text)
        #save EditTds to new filename
        dlg=QtGui.QFileDialog( self )
        dlg.setWindowTitle( 'save Testplan' )
        dlg.setViewMode( QtGui.QFileDialog.Detail )
        dlg.setNameFilters( [self.tr('DataSet (*.TDS3)')] )
        dlg.setDefaultSuffix( 'TDS3' )
        dlg.setDirectory('.')
        _fname = []
        if dlg.exec_() :
            _fname = dlg.selectedFiles()
            if _fname == '':
                return
        shutil.copy("../WorkingDir/EditTDS.tds3", _fname[0])
        _text = 'Testplan written to file {0}'.format(_fname[0])
        self.messageInfo(_text)
        pass

    def onBtnSave(self):
        # save EditTds as 'onMnuSave' and additional to workbench
        self.onMnuSave()
      #  self.onMnuCommit()

    def onMnuCommit(self):
        self.onMnuSave(False)
        _tpl3File = Tpl3Files(self.workBenchDB,0)
        _tpl3File.title = self.ds.db.title
        _tpl3File.type = "Testplan"
        _tpl3File.version = self.ds.db.version
        _d = datetime.now()
        _tpl3File.date = datetime(_d.year, _d.month, _d.day, _d.hour, _d.minute, _d.second).isoformat(' ')
        input_file = open('../WorkingDir/EditTDS.tds3', 'rb')
        bdata = input_file.read()
        _tpl3File.data = bdata
        id = _tpl3File.testplanExists()
        if id > 0:
            _tpl3File.file_id = id
            refcount = _tpl3File.findTestplanReference()
            if refcount > 0:
                _text = 'can not overwrite TDS\none or more Tests reverences the current version-no {0}'.format(str(_tpl3File.version))
                self.messageInfo(_text)
                return
            else:
                ret = _tpl3File.update()
                if ret == 0:
                    _text = 'can not update file {0}'.format(str(_tpl3File.title))
                    self.messageInfo(_text)
                    return
                else:
                    _text = 'file {0} written to workbench'.format(str(_tpl3File.title))
                    self.messageInfo(_text)
                    return


        else:
            ret = _tpl3File.add()
            if not ret:
                _text = 'can not add file {0}'.format(str(_tpl3File.title))
                self.messageInfo(_text)
            else:
                _text = 'file {0} written to workbench'.format(str(_tpl3File.title))
                self.messageInfo(_text)

        pass


    def openAction(self, row, column):
        if self._slideShowWin:
            self._slideShowWin.showImageByPath(self._twoDLst[row][column])
            self._animateUpOpen()

    def deleteSelected(self):
        # TODO
        pass

    def openTDS3(self):
        #open Testplan from File
        dlg=QtGui.QFileDialog( self )
        dlg.setWindowTitle( 'open or create Testplan' )
        dlg.setViewMode( QtGui.QFileDialog.Detail )
        dlg.setNameFilters( [self.tr('DataSet (*.TDS3)')] )
        dlg.setDefaultSuffix( 'TDS3' )
        dlg.setDirectory('.')
        _fname = []
        if dlg.exec_() :
            _fname = dlg.selectedFiles()
            if _fname == '':
                return
            #work with duplicate
            if QtCore.QFile.exists(_fname[0]):
                if os.path.exists("../WorkingDir/EditTDS.tds3"):
                    os.remove("../WorkingDir/EditTDS.tds3")
                shutil.copy(_fname[0],"../WorkingDir/EditTDS.tds3")
                self.onLoadTDS("../WorkingDir/EditTDS.tds3")
            else:
                print('new TDS', _fname)
        self.filename = _fname

    def onBtnDelItem(self):
        pass

    def onBtnExpandAll(self):
        self.ui.treeWidget.expandAll()
        pass

    def onBtnCollapseAll(self):
        self.ui.treeWidget.collapseAll()
        pass

    def onLoadTDS(self, fileName):
        self.dataSetFileName = fileName
        #-loads ActiveTestPlan to TreeView

        self.ds = Dataset(fileName)
        if self.ds.read():
            self.initTreeView()
        #self.ui.setCursor(QtCore.Qt.ArrowCursor)

    def initTreeView(self):
        _parentPlan = self.ui.treeWidget.invisibleRootItem()

        for i in reversed(range(_parentPlan.childCount())):
            _parentPlan.removeChild(_parentPlan.child(i))

        _text ='Plan ' + self.ds.db.title
        _parentPlot = self.ui.treeWidget.addItem(_parentPlan,PLAN_TYPE,self.ds.db.title,0)
        self.ds.db.treeviewItem = _parentPlot

        for _member_plot in self.ds.db.plot_list:
            _idx = self.ds.db.plot_list.index(_member_plot)
            assert isinstance(_member_plot,DatasetPlot)
            _parentRoutine = self.ui.treeWidget.addItem(_parentPlot,PLOT_TYPE,_member_plot.title,_idx)
            self.ui.treeWidget.collapseItem(_parentRoutine)

            for _member_routine in _member_plot.routine_list:
                _idx = _member_plot.routine_list.index(_member_routine)
                assert isinstance(_member_routine, DatasetRoutine)
                _parentSetting = self.ui.treeWidget.addItem(_parentRoutine,ROUTINE_TYPE,_member_routine.title,_idx)

                if not _member_routine.limits is None:
                    _limitLines = _member_routine.limits.split('\n')
                    if _limitLines[0] != '':
                        for _member_line in _limitLines:
                            self.ui.treeWidget.addItem(_parentSetting, LIMIT_TYPE, _member_line,0)
                if not _member_routine.lines is None:
                    _lines = _member_routine.lines.split('\n')
                    if _lines[0] != '':
                        for _member_line in _lines:
                            self.ui.treeWidget.addItem(_parentSetting, LIMIT_TYPE, _member_line[0])
                for _member_setting in _member_routine.setting_list:
                        _idx = _member_routine.setting_list.index(_member_setting)
                        _parentTrace = self.ui.treeWidget.addItem(_parentSetting,SETTING_TYPE,_member_setting.title,_idx)
                        if _member_setting.route != None:
                            self.ui.treeWidget.addItem(_parentTrace,ROUTE_TYPE,_member_setting.route,0)
                        for _member_trace in _member_setting.trace_list:
                            self.ui.treeWidget.addItem(_parentTrace,TRACE_TYPE,_member_trace.title,_member_trace.id_trace)

       # self.onBtnCollapseAll()

    def onCopied(self):
        #   print("copiert")
        pass

    def onBtnExit(self):
        self.close()

    def saveToEditTDS(self):
        try:
            saveMethode = getattr(self,self.saveFunction)
            ret = saveMethode()
        except Exception as _err:
            print (_err)
            pass

    def savePlan(self):
        _plan = self.ds.db
        _plan.update()
        _plan.treeviewItem.setText(0,_plan.title)
        self.changeFlag = False
 #       self.ui.treeWidget.expandAll()

    def savePlot(self):
        if not self.changeFlag:
            return True
        _plan = self.ds.db
        for i in _plan.plot_list:
            i.update()
        self.initTreeView()
        self.ui.treeWidget.expandAll()
        self.changeFlag = False

    def saveRoutine(self):
        if not self.changeFlag:
            return True
        for i in self.routineList:
            i.update()
            tdsFile = DatasetFile(self.dataSetFileName, 0)
            tdsFile.deleteFiles('Routine')
            if i.routinePath != "":
                input_file = open(i.routinePath, 'rt')
                bdata = input_file.read()

                tdsFile = DatasetFile(self.dataSetFileName,0)
                tdsFile.type = 'Routine'
                tdsFile.title = i.title
                tdsFile.data = bdata
                tdsFile.add()

            tdsFile.deleteFiles('Driver')
            if len(i.driverPathes) > 0:
                for x in i.driverPathes:
                    input_file = open(x, 'rt')
                    bdata = input_file.read()
                    s = (os.path.splitext(os.path.basename(x)))
                    tdsFile.type = 'Driver'
                    tdsFile.title = s[0]
                    tdsFile.data = bdata
                    tdsFile.add()



        self.initTreeView()
        self.ui.treeWidget.expandAll()
        self.changeFlag = False
        return True

    def saveSetting(self):
        if not self.changeFlag:
            return True
        try:
            for i in self.settingList:
                if not i.update():
                    raise  Exception('update Setting')
                if not i.delTraces():
                    raise Exception ('delete old Traces')
                for j in i.trace_list:
                    j.id_setting = i.id_setting
                    if not j.add():
                        raise Exception('renew Traces')
                if not i.delCommands():
                    raise Exception('delete old Commands')
                for j in i.command_list:
                    j.filename = self.dataSetFileName
                    j.id_setting = i.id_setting
                    if not j.add():
                        raise Exception('renew Commands')
        except Exception as _err:
            print (_err)
            return False
    #    self.messageSaveOk('Setting')
        self.initTreeView()
        self.ui.treeWidget.expandAll()
        self.changeFlag = False

        return True

    def messageInfo(self,text):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('TMV3 Editor')
        msgBox.setText(text)
        msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
        msgBox.exec_()


    def onSelectionChanged(self):
        self.noContext = False
        if self.changeFlag:
            self.saveToEditTDS()

        try:
            self.ui.treeWidget.customContextMenuRequested.disconnect()
        except Exception:
            pass

        _inx = self.ui.treeWidget.selectedIndexes()
        if len(_inx) > 0:
            _type = self.ui.treeWidget.itemFromIndex(_inx[0]).type
            _listIdx = self.ui.treeWidget.itemFromIndex(_inx[0]).id
            try:
                self.ui.tableView.doubleClicked.disconnect()
                self.viewTableModel.dataChanged.disconnect()
            except:
                pass
            self.ui.tableView.horizontalHeader().setSectionHidden(0,False)  # ListIndex
            if _type == PLAN_TYPE:
                self.ui.BtnAddPlot.setEnabled(True)
                self.ui.BtnAddRoutine.setEnabled(False)
                self.ui.BtnAddSetting.setEnabled(False)
                self.editPlan()
            elif _type == PLOT_TYPE:
                self.ui.BtnAddPlot.setEnabled(False)
                self.ui.BtnAddRoutine.setEnabled(True)
                self.ui.BtnAddSetting.setEnabled(False)
                self.editPlot(_listIdx)

            elif _type == ROUTINE_TYPE:
                self.ui.BtnAddPlot.setEnabled(False)
                self.ui.BtnAddRoutine.setEnabled(False)
                self.ui.BtnAddSetting.setEnabled(True)
                _listIdxP = self.ui.treeWidget.itemFromIndex(_inx[0]).parent().id
                self.editRoutine(_listIdxP,_listIdx)
            #    print(_listIdxP,_listIdx)

            elif _type == SETTING_TYPE:
                self.ui.BtnAddPlot.setEnabled(False)
                self.ui.BtnAddRoutine.setEnabled(False)
                self.ui.BtnAddSetting.setEnabled(False)
                _listIdxPP = self.ui.treeWidget.itemFromIndex(_inx[0]).parent().parent().id
                _listIdxP = self.ui.treeWidget.itemFromIndex(_inx[0]).parent().id
                self.editSetting(_listIdxPP,_listIdxP,_listIdx)
                pass
            elif _type == TRACE_TYPE:
                self.ui.BtnAddPlot.setEnabled(False)
                self.ui.BtnAddRoutine.setEnabled(False)
                self.ui.BtnAddSetting.setEnabled(False)
                msgBox =  QtGui.QMessageBox()
                msgBox.setWindowTitle('TMV3 Editor')
                msgBox.setText('please use Setting to edit Traces')
                msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
                msgBox.exec_()
            elif _type == LIMIT_TYPE:
                self.ui.BtnAddPlot.setEnabled(False)
                self.ui.BtnAddRoutine.setEnabled(False)
                self.ui.BtnAddSetting.setEnabled(False)
                title = self.ui.treeWidget.itemFromIndex(_inx[0]).title
                title_list = title.split(',')
                print (title_list)
                if title_list[0] != 'None':
                    limit = Tpl3Lines(self.workBenchDB, 0)
                    limit.title = title_list[0]
                    limit.version = title_list[1]
                    limit.version = limit.version.rstrip('\r')
                    limit.readLimitTitle()
                #    print(limit.line_id)
                    editLimits = Line(self, limit.line_id, True)
                    editLimits.show()
            elif _type == ROUTE_TYPE:
                self.ui.BtnAddPlot.setEnabled(False)
                self.ui.BtnAddRoutine.setEnabled(False)
                self.ui.BtnAddSetting.setEnabled(False)
                msgBox =  QtGui.QMessageBox()
                msgBox.setWindowTitle('TMV3 Editor')
                msgBox.setText('please use Controller to edit Routes')
                msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
                msgBox.exec_()
                pass
              #  self.ui.treeWidget.customContextMenuRequested.connect(self.contextMenuSetting)

              #  self.ui.BtnAddRoute.setEnabled(True)
              #  self.ui.treeWidget.setFlags(ROUTINE_TYPE)
            else:
                pass

    def onItemChanged(self):
        pass

    def onAddPlot(self):
        _inx = self.ui.treeWidget.selectedIndexes()
        if len(_inx) <= 0:
            return
        _parent = self.ui.treeWidget.itemFromIndex(_inx[0])
        #if any plot exists, than copy
        newPlot = DatasetPlot(self.ds.db.filename,0)
        newPlot.id_plan =  self.ds.db.planID
        item = self.ui.treeWidget.addItem(_parent, PLOT_TYPE, 'new Plot', self.id)
        newPlot.treeviewItem = item
        self.id += 1
        count =  len(self.ds.db.plot_list)
        if count > 0:
            newPlot.id_plan = self.ds.db.plot_list[count-1].id_plan
            newPlot.title = 'New Plot'
            newPlot.x1 = self.ds.db.plot_list[count-1].x1
            newPlot.x2 = self.ds.db.plot_list[count-1].x2
            newPlot.y1 = self.ds.db.plot_list[count-1].y1
            newPlot.y2 = self.ds.db.plot_list[count-1].y2
            newPlot.log = self.ds.db.plot_list[count-1].log
            newPlot.unit = self.ds.db.plot_list[count-1].unit
            newPlot.order = int(self.ds.db.plot_list[count-1].order)+1
            newPlot.annotation = self.ds.db.plot_list[count-1].annotation
            newPlot.comment = self.ds.db.plot_list[count-1].comment
        else:
            newPlot.id_plan = self.ds.db.planID
            newPlot.title = 'New Plot'
            newPlot.x1 = 1000
            newPlot.x2 = 10000
            newPlot.y1 = 100
            newPlot.y2 = 0
            newPlot.log = 1
            newPlot.unit = 'dBµV'
            newPlot.order = 1
            newPlot.annotation = "new Plot"
            newPlot.comment = "new Plot"

        newPlot.add()
        self.ui.treeWidget.clear()
        self.onLoadTDS(self.ds.db.filename)
        self.ui.treeWidget.expandAll()

        pass

    def onAddRoutine(self):
        _inx = self.ui.treeWidget.selectedIndexes()
        _parent = self.ui.treeWidget.itemFromIndex(_inx[0])
        item =self.ui.treeWidget.addItem(_parent,ROUTINE_TYPE, 'new Routine', self.id)
        self.id += 1
        _inx = self.ui.treeWidget.selectedIndexes()
        _listIdx = self.ui.treeWidget.itemFromIndex(_inx[0]).id
        parentPlot = self.ds.db.plot_list[_listIdx]
        newRt = DatasetRoutine(self.ds.db.filename,0)
        newRt.id_plot =  parentPlot.id_plot
        newRt.treeviewItem = item
        count =  len(parentPlot.routine_list)
        if count > 0:
            parentRoutine = parentPlot.routine_list[count-1]
            newRt.title = 'New Routine'
            newRt.device1 = parentRoutine.device1
            newRt.device2 = parentRoutine.device2
            newRt.device3 = parentRoutine.device3
            newRt.instruction = parentRoutine.instruction
            newRt.instruction_file = parentRoutine.instruction_file
            newRt.signal_class = parentRoutine.signal_class
            newRt.order = int (parentRoutine.order) + 1
            newRt.comment = parentRoutine.comment
            newRt.limits = parentRoutine.limits
            newRt.lines = parentRoutine.lines
        else:
            newRt.title = 'New Routine'
            newRt.device1 = ""
            newRt.device2 = ""
            newRt.device3 = ""
            newRt.instruction = ""
            newRt.instruction_file = ""
            newRt.signal_class = 2
            newRt.order = 1
            newRt.comment = ""
           # newRt.limits = None
           # newRt.lines = None

        newRt.add()
        self.ui.treeWidget.clear()
        self.onLoadTDS(self.ds.db.filename)
        self.ui.treeWidget.expandAll()

        pass

    def onAddSetting(self):
        _inx = self.ui.treeWidget.selectedIndexes()
        _parent = self.ui.treeWidget.itemFromIndex(_inx[0])
        item = self.ui.treeWidget.addItem(_parent,SETTING_TYPE,'new Setting',self.id)
        self.id += 1
        _listIdxR = self.ui.treeWidget.itemFromIndex(_inx[0]).id
        _listIdxP = self.ui.treeWidget.itemFromIndex(_inx[0]).parent().id
        parentRt = self.ds.db.plot_list[_listIdxP].routine_list[_listIdxR]
        newSe = DatasetSetting(self.ds.db.filename,0)
        newSe.id_routine =  parentRt.id_routine
        newSe.treeviewItem = item
        count =  len(parentRt.setting_list)
        if count > 0:
            parentSe = parentRt.setting_list[count-1]
            newSe.title = 'New Setting'
            newSe.order = parentSe.order+1
            newSe.route = parentSe.route
            newSe.instruction = parentSe.instruction
            newSe.autorange = parentSe.autorange
            newSe.start_freq = parentSe.start_freq
            newSe.stop_freq = parentSe.stop_freq
            newSe.step = parentSe.step
            newSe.step_width = parentSe.step_width
            newSe.step_time = parentSe.step_time
            newSe.id_setting = newSe.add()

            for i in parentSe.trace_list:
                t = DatasetTrace(self.ds.db.filename,0)
                t.id_setting = newSe.id_setting
                t.start_freq = i.start_freq
                t.stop_freq = i.stop_freq
                t.add()

            for i in parentSe.command_list:
                c = DatasetCommand(self.ds.db.filename,0)
                c.id_setting = newSe.id_setting
                c.order = i.order
                c.command = i.command
                c.parameter = i.parameter
                c.add()

        else:
            newSe.title = 'New Setting'
            newSe.order = '1'
            newSe.route = 'no Route'
            newSe.instruction = ''
            newSe.autorange = 0
            newSe.start_freq = 10000
            newSe.stop_freq = 100000
            newSe.step = 0
            newSe.step_with = 0
            newSe.step_time = 1
            newSe.add()

        self.ui.treeWidget.clear()
        self.onLoadTDS(self.ds.db.filename)
        self.ui.treeWidget.expandAll()

        pass

    def onDel(self):
        _inx = self.ui.treeWidget.selectedIndexes()
        if len(_inx) > 0:
            _item = self.ui.treeWidget.itemFromIndex(_inx[0])
            _c =  _item.childCount()
            if _c > 0:
                msgBox =  QtGui.QMessageBox()
                msgBox.setText('the selected item is head of a branch\nIf you delete this item, all subitems will be deleted too!')
                msgBox.setInformativeText('proceed anyway ?')
                msgBox.setStandardButtons(QtGui.QMessageBox.No|QtGui.QMessageBox.Yes)
                msgBox.setDefaultButton(QtGui.QMessageBox.No)
                _ret = msgBox.exec_()
                if _ret == QtGui.QMessageBox.Yes:
                     self.ui.treeWidget.delItem(_item)
            else:
                self.ui.treeWidget.delItem(_item)
        pass

    def disableColumns(self,disable):
        colCount = self.viewTableModel.columnCount()
        for i in range(colCount):
            if disable:
                self.ui.tableView.model().setColumnDisable(i,True)
            else:
                self.ui.tableView.model().setColumnDisable(i,False)

    def editPlan(self, id=0):
        self.viewTableModel= None
        self.viewTableModel = TableModel(['Title','Version','Zoning','KMV','Nato','Company','Operator','Date','Comment'])
        self.viewTableModel.beginResetModel()
        self.viewTableModel.removeRows(0, self.viewTableModel.rowCount())
        _plan = self.ds.db
        self.viewTableModel.addData([_plan.title,
                                     _plan.version,
                                     _plan.kmv,
                                     _plan.zoning,
                                     _plan.nato,
                                     _plan.company,
                                     _plan.operator,
                                     _plan.date,
                                     _plan.comment])

        self.ui.tableView.scrollToBottom()

        self.viewTableModel.endResetModel()
        self.proxy = ProxyModel(self)
        self.proxy.setSourceModel(self.viewTableModel)
        self.ui.tableView.setModel(self.proxy)
        self.ui.tableView.resizeColumnsToContents()
        self.ui.tableView.resizeRowsToContents()

        self.ui.tableView.model().setColumnReadOnly(2,True) #Zoning CBox
        self.ui.tableView.model().setColumnReadOnly(3,True) #KMV CBox
        self.ui.tableView.model().setColumnReadOnly(4,True) #Nato CBox
        self.ui.tableView.model().setColumnReadOnly(7,True) #Nato Calender
        self.ui.tableView.model().setColumnReadOnly(8,True) #Comment=PlainEditor
        self.ui.tableView.doubleClicked.connect(self.onDoubleClickTableViewPlan)
        self.viewTableModel.dataChanged.connect(self.onDataChangedPlan)

        self.saveFunction = 'savePlan'
        pass

    def onDataChangedPlan(self,mi):
        row = mi.row()
        col = mi.column()
        colName = self.viewTableModel.headerData(col, Qt.Horizontal,Qt.DisplayRole)
        idx = self.ui.tableView.model().index(row, col)
        _plan = self.ds.db

        if colName == 'Title':
            ret = self.viewTableModel.data(idx,Qt.DisplayRole)
            _plan.title = ret
            self.changeFlag = True
        if colName == 'Version':
            ret = self.viewTableModel.data(idx,Qt.DisplayRole)
            _plan.version = ret
            self.changeFlag = True
        if colName == 'Company':
            ret = self.viewTableModel.data(idx,Qt.DisplayRole)
            _plan.company = ret
            self.changeFlag = True
        if colName == 'Operator':
            ret = self.viewTableModel.data(idx,Qt.DisplayRole)
            _plan.operator = ret
            self.changeFlag = True

    def onDoubleClickTableViewPlan(self,mi):
        self.ui.tableView.blockSignals(True)
        row = mi.row()
        col = mi.column()
        _plan = self.ds.db
        colName = self.viewTableModel.headerData(col, Qt.Horizontal,Qt.DisplayRole)
        cursor = QtGui.QCursor()
        pos = self.ui.treeWidget.mapFromGlobal(cursor.pos())
        idx = self.ui.tableView.model().index(row, col)
        self.disableColumns(True)

        if colName == 'Zoning':
            ret = EditYesNo.getYesNo(pos,self)
            if ret != None:
                self.viewTableModel.setData(idx,ret)
                _plan.zoning = ret
                self.changeFlag = True

        elif colName == 'KMV':
            ret = EditYesNo.getYesNo(pos,self)
            if ret != None:
                self.viewTableModel.setData(idx,ret)
                _plan.kmv = ret
                self.changeFlag = True

        elif colName == 'Nato':
            ret = EditYesNo.getYesNo(pos,self)
            if ret != None:
                self.viewTableModel.setData(idx,ret)
                _plan.nato = ret
                self.changeFlag = True

        elif colName == 'Date':
            ret = EditDate.getDate(pos,self.viewTableModel.data(idx,Qt.DisplayRole),self)
            if ret != None:
                self.viewTableModel.setData(idx,ret)
                _plan.date = ret
                self.changeFlag = True

        elif colName == 'Comment':
            ret = EditPlain.getText(pos,self.viewTableModel.data(idx,Qt.DisplayRole),self)
            if ret != None:
                self.viewTableModel.setData(idx,ret)
                _plan.comment = ret
                self.changeFlag = True

        self.disableColumns(False)
        self.ui.tableView.blockSignals(False)

    def editPlot(self, idx):
        self.viewTableModel= None
        _bool = ['No','Yes']

        self.viewTableModel = TableModel(['Title','StartFreq','StopFreq','RefLevel','dB/Dev','x-Log','Unit','Order','Text','Comment'])

        self.viewTableModel.beginResetModel()
        self.viewTableModel.removeRows(0, self.viewTableModel.rowCount())
        for _plot in self.ds.db.plot_list:
            self.viewTableModel.addData([_plot.title,
                                        Format.FloatToString(self, _plot.x1,3),
                                        Format.FloatToString(self, _plot.x2, 3),
                                        _plot.y2,
                                        (_plot.y2 -_plot.y1) / 10,
                                        _bool[_plot.log],
                                        _plot.unit,
                                        _plot.order,
                                        _plot.annotation,
                                        _plot.comment])

        self.ui.tableView.scrollToBottom()
        self.viewTableModel.endResetModel()
        self.proxy = ProxyModel(self)
        self.proxy.setSourceModel(self.viewTableModel)
        self.ui.tableView.setModel(self.proxy)
        self.ui.tableView.resizeColumnsToContents()
        self.ui.tableView.resizeRowsToContents()

        self.ui.tableView.model().setColumnReadOnly(4,True) #dB/Dev
        self.ui.tableView.model().setColumnReadOnly(5,True) #x-log
        self.ui.tableView.model().setColumnReadOnly(6,True) #Unit
        self.ui.tableView.model().setColumnReadOnly(8,True) #Text
        self.ui.tableView.model().setColumnReadOnly(9,True) #Comment=PlainEditor
        self.ui.tableView.doubleClicked.connect(self.onDoubleClickTableViewPlot)

        #index = self.ui.tableView.model().index(idx,0)
        self.ui.tableView.selectRow(idx)
        self.saveFunction = 'savePlot'
        self.viewTableModel.dataChanged.connect(self.onDataChangedPlot)

    def onDataChangedPlot(self,mi):
        row = mi.row()
        col = mi.column()
        colName = self.viewTableModel.headerData(col, Qt.Horizontal,Qt.DisplayRole)
        idx = self.ui.tableView.model().index(row, col)
        _plot = self.ds.db.plot_list

        if colName == 'Title':
            ret = self.viewTableModel.data(idx,Qt.DisplayRole)
            _plot[row].title = ret
            self.changeFlag = True

        if colName == 'StartFreq':
            ret = self.viewTableModel.data(idx,Qt.DisplayRole)
            fValue = Format.StringToFloat(self, ret)
            sValue = Format.FloatToString(self, fValue, 3)
            self.viewTableModel.setData(idx, sValue, Qt.DisplayRole,False) #no dataChanged Signal
            _plot[row].x1 = fValue
            self.changeFlag = True

        if colName == 'StopFreq':
            ret = self.viewTableModel.data(idx,Qt.DisplayRole)
            fValue = Format.StringToFloat(self, ret)
            sValue = Format.FloatToString(self, fValue, 3)
            self.viewTableModel.setData(idx, sValue, Qt.DisplayRole,False)
            _plot[row].x2 = fValue
            self.changeFlag = True

        if colName == 'RefLevel':
            ret = self.viewTableModel.data(idx,Qt.DisplayRole)
            self.viewTableModel.setData(idx, ret, Qt.DisplayRole,False)
            _plot[row].y2 = ret
            idxdev = self.ui.tableView.model().index(row, col+1)
            _dbDev = self.viewTableModel.data(idxdev,Qt.DisplayRole)
            _y1 = ret - _dbDev * 10
            _plot[row].y1 = _y1
            self.changeFlag = True

        if colName == 'Order':
            ret = self.viewTableModel.data(idx,Qt.DisplayRole)
            _plot[row].order = ret
            self.changeFlag = True

    def onDoubleClickTableViewPlot(self, mi):
        self.ui.tableView.blockSignals(True)
        row = mi.row()
        col = mi.column()
        colName = self.viewTableModel.headerData(col, Qt.Horizontal, Qt.DisplayRole)
        cursor = QtGui.QCursor()
        pos = self.ui.treeWidget.mapFromGlobal(cursor.pos())
        idx = self.ui.tableView.model().index(row, col)
        _plot = self.ds.db.plot_list
        self.disableColumns(True)

        if colName == 'dB/Dev':
            ret = EditSelection.getSelection(pos,['5','10','15'],self)
            if ret != None:
                self.viewTableModel.setData(idx, float(ret))
                _y2 = _plot[row].y2
                _dBdev = float(ret)
                _y1 = _y2 - 10*_dBdev
                _plot[row].y1 = _y1
                self.changeFlag = True

        if colName == 'x-Log':
            ret = EditYesNo.getYesNo(pos, self)
            self.viewTableModel.setData(idx, ret)
            if ret == 'Yes':
                _plot[row].log = 1
            else:
                _plot[row].log = 0
            self.changeFlag = True

        if colName == 'Unit':
            ret = EditSelection.getSelection(pos,['dBµV','dBm'],self)
            if ret != None:
                self.viewTableModel.setData(idx, ret)
                _plot[row].unit = ret
                self.changeFlag = True

        if colName == 'Text':
            ret = EditPlain.getText(pos, self.viewTableModel.data(idx, Qt.DisplayRole), self)
            if ret != None:
                self.viewTableModel.setData(idx, ret)
                _plot[row].annotation = ret
                self.changeFlag = True

        if colName == 'Comment':
            ret = EditPlain.getText(pos, self.viewTableModel.data(idx, Qt.DisplayRole), self)
            if ret != None:
                self.viewTableModel.setData(idx, ret)
                _plot[row].comment = ret
                self.changeFlag = True

        self.disableColumns(False)
        self.ui.tableView.blockSignals(False)

    def editRoutine(self,idxP,idx):
        self.viewTableModel = None
        _bool = ['No', 'Yes']

        self.viewTableModel = TableModel(
            ['Routine', 'Device-Driver', 'Instruction', 'Instruction-File', 'Signal-Class', 'Order','Limits', 'Lines','Comment'])

        self.viewTableModel.beginResetModel()
        self.viewTableModel.removeRows(0, self.viewTableModel.rowCount())
        self.routineList = self.ds.db.plot_list[idxP].routine_list
        for _rt in self.routineList:
            self.viewTableModel.addData([_rt.title,
                                         _rt.device1.replace(',',''),
                                         _rt.instruction,
                                         _rt.instruction_file,
                                         _rt.signal_class,
                                         _rt.order,
                                         _rt.limits,
                                         self.setLineField(_rt.lines),
                                         _rt.comment])

        self.ui.tableView.scrollToBottom()
        self.viewTableModel.endResetModel()
        self.proxy = ProxyModel(self)
        self.proxy.setSourceModel(self.viewTableModel)
        self.ui.tableView.setModel(self.proxy)
        self.ui.tableView.resizeColumnsToContents()
        self.ui.tableView.resizeRowsToContents()
        self.ui.tableView.model().setColumnReadOnly(0,True) #Routine
        self.ui.tableView.model().setColumnReadOnly(1,True) #Devices
        self.ui.tableView.model().setColumnReadOnly(2,True) #Instruction
        self.ui.tableView.model().setColumnReadOnly(3,True) #Instruction-File
        self.ui.tableView.model().setColumnReadOnly(4,True) #Signal-Class
        self.ui.tableView.model().setColumnReadOnly(6,True) #Limits
        self.ui.tableView.model().setColumnReadOnly(7,True) #Lines
        self.ui.tableView.model().setColumnReadOnly(8,True) #Comment

        self.ui.tableView.doubleClicked.connect(self.onDoubleClickTableViewRoutine)
        self.ui.tableView.selectRow(idx)
        self.saveFunction = 'saveRoutine'
        self.viewTableModel.dataChanged.connect(self.onDataChangedRoutine)
        pass

    def onDataChangedRoutine(self,mi):
        row = mi.row()
        col = mi.column()
        colName = self.viewTableModel.headerData(col, Qt.Horizontal,Qt.DisplayRole)
        idx = self.ui.tableView.model().index(row, col)

        if colName == 'Order':
            ret = self.viewTableModel.data(idx,Qt.DisplayRole)
            self.routineList[row].order = ret

    def onDoubleClickTableViewRoutine(self, mi):
        self.ui.tableView.blockSignals(True)
        row = mi.row()
        col = mi.column()
        colName = self.viewTableModel.headerData(col, Qt.Horizontal, Qt.DisplayRole)
        cursor = QtGui.QCursor()
        pos = self.ui.treeWidget.mapFromGlobal(cursor.pos())
        idx = self.ui.tableView.model().index(row, col)
        routine = self.routineList[row]
        assert isinstance(routine,DatasetRoutine)
        self.disableColumns(True)

        if colName == 'Routine':
            dlg = QtGui.QFileDialog(self)
            dlg.setWindowTitle('select Testplan Routine')
            dlg.setViewMode(QtGui.QFileDialog.Detail)
            dlg.setNameFilters([self.tr('Python-File (*.PY)')])
            dlg.setDefaultSuffix('PY')
            dlg.setDirectory('../Routines')
            dlg.setFileMode(QtGui.QFileDialog.ExistingFile)
            if dlg.exec_():
                _fname = dlg.selectedFiles()
                s = (os.path.splitext(os.path.basename(_fname[0])))
                self.viewTableModel.setData(idx, s[0])
                self.routineList[row].title = s[0]
                self.routineList[row].routinePath = _fname[0]
                self.changeFlag = True


        if colName == 'Device-Driver':
            dlg = QtGui.QFileDialog(self)
            dlg.setWindowTitle('select Device Driver')
            dlg.setViewMode(QtGui.QFileDialog.Detail)
            dlg.setNameFilters([self.tr('Python-File (*.PY)')])
            dlg.setDefaultSuffix('PY')
            dlg.setDirectory('../DeviceDriver')
            dlg.setFileMode(QtGui.QFileDialog.ExistingFiles)
            if dlg.exec_():
                _fname = dlg.selectedFiles()
                dList = ""
                for x in _fname:
                    s = (os.path.splitext(os.path.basename(x)))
                    dList += s[0] + "\n"
                dList = dList.rstrip("\n")

                self.viewTableModel.setData(idx, dList)
                self.routineList[row].device1 = dList
                self.routineList[row].driverPathes = _fname
                print (self.routineList[row].driverPathes)

                self.changeFlag = True

        if colName == 'Instruction':
            ret = EditPlain.getText(pos, self.viewTableModel.data(idx, Qt.DisplayRole), self)
            if ret != None:
                self.viewTableModel.setData(idx, ret)
                routine.instruction = ret
                self.changeFlag = True
        if colName == 'Instruction-File':
            dlg = QtGui.QFileDialog(self)
            dlg.setWindowTitle('select Instruction File')
            dlg.setViewMode(QtGui.QFileDialog.Detail)
            dlg.setNameFilters([self.tr('PDF-File (*.PDF)')])
            dlg.setDefaultSuffix('PDF')
            dlg.setDirectory('.')
            if dlg.exec_():
                _fname = dlg.selectedFiles()
                self.viewTableModel.setData(idx, _fname[0])
                routine.instruction_file = _fname[0]
                self.changeFlag = True
        if colName == 'Signal-Class':
            ret = EditSelection.getSelection(pos,['1','2'],self)
            if ret != None:
                self.viewTableModel.setData(idx, ret)
                routine.signal_class = ret
                self.changeFlag = True
        if colName == 'Limits':
            limitDB = Tpl3Lines(self.workBenchDB,0)
            limitList = limitDB.readLimitTitles(True)
            ret = EditMultiSelection.getMultiSelection(pos, self.linesToStringTable(limitList[1]), self)
            if ret != None:
                s = ''
                for i in ret:
                    j = i.replace('\tVers: ','')
                    s = s + j + '\n'
                s = s.rstrip('\n')
                self.viewTableModel.setData(idx, s)
                routine.limits = s
                self.changeFlag = True
        if colName == 'Lines':
            linesDB = Tpl3Lines(self.workBenchDB,0)
            linesList = linesDB.readLineTitles(True)
            ret = EditMultiSelection.getMultiSelection(pos, self.linesToStringTable(linesList[1]), self)
            if ret != None:
                s = ''
                for i in ret:
                    j = i.replace('\tVers:','')
                    s = s + j + '\n'
                s = s.rstrip('\n')
                self.viewTableModel.setData(idx, s)
                self.ui.tableView.resizeRowsToContents()
                routine.lines = s
                self.changeFlag = True
        if colName == 'Comment':
            ret = EditPlain.getText(pos, self.viewTableModel.data(idx, Qt.DisplayRole), self)
            if ret != None:
                self.viewTableModel.setData(idx, ret)
                routine.comment = ret
                self.changeFlag = True
        self.ui.tableView.resizeRowsToContents()
        self.ui.tableView.resizeColumnsToContents()
        self.disableColumns(False)
        self.ui.tableView.blockSignals(False)

    def editSetting(self,idxPP,idxP,idx):

        self.viewTableModel = None
        _bool = ['No', 'Yes']

        self.viewTableModel = TableModel(
            ['ID','Order', 'Route', 'Instruction', 'Autorange', 'Traces','Commands','CommandObjects'])
        self.viewTableModel.beginResetModel()
        self.viewTableModel.removeRows(0, self.viewTableModel.rowCount())
        self.settingList = self.ds.db.plot_list[idxPP].routine_list[idxP].setting_list
        dd = self.ds.db.plot_list[idxPP].routine_list[idxP].device1.replace('\r',"")
        self.drivers = dd.split('\n')
        print (self.drivers)
        n = 0
        for _se in self.settingList:
            traces =  _se.trace_list
            traces =  _se.trace_list
            sTraceList = ''
            for x in traces:
                f1 = Format.FloatToString(self,x.start_freq,3)
                f2 = Format.FloatToString(self,x.stop_freq,3)
                s = f1 + "-" +f2 + '\n'
                sTraceList += s
            sTraceList = sTraceList.rstrip('\n')

            sCommand = ''
            oCommandList = []
            for x in _se.command_list:
                sCommand += x.tableEntry + '\n'
                oCommandList.append(x)

            sCommand = sCommand.rstrip('\n')

            self.viewTableModel.addData([n,
                                         _se.order,
                                         _se.route,
                                         _se.instruction,
                                         _bool[_se.autorange],
                                         sTraceList,
                                         sCommand,
                                         oCommandList])
            n += 1

        self.ui.tableView.scrollToBottom()
        self.viewTableModel.endResetModel()
        self.proxy = ProxyModel(self)
        self.proxy.setSourceModel(self.viewTableModel)
        self.ui.tableView.setModel(self.proxy)
        self.ui.tableView.resizeColumnsToContents()
        self.ui.tableView.resizeRowsToContents()
        self.ui.tableView.horizontalHeader().hideSection(0) #ListIndex
        self.ui.tableView.model().setColumnReadOnly(2, True)  # Route
        self.ui.tableView.model().setColumnReadOnly(3, True)  # Instruction
        self.ui.tableView.model().setColumnReadOnly(4, True)  # Autorange
        self.ui.tableView.model().setColumnReadOnly(5,True) #TraceList
        self.ui.tableView.model().setColumnReadOnly(6,True) #CommandList
        self.ui.tableView.horizontalHeader().hideSection(7) #CommandObjects

        self.ui.tableView.doubleClicked.connect(self.onDoubleClickTableViewSetting)

        self.ui.tableView.selectRow(idx)
        self.saveFunction = 'saveSetting'
        self.viewTableModel.dataChanged.connect(self.onDataChangedSetting)

        pass



    def onDataChangedSetting(self,mi):
        row = mi.row()
        col = mi.column()
        colName = self.viewTableModel.headerData(col, Qt.Horizontal,Qt.DisplayRole)
        idx = self.ui.tableView.model().index(row, col)

        if colName == 'Order':
            ret = self.viewTableModel.data(idx,Qt.DisplayRole)
            self.settingList[row].order = ret


    def onDoubleClickTableViewSetting(self,mi):
        self.ui.tableView.blockSignals(True)
        row = mi.row()
        col = mi.column()
        colName = self.viewTableModel.headerData(col, Qt.Horizontal, Qt.DisplayRole)
        cursor = QtGui.QCursor()
        pos = self.ui.treeWidget.mapFromGlobal(cursor.pos())
        idx = self.ui.tableView.model().index(row, col)

        if colName == 'Traces':
            sTraces = self.viewTableModel.data(idx,Qt.DisplayRole)
            sTraceList = None
            if sTraces != "":
                sTraceList = sTraces.split('\n')
            ret = EditTraces.editTraces (sTraceList,self)
            if ret is None:
                self.viewTableModel.setData(idx, sTraces)
            else:
                self.viewTableModel.setData(idx, ret)
                self.settingList[row].trace_list=[]
                sTraceList = ret.split('\n')
                fStartFreq = 100e9
                fStopFreq = 0
                for i in sTraceList:
                    sTrace = i.split('-')
                    trace = DatasetTrace(self.dataSetFileName,0)
                    trace.id_setting = self.settingList[row].id_setting
                    trace.start_freq = Format.StringToFloat(self,sTrace[0])
                    trace.stop_freq = Format.StringToFloat(self,sTrace[1])
                    if fStartFreq > trace.start_freq:
                        fStartFreq = trace.start_freq
                    if fStopFreq < trace.stop_freq:
                        fStopFreq = trace.stop_freq
                    self.settingList[row].trace_list.append(trace)
                settingTitle = Format.FloatToString(self,fStartFreq,None)+'-'+Format.FloatToString(self,fStopFreq,None)
                self.settingList[row].title = settingTitle
                self.settingList[row].startfreq = fStartFreq
                self.settingList[row].stopfreq = fStopFreq
                self.changeFlag = True
        if colName == 'Instruction':
            ret = EditPlain.getText(pos, self.viewTableModel.data(idx, Qt.DisplayRole), self)
            self.viewTableModel.setData(idx, ret)
            self.settingList[row].instruction = ret
            self.changeFlag = True

        if colName == 'Commands':
            if self.drivers[0] == '':
                self.messageInfo("you have to choose device-drivers first")
            else:

                _idx = self.viewTableModel.data(self.ui.tableView.model().index(row, 0),Qt.DisplayRole)
                oCommandList = self.viewTableModel.data(self.ui.tableView.model().index(row, 7),Qt.DisplayRole)
                sCommand = self.viewTableModel.data(self.ui.tableView.model().index(row, 6),Qt.DisplayRole)
               # ret = EditCommands.editCommands(self.settingList[_idx].command_list,self.drivers[0],self)
               # ret = self.viewTableModel.data(EditCommands.editCommands(self.settingList[_idx].command_list,self.drivers[0],self))
                ret = EditCommands.editCommands(oCommandList,self.drivers[0])
           #     print ('ret',ret)
                if ret == None:
                    self.viewTableModel.setData(idx,sCommand)
                else:
                    self.viewTableModel.setData(idx,ret[0])
                    self.settingList[_idx].command_list = ret[1]
                    # oCommandList = self.viewTableModel.data(self.ui.tableView.model().index(row, 7), Qt.DisplayRole)
                    # self.settingList[_idx].command_list = []
                    # _order = 1
                    for i in oCommandList:
                        i.filename = self.dataSetFileName
                    self.changeFlag = True
                    self.ui.tableView.resizeRowsToContents()
                    self.ui.tableView.resizeColumnsToContents()


        if colName == 'Autorange':
            ret = EditYesNo.getYesNo(pos, self)
            print (ret)
            self.viewTableModel.setData(idx, ret)
            if ret == 'Yes':
                self.settingList[row].autorange = 1
            else:
                self.settingList[row].autorange = 0
            self.changeFlag = True
        if colName == 'Route':
            routeDB = Tpl3Routes(self.workBenchDB,0)
            routeList = routeDB.readAliasTitle()
            ret = EditSelection.getSelection(pos, routeList, self)
            self.viewTableModel.setData(idx, ret)
            self.settingList[row].route = ret
            self.changeFlag = True
        self.ui.tableView.resizeRowsToContents()
        self.ui.tableView.resizeColumnsToContents()
        self.ui.tableView.blockSignals(False)

    def linesToStringTable(self,limits):
        s = ""
        sList = []
        for i in limits:
            s = i[0]+ ',\tVers: '
            s = s + i[1]
            sList.append(s)

        sList.sort()
        return sList

    def setLineField(self,lines):

        try:
            if type(lines) != list:
                return
            if len(lines) == 0:
                return
            _lines = eval(lines)
            _ret = ""
            for x in _lines:
                if not x is None:
                    _ret = _ret + x[0] + '; version  ' + x[1] + '\n'
            return _ret.rstrip('\n')
        except Exception as err:
            print ('set Line Field:',err)
            pass

    def getRoutineList(self):
        dList = glob.glob("../Routines/*.py")
        fList = []
        for i in dList:
            s = (os.path.splitext(os.path.basename(i)))
            fList.append(s[0])
        return fList

    def getDeviceDriverList(self):
        pass


def main(argv):
    app = QtGui.QApplication(sys.argv)

    sshFile = "../Templates/darkorange.css"
    with open (sshFile,"r") as fh:
        app.setStyleSheet(fh.read())
    currentTestPlan = False
    if len(sys.argv) > 1:
        currentTestPlan = True
    form = MainForm()
    form.show()
    app.exec_()




if __name__ == '__main__':
    import sys
    main(sys.argv[1])



