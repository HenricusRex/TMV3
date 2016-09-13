__author__ = 'heinz'

from NeedfullThings import *
from DB_Handler_TDS3 import *
import EditElement

class EditPlan(EditElement.EditElement):
    def __init__(self, parent=None):
        super(EditPlan, self).__init__()

        self.ui = uic.loadUi("EditorPlan.ui", self)
        self.config = configparser.ConfigParser()
        self.config.read('../Lib/TMV3.ini')

        dispatcher.connect(self.onFillPlanID,signal=self.signals.EDIT_PLANID,sender=dispatcher.Any)
        self.ui.tableWidget.doubleClicked.connect(self.dClicked)
        assert isinstance(self.ui.tableWidget,QtGui.QTableWidget)
        self.ui.tableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
#        self.ui.tableWidget.setSelection()

        self.chooseListYesNo = ['Yes','No']


        pass
    pass



    def onFillPlanID(self,par1,par2):

        QtGui.QApplication.setOverrideCursor((QtGui.QCursor(Qt.WaitCursor)))

        filename = par1
        ID = par2

        print ('filename,ID',filename,ID)
        _plan = DatasetPlan(filename)
        _plan.read()
        self.setCell(self.ui.tableWidget,'Title',_plan.title)
        self.setCell(self.ui.tableWidget,'Version',_plan.version)
        self.setCell(self.ui.tableWidget,'TMV3 Version',_plan.tmv_version)
        self.setCell(self.ui.tableWidget,'KMV',_plan.kmv)
        self.setCell(self.ui.tableWidget,'Zooning',_plan.zooning)
        self.setCell(self.ui.tableWidget,'NATO',_plan.nato)
        self.setCell(self.ui.tableWidget,'Company',_plan.company)
        self.setCell(self.ui.tableWidget,'Operator',_plan.operator)
        self.setCell(self.ui.tableWidget,'Date',_plan.date)
        self.setCell(self.ui.tableWidget,'Comment',_plan.comment)

        QtGui.QApplication.restoreOverrideCursor()

    def dClicked(self,mi):

        _row = mi.row()
        _col = mi.column()
        _itemHeader = self.ui.tableWidget.verticalHeaderItem(_row)
        header = _itemHeader.text()
        if header.startswith('KMV'):
            _item = self.ui.tableWidget.item(_row, _col)
            _text = _item.text()
            _cl = EditElement.CellChooseList(self.ui.tableWidget,_row,_text,self.chooseListYesNo)
            _cl.exec_()
            if _cl.ret:
                self.setCell('KMV',_cl.retChoose)

        elif header.startswith('NATO'):
            _item = self.ui.tableWidget.item(_row, _col)
            _text = _item.text()
            _cl = EditElement.CellChooseList(self.ui.tableWidget,_row,_text,self.chooseListYesNo)
            _cl.exec_()
            if _cl.ret:
                self.setCell('NATO',_cl.retChoose)

            self.ui.tableWidget.setSelection(self.ui.tableWidget.indexAt(mi))

        elif header.startswith('Zooning'):
            _item = self.ui.tableWidget.item(_row, _col)
            _text = _item.text()
            _cl = EditElement.CellChooseList(self.ui.tableWidget,_row,_text,self.chooseListYesNo)
            _cl.exec_()
            if _cl.ret:
                self.setCell('Zooning',_cl.retChoose)

        elif header.startswith('Date'):
            _item = self.ui.tableWidget.item(_row, _col)
            _text = _item.text()
            _cl = EditElement.CellChooseList(self.ui.tableWidget,_row,_text)
            _cl.exec_()
            if _cl.ret:
                self.setCell('Scale',_cl.retChoose)

        elif header.startswith('Comment'):
            _item = self.ui.tableWidget.item(_row, _col)
            _text = _item.text()
            _cl = EditElement.CellEdit(self.ui.tableWidget,_row,_text)
            _cl.exec_()

            if _cl.ret:
                self.setCell('Unit',_cl.retChoose)


        else:
            pass

        pass