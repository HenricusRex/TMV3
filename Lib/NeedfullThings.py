__author__ = 'HS'

from PyQt4.QtCore import *
from PyQt4 import QtGui,uic,QtCore
import configparser
import threading
import cProfile

class Signal(object):
    signalMeasConnected = pyqtSignal()
    def __init__(self):
        self.ERROR_MESSAGE = "ErrorMessage"
        self.SHOW_MESSAGE = "ShowMessage"
        self.MEAS_STARTED = "MeasStarted"
        self.MEAS_STOP = "MeasStop"
        self.MEAS_ERROR = "MeasError"
        self.MEAS_CONNECTED = "MeasConnected"
        self.MEAS_PAUSE = "MeasPause"
        self.MEAS_COMPLETE = "MeasComplete"
        self.MEAS_PLOT_COMPLETE = "MeasPlotComplete"
        self.MEAS_RESULT = "MeasResult"
        self.MEAS_GOON = "MeasGoOn"
        self.SHOW_MESSAGE = "ShowMessage"
        self.ENDE = "Ende"

        self.ITEM_ACTIVE = "ItemActive"
        self.ITEM_COMPLETE ="ItemComplete"

        self.CTR_LOAD_TESTPLAN = "CtrLoadTestplan"
        self.CTR_SHOW_PLOT = "CtrShowPlot"
        self.CTR_EXIT = "CtrExit"
        self.CTR_LOAD_TEST = "CtrLoadTest"
        self.CTR_SET_MASTER_ID = "CtrSetMasterID"
        self.JOB_TABLE = "JobTable"
        self.JOB_COMPLETE = "JobComplete"
        self.JOB_NEXT = "JobNext"
        self.JOB_START = "JobStart"
        self.PLOT_COMPLETE = "PlotComplete"
        self.PLOT_NEW = "PlotID"
        self.PLOT_UPDATE = "PlotUpdate"
        self.WB_CREATE_NEW_WB = "WB_CreateWorkbench"
        self.WB_COPY_WB = "WB_CopyWorkbench"
        self.WB_ADD_TEST = "WB_AddTest"
        self.WB_GET_TEST = "WB_GetTest"
        self.WB_CLONE_TEST = "WB_CloneTest"
        self.WB_GET_TEST_FIRST = "WB_GetTestFirst"
        self.WB_GET_TEST_PREV = "WB_GetTestPrev"
        self.WB_GET_TEST_NEXT = "WB_GetTestNext"
        self.WB_GET_TEST_LAST = "WB_GetTestLast"
        self.WB_GET_TESTINFO = "WB_GetTestInfo"
        self.WB_GET_TEST_IDS = "WB_GetTestIDs"
        self.WB_GET_NEW_POJECT = "WB_GetNewProject"
        self.WB_GET_PROJECT = "WB_GetProject"
        self.WB_GET_PROJECT_FIRST = "WB_GetProjectFirst"
        self.WB_GET_PROJECT_PREV = "WB_GetProjectPrev"
        self.WB_GET_PROJECT_NEXT = "WB_GetProjectNext"
        self.WB_GET_PROJECT_LAST = "WB_GetProjectLast"
        self.WB_GET_PROJECT_IDS = "WB_GetProjectIDs"
        self.WB_UPDATE_PROJECT = "WB_UpdateProject"
        self.WB_DEL_TEST = "WB_DelTest"
        self.WB_DEL_PLOT = "WB_DelPlot"
        self.WB_ADD_PLAN = "WB_AddPlan"
        self.WB_GET_PLAN = "WB_GetPlan"
        self.WB_GET_CURRENT_PLAN = "WB_GetCurrentPlan"
        self.WB_SET_CURRENT_PLAN = "WB_SetCurrentPlan"
        self.WB_MODIFY_PLAN = "WB_ModifyPlan"
        self.WB_DELETE_PLAN = "WB_DeletePlan"
        self.WB_OK = "WB_Ok"
        self.WB_ERROR = "WB_Error"
        self.WB_PLAN = "WB_Plan"
        self.WB_TEST = "WB_Test"    #
        self.WB_TESTINFO = "WB_TestInfo"
        self.WB_CURRENT_PLAN_ID = 1
        self.WB_UPDATE_TEST = "WB_UpdateTest"
        self.WB_GET_NEW_TEST = "WB_GetNewTest"
        self.WB_EXPORT_FILE = "WB_ExportFile"
        self.WB_GET_TICKET = "WB_GetTicket"
        self.WB_NEW_PLOT = "WB_NewPlot"
        self.WB_NEW_PLOT_ID = "WB_NewPlotID"
        self.WB_ADD_TRACE = "WB_AddTrace"
        self.WB_ADD_LINE = "WB_AddLine"
        self.WB_ADD_MARK = "WB_AddMark"
        self.WB_ADD_OBJECT = "WB_AddObject"
        self.WB_IMPORT_LINE = "WB_ImportLine"
        self.WB_IMPORT_TDS = "WB_ImportTds"
        self.WB_EXPORT_LIMIT = "WB_ExportLimit"
        self.WB_EXPORT_CORR = "WB_ExportCorr"
        self.WB_EXPORT_TDS = "WB_ExportTds"
        self.WB_DEL_ROUTE = "WB_DelRoute"
        self.WB_ADD_ROUTE = "WB_AddRoute"
        self.WB_GET_ROUTE = "WB_GetRoute"
        self.WB_GET_ROUTE_IDS = "WB_GetRouteIDs"
        self.WB_UPDATE_ROUTE = "WB_UpdateRoute"
        self.WB_GET_LINE = "WB_GetLine"
        self.WB_GET_LINE_IDS = "WB_GetLine_IDs"
        self.WB_GET_LINE_EXISTS = "WB_GetLineExists"
        self.WB_GET_RELAIS = "WB_GetRelais"
        self.WB_GET_RELAIS_IDS = "WB_GetRelaisIDs"
        self.WB_GET_MASTER_IDS = "WB_Get_MasterIDs"
        self.WB_GET_MASTER_PLOT = "WB_GetMasterPlot"
        self.WB_GET_PLOT_INFO_IDS = "WB_GetPlotInfoIDs"
        self.WB_GET_PLOT_INFO = "WB_GetPlot_Info"
        self.WB_GET_PLOT = "WB_GetPlot"
        self.WB_GET_PLOT_CORR_IDS = "WB_GetPlotCorrIDs"
        self.WB_SET_RESULT = "WB_SetResult"
        self.WB_SET_IMAGE = "WB_SetImage"
        self.WB_SET_GROUP = "WB_SetGroup"
        self.WB_GET_PROJECTS_TEST_IDS = "WB_GetProjectTestIDs"

        self.GRAPH_CONNECTED = "GRAPH_Connected"
        self.GRAPH_NEW_PLOT = "GRAPH_NewPlot"
        self.GRAPH_NEW_TRACE = "GRAPH_NewTrace"
        self.GRAPH_NEW_LINE = "GRAPH_NewLine"
        self.GRAPH_NEW_ANNOTATION = "GRAPH_NewAnnotation"
        self.GRAPH_NEW_CLASSIFICATION = "GRAPH_NewClassification"
        self.GRAPH_NEW_DESCRIPTION = "GRAPH_Description"
        self.GRAPH_NEW_NUMBER = "GRAPH_Number"
        self.GRAPH_SHOW_PLOT = "GRAPH_ShowPlot"
        self.GRAPH_PRINT = "GRAPH_Print"
        self.GRAPH_STOP = "GRAPH_Stop"
        self.GRAPH_STARTED = "GRAPH_Started"
        self.GRAPH_STOPPED = "GRAPH_Stopped"
        self.GRAPH_ERROR = "GRAPH_Error"
        self.GRAPH_RESULT = "GRAPH_Result"
        self.GRAPH_MAKE_THUMBNAIL = "GRAPH_Make_Thumbnail"
        self.GRAPH_THUMBNAIL_READY = "GRAPH_Make_Thumbnail_Ready"

        self.EDIT_PLANID ="EDIT_PlanID"
        self.EDIT_PLOTID ="EDIT_PlotID"
        self.EDIT_ROUTINEID ="EDIT_RoutineID"
        self.EDIT_SETTINGID ="EDIT_SettingID"
        self.EDIT_ADD_LIMIT = "EDIT_Add_Limit"
        self.EDIT_ADD_LINE = "EDIT_Add_Line"
        self.EDIT_ADD_DEVICE = "EDIT_Add_Device"
        self.EDIT_ADD_INSTRUCTION = "EDIT_Add_Instruction"
        self.EDIT_DEL_ITEM = "EDIT_DelItem"


class StateRegister():
    MEAS_STARTED = hex(0x01)
    MEAS_FAILED = hex(0x02)
    DATASET_FAILED = hex(0x04)
    MEAS_PAUSED = hex(0x08)

    def __init__(self):
        self.reg=0
    def isMeasStarted(self):
        return(self.MEAS_STARTED)

    def isMeasFailed(self):
        return(self.MEAS_FAILED)

    def setMeasStartet(self):
        self.MEAS_STARTED = True
        pass
    def clearMeasStartet(self):
        self.MEAS_STARTED = False
        pass
    def setMeasFailed(self):
        self.MEAS_FAILED = True
        pass
    def clearMeasFailed(self):
        self.MEAS_FAILED = False
        pass


class TableModel(QAbstractTableModel):
    def __init__(self, header, parent = None):
        super(TableModel, self).__init__(parent)
        self._data = []
        self._header = header
        pass

    def rowCount(self, parent = QModelIndex()):
        return len(self._data)

    def columnCount(self, parent = QModelIndex()):
        return len(self._header)

    def data(self, index, role):
        _row = index.row()
        _col = index.column()

        if not index.isValid():
            return None
        elif role == Qt.DisplayRole:
           # print(_row,_col)
            return self._data[_row][_col]


    def addData(self, data):
        self._data.append(data)
        self.emit(SIGNAL("layoutChanged()"))
    def setData(self, index, value):
        self._data[index.row()][index.column()] = value
        self.emit(SIGNAL('dataChanged(const QModelIndex &, '
        'const QModelIndex &)'), index, index)
        return True

    def headerData(self, col, orientation, role):
        if role == Qt.DisplayRole :
            if orientation == Qt.Horizontal :
                return self._header[col]
            elif orientation == Qt.Vertical :
                return None
        return None

    def removeRows(self, row, count, parent=QModelIndex()):
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        del self._data[row:row + count]
        self.endRemoveRows()
        return True


    def sort(self, Ncol, order):
        """
        Sort table by given column number.
        """
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        #self._data = sorted(self._data, key=Ncol))
        if order == Qt.DescendingOrder:
            self.arraydata.reverse()
        self.emit(SIGNAL("layoutChanged()"))

        return None



    def updateView(self):
        self.emit(SIGNAL('dataChanged()'))

class ImageDelegate(QtGui.QStyledItemDelegate):
    def __init__(self,parent):
        QtGui.QStyledItemDelegate.__init__(self,parent)

    def paint(self,painter,option,index):
        _currentQAbstractItemModel = index.model()
        _iconQModelIndex = _currentQAbstractItemModel.index(index.row(), 1, index.parent())
        _image = QtGui.QImage.fromData(_currentQAbstractItemModel.data(index,QtCore.Qt.DisplayRole))
        _iconQPixmap  = QtGui.QPixmap.fromImage(_image)
        if not _iconQPixmap.isNull():
            painter.drawPixmap (
            option.rect.x(),
            option.rect.y(),
            _iconQPixmap.scaled(200, 120, QtCore.Qt.KeepAspectRatio))

class Choose(QtGui.QDialog):

    def __init__(self, model, title):
        #global model
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("Choose.ui", self)
        self.centerOnScreen()
        self.signals = Signal()
        self._config = configparser.ConfigParser()
        self._config.read('TMV3.ini')
        self.ret = False
        self.sel = []
        self.selIdx = []

        self.ui.setWindowTitle(title)
        self.ui.tableView.setModel(model)
        self.ui.BtnOk.clicked.connect(self.onBtnOk)
        self.ui.BtnCancel.clicked.connect(self.onBtnCancel)
        self.ui.tableView.doubleClicked.connect(self.onBtnOk)

        self.ui.show()

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

    def onDoubleClick(self,index):
        self.onBtnOk()

    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))



