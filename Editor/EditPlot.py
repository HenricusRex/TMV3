__author__ = 'heinz'

from pydispatch import dispatcher
from NeedfullThings import *
from DB_Handler_TDS3 import *
import EditElement
import EngFormat

class EditPlot(EditElement.EditElement):

    def __init__(self, parent=None):
        super(EditPlot, self).__init__()
        self.ui = uic.loadUi("EditorPlot.ui", self)
        dispatcher.connect(self.onFillPlotID,signal=self.signals.EDIT_PLOTID,sender=dispatcher.Any)

        self.ui.tableWidget.doubleClicked.connect(self.dClicked)
        self.chooseListDBDEV = ['5', '10', '15', '20']
        self.chooseListSCALE = ['logarithmic', 'linear']
        self.chooseListUNIT = ['dBµV', 'dBm','dBµV/m', 'dB']




    pass
    def onFillPlotID(self,par1,par2):
        filename = par1
        ID = par2

        _plot = DatasetPlot(filename,ID)
        _plot.read()
        self.setCell(self.ui.tableWidget,'Title',_plot.title)
        self.setCell(self.ui.tableWidget,'Start',str(_plot.x1))
        self.setCell(self.ui.tableWidget,'Stop',str(_plot.x2))
        self.setCell(self.ui.tableWidget,'Ref',str(_plot.y2))

        _div = (_plot.y2 -_plot.y1) / 10
        _db = str(round(_div/5)*5)
        self.setCell(self.ui.tableWidget,'dB',_db)

        if _plot.log:
            self.setCell(self.ui.tableWidget,'Scale','logarithmic')
        else:
            self.setCell(self.ui.tableWidget,'Scale','linear')

        self.setCell(self.ui.tableWidget,'Unit',_plot.unit)
        self.setCell(self.ui.tableWidget,'Anno',_plot.annotation)
        self.setCell(self.ui.tableWidget,'Comment',_plot.comment)

    def dClicked(self,mi):

        _row = mi.row()
        _col = mi.column()
        _itemHeader = self.ui.tableWidget.verticalHeaderItem(_row)
        header = _itemHeader.text()
        if header.startswith('dB'):
            _item = self.ui.tableWidget.item(_row, _col)
            _text = _item.text()
            _cl = EditElement.CellChooseList(self.ui.tableWidget,_row,_text,self.chooseListDBDEV)
            _cl.exec_()

            if _cl.ret:
                self.setCell('dB',_cl.retChoose)

        elif header.startswith('Scale'):
            _item = self.ui.tableWidget.item(_row, _col)
            _text = _item.text()
            _cl = EditElement.CellChooseList(self.ui.tableWidget,_row,_text,self.chooseListSCALE)
            _cl.exec_()

            if _cl.ret:
                self.setCell('Scale',_cl.retChoose)

        elif header.startswith('Unit'):
            _item = self.ui.tableWidget.item(_row, _col)
            _text = _item.text()
            _cl = EditElement.CellChooseList(self.ui.tableWidget,_row,_text,self.chooseListUNIT)
            _cl.exec_()

            if _cl.ret:
                self.setCell('Unit',_cl.retChoose)

        elif header.startswith('Anno'):
            _item = self.ui.tableWidget.item(_row, _col)
            _text = _item.text()
            _pe = EditElement.CellEditPlain(self.ui.tableWidget,_row,_text)
            _pe.exec()

            if _pe.ret:
                self.setCell('Anno',_pe.newText)

        elif header.startswith('Comm'):
            _item = self.ui.tableWidget.item(_row, _col)
            _text = _item.text()
            _pe = EditElement.CellEditPlain(self.ui.tableWidget,_row,_text)
            _pe.exec()

            if _pe.ret:
                self.setCell('Comm',_pe.newText)

        else:
            pass

        pass
       # self.blockSignals(False)