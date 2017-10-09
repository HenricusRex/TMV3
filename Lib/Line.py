__author__ = 'heinz'


from NeedfullThings import *
from pydispatch import dispatcher
from EngFormat import Format
import configparser
import ast
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from Workbench import Ticket
import DB_Handler_TPL3

class Line(QtGui.QDialog):
    def __init__(self,parent,ID,edit):
        #global model
        super(Line,self).__init__(parent)
        try:
            self.ui = uic.loadUi("Line.ui", self)
        except:
            self.ui = uic.loadUi("../Lib/Line.ui",self)
        self.centerOnScreen()
        self.signals = Signal()
        self.formater = Format()
        self.ticket = Ticket
        self.line = 0
        self.edit = edit

        #Buttons
        self.ui.BtnAdd.clicked.connect(self.onBtnAdd)
        self.ui.BtnGet.clicked.connect(self.onBtnGet)
        self.ui.BtnDraw.clicked.connect(self.onBtnDraw)
        self.ui.tableWidget_2.cellChanged.connect(self.onCellChanged)

        #self.ui.BtnLoadAndResume.clicked.connect(self.onBtnLoadAndResume)
        if not edit:
            self.ui.BtnAdd.hide()
            self.ui.BtnDraw.hide()
            self.ui.BtnGet.hide()

        # create a figure
        self.figure_canvas = FigureCanvas(Figure())
        self.figure_canvas.setParent(self.ui.GrafikFrame)
        size = self.ui.GrafikFrame.frameSize()
        self.figure_canvas.setFixedSize(size)
         # and the axes for the figure
        self.axes = self.figure_canvas.figure.add_subplot(111)
        self.setAxes()
        self.figure_canvas.draw()
        #
        #access to Limit only via Editor => no Workbench-Process running => direct access to Workbench
        self.line = DB_Handler_TPL3.Tpl3Lines('../DB/TMV3Workbench.TPL3',ID)
       # dispatcher.send(self.signals.WB_GET_LINE, dispatcher.Anonymous,self.ticket)
        self.line.read()
        self.fillForm()

    def fillForm(self):
        _item1 = QtGui.QTableWidgetItem(self.line.title)
        _item2 = QtGui.QTableWidgetItem(self.line.version)
        _item3 = QtGui.QTableWidgetItem(self.line.date)
        _item4 = QtGui.QTableWidgetItem(self.line.comment)
        self.ui.tableWidget.setItem(0,0,_item1)
        self.ui.tableWidget.setItem(1,0,_item2)
        self.ui.tableWidget.setItem(2,0,_item3)
        self.ui.tableWidget.setItem(3,0,_item4)

        _row = self.ui.tableWidget_2.rowCount()
        _xyf = ast.literal_eval(self.line.data_xy)

        for it in _xyf:
            _itemX = MyTableWidgetItem(str(it[0]))
            _itemX.setTextAlignment(QtCore.Qt.AlignRight)
            _itemY = MyTableWidgetItem(str(it[1]))
            _itemY.setTextAlignment(QtCore.Qt.AlignRight)
            _row += 1
            self.ui.tableWidget_2.setRowCount(_row)
            self.ui.tableWidget_2.setItem(_row-1,0,_itemX)
            self.ui.tableWidget_2.setItem(_row-1,1,_itemY)

        self.onBtnDraw()

        if not self.edit:
            self.ui.tableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
            self.ui.tableWidget_2.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
    def setAxes(self):
        self.axes.set_ylabel('dBµV')
        self.axes.set_xlabel('Hz')
        self.axes.grid(True)
        self.axes.set_xscale('log')

    def onBtnDraw(self):
        _x = []
        _y = []
        _xmax = -1
        _xmin = 1e10
        _ymax = -200
        _ymin = 200

        self.axes.cla()
        self.setAxes()
            #_sdata = sorted(_data,key = lambda x: x[0])
        self.ui.tableWidget_2.sortItems(0,QtCore.Qt.AscendingOrder)
        _ret = self.ui.tableWidget_2.rowCount()

        for i in range (_ret):
            _item =  self.ui.tableWidget_2.item(i,0)
            _vf = self.formater.StringToFloat(_item.text())
            _x.append(_vf)
            if _vf > _xmax: _xmax = _vf
            if _vf < _xmin: _xmin = _vf

            _item =  self.ui.tableWidget_2.item(i,1)
            _vf = self.formater.StringToFloat(_item.text())
            _y.append(_vf)
            if _vf > _ymax: _ymax = _vf
            if _vf < _ymin: _ymin = _vf
        if _ymax - _ymin < 10:
            _ymid = (_ymax - _ymin)/ 2 + _ymin
            _ymid = round(_ymid,0)
            _ymax = _ymid + 5
            _ymin = _ymid - 5

        self.axes.set_xlim(_xmin, _xmax)
        self.axes.set_ylim(_ymin, _ymax)
        self.axes.plot(_x, _y, picker=5, color='red', ls='-', lw=3)
        self.figure_canvas.draw()

    def onBtnAdd(self):
        _ret = self.ui.tableWidget_2.rowCount()
        _ret += 1

        self.ui.tableWidget_2.setRowCount(_ret)

        _item1 = MyTableWidgetItem("0")
        _item1.setTextAlignment(QtCore.Qt.AlignRight)
        self.ui.tableWidget_2.setItem(_ret-1, 0, _item1)

        _item2 = MyTableWidgetItem("0")
        _item2.setTextAlignment(QtCore.Qt.AlignRight)
        self.ui.tableWidget_2.setItem(_ret-1, 1, _item2)

    def onBtnGet(self):
        _ret = self.ui.tableWidget_2.rowCount()

        for i in range (_ret):
            print(self.ui.tableWidget_2.item(i,0).text)

    def onCellChanged(self,x,y):
        _item =  self.ui.tableWidget_2.item(x,y)
        _v = _item.text()
        _value = self.formater.StringToFloat(_v)
        if y == 0:
            _formValue = self.formater.FloatToString(_value, 3)
            self.ui.tableWidget_2.item(x,y).setText(_formValue)
        if y == 1:

            _formValue = self.formater.FloatToString(_value, 1)
            self.ui.tableWidget_2.item(x,y).setText(_formValue)

    def _fill_form(self):
        pass

    def onBtnFwd(self):
        pass

    def onBtnFFwd(self):
        pass

    def onBtnRwd(self):
        pass

    def onBtnFRwd(self):
        pass

    def onBtnCancel(self):
        #print('onBtnCancel')
        self.close()
        pass

    def onBtnOk(self):
        self.onBtnSaveDescription()
        self._config['ControllerDefaults']['current_testID'] = str(self._current_testID)
        self._config['ControllerDefaults']['current_planID'] = str(self._current_planID)
        with open('../TMV3.ini','w')as configfile:
            self._config.write(configfile)

        self.close()


    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))


    def onClose(self):
        self.close()

class MyTableWidgetItem(QtGui.QTableWidgetItem):
    def __lt__(self, other):
        if ( isinstance(other, QtGui.QTableWidgetItem) ):
            form = Format()

            _my_value_string = self.data(QtCore.Qt.EditRole)
            _my_value = form.StringToFloat(_my_value_string)

            _other_value_string = other.data(QtCore.Qt.EditRole)
            _other_value = form.StringToFloat(_other_value_string)

            #my_value, my_ok = self.data(QtCore.Qt.EditRole).toInt()
            #other_value, other_ok = other.data(QtCore.Qt.EditRole).toInt()

            return _my_value < _other_value

        return super(MyTableWidgetItem, self).__lt__(other)