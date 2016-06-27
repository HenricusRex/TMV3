__author__ = 'heinz'

from pydispatch import dispatcher
from NeedfullThings import *
from DB_Handler_TDS3 import *
import EditElement

class EditPlot(EditElement.EditElement):
    def __init__(self, parent=None):
        super(EditPlot, self).__init__()
        self.ui = uic.loadUi("EditorPlot.ui", self)
        dispatcher.connect(self.onFillPlotID,signal=self.signals.EDIT_PLOTID,sender=dispatcher.Any)
        pass
    pass
    def onFillPlotID(self,par1,par2):
        filename = par1
        ID = par2
        print ('filename,ID',filename,ID)
        _plot = DatasetPlot(filename,ID)
        _plot.read()
        self.setCell('Title',_plot.title)
        self.setCell('Start',str(_plot.x1))
        self.setCell('Stop',str(_plot.x2))
        self.setCell('Ref',str(_plot.y2))

        self.cBoxDB = QtGui.QComboBox()
        self.cBoxDB.addItem('5 dB')
        self.cBoxDB.addItem('10 dB')
        self.cBoxDB.addItem('15 dB')
        self.cBoxDB.addItem('20 dB')
        _div = (_plot.y2 -_plot.y1) / 10
        if _div < 9:
            self.cBoxDB.setCurrentIndex(0) #5dB
        elif _div < 14:
            self.cBoxDB.setCurrentIndex(1) #10dB
        elif _div < 19:
            self.cBoxDB.setCurrentIndex(2) #15dB
        else:
            self.cBoxDB.setCurrentIndex(3) #20dB
        self.setCellComboBox('dB',self.cBoxDB)

        self.cBoxScale = QtGui.QComboBox()
        self.cBoxScale.addItem('logarithmic')
        self.cBoxScale.addItem('linear')
        if _plot.log:
            self.cBoxScale.setCurrentIndex(0)
        else:
            self.cBoxScale.setCurrentIndex(1)
        self.setCellComboBox('Scale',self.cBoxScale)

        self.cBoxUnit = QtGui.QComboBox()
        self.cBoxUnit.addItem('dBµV')
        self.cBoxUnit.addItem('dBm')
        self.cBoxUnit.addItem('dBµV/m')
        self.cBoxUnit.addItem('dB')
        if _plot.unit == 'dBµV':
            self.cBoxUnit.setCurrentIndex(0)
        elif _plot.unit == 'dBm':
            self.cBoxUnit.setCurrentIndex(1)
        elif _plot.unit == 'dBµV/m':
            self.cBoxUnit.setCurrentIndex(2)
        elif _plot.unit == 'dB':
            self.cBoxUnit.setCurrentIndex(3)
        self.setCellComboBox('Unit',self.cBoxUnit)


        self.setCell('Anno',_plot.annotation)
        self.setCell('Comment',_plot.comment)

