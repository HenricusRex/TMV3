__author__ = 'heinz'

from pydispatch import dispatcher
from NeedfullThings import *
from DB_Handler_TDS3 import *
from DB_Handler_TPL3 import Tpl3Lines
import EditElement
import EngFormat
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
        self.formater = EngFormat.Format()
        dispatcher.connect(self.onFillSettingID,signal=self.signals.EDIT_SETTINGID,sender=dispatcher.Any)



    pass
    def onFillSettingID(self,par1,par2):
        self.filename = par1
        self.settingID = par2
        self.fillTable(self.filename,self.settingID)
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

    def fillTable(self,par1,par2):
        if self.mode == BASE_MODE:
            filename = par1
            ID = par2
            _setting = DatasetSetting(filename,ID)
            _setting.read()

            self.setCell(self.ui.tableWidget_0,'Title',_setting.title)
            self.setCell(self.ui.tableWidget_0,'Start',self.formater.FloatToString(_setting.start_freq,0))
            self.setCell(self.ui.tableWidget_0,'Stop',self.formater.FloatToString(_setting.stop_freq,0))
            if _setting.autorange:
                self.setCell(self.ui.tableWidget_0,'Auto','yes')
            else:
                self.setCell(self.ui.tableWidget_0,'Auto','no')
            self.setCell(self.ui.tableWidget_0,'Order',str(_setting.order))
            self.setCell(self.ui.tableWidget_0,'Inst',_setting.instruction)
            if _setting.step_width == 0:
                self.ui.RBtnSweep.checked = True
            else:
                self.ui.RBtnStep.checked = True



class EditSettingBase(EditElement.EditElement):
    def __init__(self,ui ,parent=None):
        super(EditSettingBase, self).__init__()
        self.ui = ui
        self.parent = parent
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








