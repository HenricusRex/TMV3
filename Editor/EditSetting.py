__author__ = 'heinz'

from pydispatch import dispatcher
from NeedfullThings import *
from DB_Handler_TDS3 import *
from DB_Handler_TPL3 import Tpl3Lines
import EditElement
import os
import ast

BASE_MODE,COMMAND_MODE,TRACE_MODE = (0, 1, 2)

class EditSetting(EditElement.EditElement):
    def __init__(self, parent=None):
        super(EditSetting, self).__init__()
        self.ui = uic.loadUi("EditorSetting.ui", self)
        self.config = configparser.ConfigParser()
        self.config.read('../Lib/TMV3.ini')
        self.workBenchDB = self.config['DataBases']['workbench']
        self.settingID = 0
        self.filename = ''
        self.mode = BASE_MODE
        self.editBase = EditSettingBase(self)
        dispatcher.connect(self.onFillSettingID,signal=self.signals.EDIT_ROUTINEID,sender=dispatcher.Any)
        self.editBase.fillTable(self.filename,self.settingID)


    pass
    def onFillSettingID(self,par1,par2):
        self.filename = par1
        self.settingID = par2
    def onTabChanged(self,idx):
        self.mode = idx
        pass
    def onCellClicked(self,row,column):
        self.selectedTableItem.append(row)
        self.selectedTableItem.append(column)
        _item = self.ui.tableWidget.itemAt(row,column)
        self.selectedTableItem.append(_item.text())
        self.selectedTableItem.append(_item.data([0]))
        print (self.selectedTableItem)
        pass
    def onDelItem(self):
#        _modelIdx = self.ui.tableWidget.selectedIndexes()[0]

        ret = self.ui.tableWidget.currentRow()
        ret = self.ui.tableWidget.selectedItems()
        if self.ui.tableWidget.currentItem() == None:
            return

        _row = self.ui.tableWidget.currentRow()
        self.ui.tableWidget.removeRow(_row)



class EditSettingBase(EditElement.EditElement):
    def __init__(self, parent=None):
        super(EditSettingBase, self).__init__()

    pass

    def onCellClicked(self,row,column):
        self.selectedTableItem.append(row)
        self.selectedTableItem.append(column)
        _item = self.ui.tableWidget.itemAt(row,column)
        self.selectedTableItem.append(_item.text())
        self.selectedTableItem.append(_item.data([0]))
        print (self.selectedTableItem)

    def fillTable(self,par1,par2):
        filename = par1
        ID = par2
        _setting = DatasetSetting(filename,ID)
        _setting.read()

        self.setCell('Title',_setting.title)
        self.setCell('Start',str(_setting.start_freq))
        self.setCell('Stop',str(_setting.stop_freq))
        if _setting.autorange:
            self.setCell('Auto','yes')
        else:
            self.setCell('Auto','no')
        self.setCell('Order',str(_setting.order))
        self.setCell('Inst',_setting.instruction)
        if _setting.step_width == 0:
            self.ui.RBtnSweep.checked = True
        else:
            self.ui.RBtnStep.checked = True








