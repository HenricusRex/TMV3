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
        self.ui.tableWidget.cellChanged.connect(self.cChanged)

        self.chooseListDBDEV = ['5 dB', '10 dB', '15 dB', '20 dB']
        self.chooseListSCALE = ['logarithmic', 'linear']
        self.chooseListUNIT = ['dBµV', 'dBm','dBµV/m', 'dB']
        self.formater = EngFormat.Format()



    pass
    def onFillPlotID(self,par1,par2):
        filename = par1
        ID = par2

        _plot = DatasetPlot(filename,ID)
        _plot.read()
        self.setCell('Title',_plot.title)

        self.setCell('Start',self.formater.FloatToString(_plot.x1, 0))
        self.setCell('Stop',self.formater.FloatToString(_plot.x2, 0))
        self.setCell('Ref',self.formater.FloatToString(_plot.y2, 0))

        _div = (_plot.y2 -_plot.y1) / 10
        if _div < 10:
            self.setCell('dB','5 dB')
        elif _div < 15:
            self.setCell('dB','10 dB')
        elif _div < 20:
            self.setCell('dB','15 dB')
        elif _div >= 20:
            self.setCell('dB','20 dB')


        if _plot.log:
            self.setCell('Scale','logarithmic')
        else:
            self.setCell('Scale','linear')

        if _plot.unit == 'dBµV':
            self.setCell('Unit','dBµV')
        elif _plot.unit == 'dBm':
            self.setCell('Unit','dBm')
        elif _plot.unit == 'dBµV/m':
            self.setCell('Unit','dBµV/m')
        elif _plot.unit == 'dB':
            self.setCell('Unit','dB')

        self.setCell('Anno',_plot.annotation)
        self.setCell('Comment',_plot.comment)

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


        else:
            pass

        pass
       # self.blockSignals(False)
    def cChanged(self,row,col):
        self.ui.tableWidget.blockSignals(True)
        _itemHeader = self.ui.tableWidget.verticalHeaderItem(row)
        header = _itemHeader.text()

        #try to build a valid float value in eng format
        if header.startswith('Start'):
            _item = self.ui.tableWidget.item(row, col)
            _text = _item.text()
            _fStartFreq = self.formater.StringToFloat(_text)
            _sStartFreq = self.formater.FloatToString(_fStartFreq,0)
            _item.setText(_sStartFreq)

        if header.startswith('Stop'):
            _item = self.ui.tableWidget.item(row, col)
            _text = _item.text()
            _fStopFreq = self.formater.StringToFloat(_text)
            _sStopFreq = self.formater.FloatToString(_fStopFreq,0)
            _item.setText(_sStopFreq)

        if header.startswith('Ref'):
            _item = self.ui.tableWidget.item(row, col)
            _text = _item.text()
            _fRef = self.formater.StringToFloat(_text)
            _sRef = self.formater.FloatToString(_fRef,0)
            _item.setText(_sRef)

        self.ui.tableWidget.blockSignals(False)
