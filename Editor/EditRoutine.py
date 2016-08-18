__author__ = 'heinz'

from pydispatch import dispatcher
from NeedfullThings import *
from DB_Handler_TDS3 import *
from DB_Handler_TPL3 import Tpl3Lines
import EditElement
import os
import ast

class EditRoutine(EditElement.EditElement):
    def __init__(self, parent=None):
        super(EditRoutine, self).__init__()
        self.ui = uic.loadUi("EditorRoutine.ui", self)
        self.config = configparser.ConfigParser()
        self.config.read('../Lib/TMV3.ini')
        self.workBenchDB = self.config['DataBases']['workbench']
        self.driverList = []
        self.limList = []
        self.limObList = []
        self.getDeviceList()
        self.getLimitList()

        self.limitComboBoxes = []

        dispatcher.connect(self.onFillRoutineID,signal=self.signals.EDIT_ROUTINEID,sender=dispatcher.Any)
        dispatcher.connect(self.onAddLimit,signal=self.signals.EDIT_ADD_LIMIT,sender=dispatcher.Any)
        dispatcher.connect(self.onAddLine,signal=self.signals.EDIT_ADD_LINE,sender=dispatcher.Any)
        dispatcher.connect(self.onAddDevice,signal=self.signals.EDIT_ADD_DEVICE,sender=dispatcher.Any)
        dispatcher.connect(self.onDelItem,signal=self.signals.EDIT_DEL_ITEM,sender=dispatcher.Any)
     #   self.ui.tableWidget.cellClicked.connect(self.onCellClicked)
        self.selectedTableItem = []
        self.firstStart = False
    pass
    def onCellClicked(self,row,column):
        self.selectedTableItem.append(row)
        self.selectedTableItem.append(column)
        _item = self.ui.tableWidget.itemAt(row,column)
        self.selectedTableItem.append(_item.text())
        self.selectedTableItem.append(_item.data([0]))
        print (self.selectedTableItem)


    def onAddLimit(self):
        cb = self.getLimitCB('')
        self.limitComboBoxes.append(cb)
        _rowPosition = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(_rowPosition)
        _item = QtGui.QTableWidgetItem("LimitCB")
        _idx = len(self.limitComboBoxes)-1
        _item.setData(Qt.UserRole,_idx)

        self.ui.tableWidget.setVerticalHeaderItem(_rowPosition,QtGui.QTableWidgetItem("Limit"))
        self.ui.tableWidget.setItem(_rowPosition,0,_item)
        self.ui.tableWidget.setCellWidget(_rowPosition,0,cb)
        self.limObList.append(cb)




        pass
    def onAddLine(self):
        cb = self.getLimitCB('')
        self.limitComboBoxes.append(cb)
        _rowPosition = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(_rowPosition)
        _item = QtGui.QTableWidgetItem("LimitCB")
        _idx = len(self.limitComboBoxes)-1
        _item.setData(Qt.UserRole,_idx)

        self.ui.tableWidget.setVerticalHeaderItem(_rowPosition,QtGui.QTableWidgetItem("Limit"))
        self.ui.tableWidget.setItem(_rowPosition,0,_item)
        self.ui.tableWidget.setCellWidget(_rowPosition,0,cb)
        self.limObList.append(cb)
        pass
    def onAddDevice(self):
        pass
    def onDelItem(self):
#        _modelIdx = self.ui.tableWidget.selectedIndexes()[0]

        ret = self.ui.tableWidget.currentRow()
        print(ret)
        ret = self.ui.tableWidget.selectedItems()
        print(ret)
        print(self.ui.tableWidget.currentItem().data(0))
        if self.ui.tableWidget.currentItem() == None:
            return

        if self.ui.tableWidget.currentItem().data(Qt.DisplayRole) == 'LimitCB':
            _id = self.ui.tableWidget.currentItem().data(Qt.UserRole)
            #self.limitComboBoxes.pop(_id)
            _row = self.ui.tableWidget.currentRow()
            self.ui.tableWidget.removeRow(_row)
#            self.ui.tableWidget.show()

    def onFillRoutineID(self,par1,par2):
        if self.firstStart: return
        self.firstStart = True
        filename = par1
        ID = par2
        print ('filename,ID',filename,ID)

        _routine = DatasetRoutine(filename,ID)
        _routine.read()
        self.setCell('Title',_routine.title)


        self.cBoxSC = QtGui.QComboBox()
        self.cBoxSC.addItem('1')
        self.cBoxSC.addItem('2')
        if _routine.signal_class == '1':
            self.cBoxSC.setCurrentIndex(0)
        else:
            self.cBoxSC.setCurrentIndex(1)
        self.setCellComboBox('SignalClass',self.cBoxSC)

        self.pTextInstruction = QtGui.QPlainTextEdit()
        self.pTextInstruction.setPlainText(str(_routine.instruction))
        self.setCellPlainText('InstructionText',self.pTextInstruction)

        if _routine.instruction_file == None:
            self.setCell('InstructionFile','None')
        else:
            self.setCell('InstructionFile',_routine.instruction_file)

        self.pTextComment = QtGui.QPlainTextEdit()
        self.pTextComment.setPlainText(str(_routine.instruction))
        self.setCellPlainText('Comment',self.pTextComment)

        #Limits
        self.getLimitList()
        _rLimits = ast.literal_eval(_routine.limits)
        for i in _rLimits:
            _cb = self.getLimitCB(i)
            self.limitComboBoxes.append(_cb)
            idx = len(self.limitComboBoxes)-1

            _rowPosition = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(_rowPosition)
            _item = QtGui.QTableWidgetItem("LimitCB")
            _item.setData(Qt.UserRole,idx)
            self.ui.tableWidget.setVerticalHeaderItem(_rowPosition,QtGui.QTableWidgetItem("Limit"))
            self.ui.tableWidget.setItem(_rowPosition,0,_item)
            self.ui.tableWidget.setCellWidget(_rowPosition,0,_cb)



    def getDeviceList(self):

        for _file in os.listdir('../DeviceDriver'):
            if _file.startswith('DD_'):
                self.driverList.append(_file)

    def getLimitList(self):

        ll = Tpl3Lines(self.workBenchDB,0)
        ret, lim = ll.readLimitTitles()
        return lim
    def getLineList(self):
        ll = Tpl3Lines(self.workBenchDB,0)
        ret, lines = ll.readLineTitles()
        return lines

    def getLimitCB(self,limit):
        _cb =  self.cBoxSC = QtGui.QComboBox()
        for i,val  in enumerate(self.limList):
            _si = '{}, Version {}'.format(val[0],val[1])
            _cb.addItem(_si,(i)) #store also index of limitlist and index of comboboxlist

        if limit != '':
            idx = _cb.findText('{}, Version {}'.format(limit[0],limit[1]))
            if idx >= 0:
                _cb.setCurrentIndex(idx)

        return _cb

    def getLineCB(self,line):
        _cb =  self.cBoxSC = QtGui.QComboBox()
        for i,val  in enumerate(self.lineList):
            _si = '{}, Version {}'.format(val[0],val[1])
            _cb.addItem(_si,(i)) #store also index of limitlist and index of comboboxlist

        if line != '':
            idx = _cb.findText('{}, Version {}'.format(line[0],line[1]))
            if idx >= 0:
                _cb.setCurrentIndex(idx)

        return _cb