from DB_Handler_TDS3 import *
from DB_Handler_TPL3 import *
from pydispatch import dispatcher
from NeedfullThings import *
import EngFormat
import os



class EditTraces(QtGui.QDialog):
    def __init__(self, traces, parent=None):
        super(EditTraces,self).__init__(parent)

        self.ui = uic.loadUi("../Editor/EditTraces.ui", self)
        self.ret = None
        self.settingStart = sys.float_info.max
        self.settingStop = sys.float_info.min
        self.title = ''
        self.viewTableModel= None
        self.viewTableModel = TableModel(['StartFreq','StopFreq'])
        self.viewTableModel.beginResetModel()
        self.viewTableModel.removeRows(0, self.viewTableModel.rowCount())

        if traces != None:
            for trace  in traces:
                s = trace.split('-')
                self.viewTableModel.addData([s[0], s[1]])
                df = Format.StringToFloat(self,s[0])
                if df < self.settingStart:
                    self.settingStart = df
                df = Format.StringToFloat(self,s[1])
                if df > self.settingStop:
                    self.settingStop = df
        else:
            self.settingStart = 1e6
            self.settingStop = 1e9


        self.ui.tableView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.ui.lineEditStartFreq.setText(Format.FloatToString(self,self.settingStart,0))
        self.ui.lineEditStopFreq.setText(Format.FloatToString(self,self.settingStop,0))
        self.ui.lineEditStopFreq.setFocusPolicy(Qt.StrongFocus)
        self.viewTableModel.endResetModel()
        self.ui.tableView.setModel(self.viewTableModel)
        self.ui.tableView.resizeColumnsToContents()
        self.ui.tableView.doubleClicked.connect(self.onDoubleClick)

        self.ui.lineEditStartFreq.editingFinished.connect(self.fValidator)
        self.ui.lineEditStopFreq.editingFinished.connect(self.fValidator)
        self.ui.lineEditHz.editingFinished.connect(self.fValidator)
        self.BtnOk.clicked.connect(self.onBtnOk)
        self.BtnCancel.clicked.connect(self.onBtnCancel)
        self.BtnDivideCount.clicked.connect(self.onBtnDivideCount)
        self.BtnDivideHz.clicked.connect(self.onBtnDivideHz)
        self.setModal(True)
      #  self.show()

    def onDoubleClick(self,idx):
        pass

    def onBtnOk(self):
        retString = ''
        sf1 = Format.FloatToString(self, self.settingStart, 3)
        sf2 = Format.FloatToString(self, self.settingStop, 3)
        self.title = sf1 + '-' + sf2
        if self.viewTableModel.rowCount() > 0:
            for row in range(self.viewTableModel.rowCount()):
                index = self.viewTableModel.index(row, 0)
                sf1 = self.viewTableModel.data(index,Qt.DisplayRole)
                index = self.viewTableModel.index(row, 1)
                sf2 = self.viewTableModel.data(index,Qt.DisplayRole)
                retString += sf1 + '-' + sf2 + '\n'
            retStrings = retString.rstrip('\n')
        else:
            retStrings = self.title

        self.ret = retStrings
        self.close()
        pass

    def onBtnCancel(self):
        self.ret = None
        self.close()
        pass

    def onBtnDivideCount(self):
        if self.settingStart >= self.settingStop:
            msgBox = QtGui.QMessageBox()
            msgBox.setText('StopFrequency has to be greater than StartFrequency')
            msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
            _ret = msgBox.exec_()
            return

        count = self.ui.spinBox.value()

        df = (self.settingStop - self.settingStart)
        ret = divmod(df,count)
        ddf = ret[0]
        remainder = ret[1]
        fe = self.settingStop -  ddf/4
        self.viewTableModel.removeRows(0, self.viewTableModel.rowCount())

        f = self.settingStart
        while f < self.settingStop:
            f1 = f
            f2 = f1 + ddf
            if f2 >= fe:
                f2 = self.settingStop
            sf1 = Format.FloatToString(self,f1,3)
            sf2 = Format.FloatToString(self,f2,3)
            self.viewTableModel.addData([sf1, sf2])
            f = f2
        pass

    def onBtnDivideHz(self):
        if self.settingStart >= self.settingStop:
            msgBox = QtGui.QMessageBox()
            msgBox.setText('StopFrequency has to be greater than StartFrequency')
            msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
            _ret = msgBox.exec_()
            return

        sdf = self.ui.lineEditHz.text()
        df = Format.StringToFloat(self,sdf)
        range = self.settingStop - self.settingStart
        count = range / df
        if count > 100 or count < 1:
            msgBox = QtGui.QMessageBox()
            msgBox.setText('{0}Hz Range results in {1} Traces\n at least 1 Trace or max. 100 Traces are possible'.format(sdf,str(count)))
            msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
            _ret = msgBox.exec_()
            return

        self.viewTableModel.removeRows(0, self.viewTableModel.rowCount())
        f = self.settingStart
        while f < self.settingStop:
            f1 = f
            f2 = f1 + df
            if f2 >= self.settingStop:
                f2 = self.settingStop
            sf1 = Format.FloatToString(self,f1,3)
            sf2 = Format.FloatToString(self,f2,3)
            self.viewTableModel.addData([sf1, sf2])
            f = f2
        pass
        pass

    @staticmethod
    def editTraces(traces, parent = None):
        dialog = EditTraces(traces,parent)
        result = dialog.exec_()
        ret = dialog.ret
        return (ret)


    def fValidator(self):

        lineEditor = self.sender()
        s = lineEditor.text()

        f = Format.StringToFloat(self,s)
        sf = Format.FloatToString(self,f,0)
        lineEditor.setText(sf)
        if lineEditor == self.ui.lineEditStartFreq:
            self.settingStart = f
        if lineEditor == self.ui.lineEditStopFreq:
            self.settingStop = f
