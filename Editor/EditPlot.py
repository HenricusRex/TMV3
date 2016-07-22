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

        self.ui.tableWidget.doubleClicked.connect(self.dClicked)


        self.chooseDB = EditElement.MyChooseList()
        self.chooseDB.addItem('5 dB')
        self.chooseDB.addItem('10 dB')
        self.chooseDB.addItem('15 dB')
        self.chooseDB.addItem('20 dB')

        self.cBoxScale = QtGui.QComboBox()
        self.cBoxScale.addItem('logarithmic')
        self.cBoxScale.addItem('linear')

        self.cBoxUnit = QtGui.QComboBox()
        self.cBoxUnit.addItem('dBµV')
        self.cBoxUnit.addItem('dBm')
        self.cBoxUnit.addItem('dBµV/m')
        self.cBoxUnit.addItem('dB')




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

        _div = (_plot.y2 -_plot.y1) / 10
        if _div < 10:
            self.setCell('dB','5')
        elif _div < 15:
            self.setCell('dB','10')
        elif _div < 20:
            self.setCell('dB','15')
        elif _div >= 20:
            self.setCell('dB','20')

        #self.setCellComboBox('dB',self.cBoxDB)

        if _plot.log:
            self.cBoxScale.setCurrentIndex(0)
        else:
            self.cBoxScale.setCurrentIndex(1)
        self.setCellComboBox('Scale',self.cBoxScale)

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

    def dClicked(self,mi):
       # self.blockSignals(True)
        _row = mi.row()
        _col = mi.column()
        _itemHeader = self.ui.tableWidget.verticalHeaderItem(_row)
        header = _itemHeader.text()
        if header.startswith('dB'):
            _item = self.ui.tableWidget.item(_row, _col)
            _db = _item.text()
            print(_db)
            if _db == '5':
                self.chooseDB.setCurrentRow(0)
            elif _db == '10':
                self.chooseDB.setCurrentRow(1)
            elif _db == '15':
                self.chooseDB.setCurrentRow(2)
            elif _db == '20':
                self.chooseDB.setCurrentRow(3)

            self.ui.tableWidget.setCellWidget(_row ,0,self.chooseDB)

            _rec = self.chooseDB.parent().pos()
            print (_rec)
         #   self.chooseDB.setParent(self.ui.tableWidget)
            _yPos = _row*self.ui.tableWidget.rowHeight(_row)
            _width = self.ui.tableWidget.columnWidth(0)
         #   self.chooseDB.setGeometry(_rec.x(),_rec.y()+(_row*self.ui.tableWidget.rowHeight(5)),200,200)
            self.chooseDB.setGeometry(0,_yPos,_width,200)

            self.chooseDB.show()

            pass
        elif header.startswith('Scale'):
            pass
        elif header.startswith('Unit'):
            pass
        else:
            pass

        pass
       # self.blockSignals(False)