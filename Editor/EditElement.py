__author__ = 'heinz'

from NeedfullThings import *
from DB_Handler_TDS3 import *

class EditElement(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.signals = Signal()


        pass
    pass





    def setCell(self,name,value):

        if value == None: return
        #loop through headers and find column number for given column name
        _headerCount = self.ui.tableWidget.rowCount()
        for x in range(_headerCount):

            _headerText = self.ui.tableWidget.verticalHeaderItem(x).text()
            if _headerText.startswith (name):

                _item = QtGui.QTableWidgetItem(value)
                self.ui.tableWidget.setItem(x,0,_item)
                break

      # cell = widget.item(row,matchcol).text()   # get cell at row, col

       # return cell
    def setCellPlainText(self,name,object):
        if object == None: return
        _headerCount = self.ui.tableWidget.rowCount()
        for x in range(_headerCount):

            _headerText = self.ui.tableWidget.verticalHeaderItem(x).text()
            if _headerText.startswith(name):
                _item = object
                self.ui.tableWidget.setCellWidget(x,0,_item)
                _h = self.ui.tableWidget.rowHeight(x)
                print('_h =',_h)
                self.ui.tableWidget.setRowHeight(x,3 * _h)
                break
    def setCellComboBox(self,name,cBox):
        if cBox == None: return
        #loop through headers and find column number for given column name
        _headerCount = self.ui.tableWidget.rowCount()
        for x in range(_headerCount):

            _headerText = self.ui.tableWidget.verticalHeaderItem(x).text()
            if _headerText.startswith(name):
                _item = cBox
                self.ui.tableWidget.setCellWidget(x,0,_item)
                break
    def setCellButton(self,name, pButton):
        if pButton == None: return
        #loop through headers and find column number for given column name
        _headerCount = self.ui.tableWidget.rowCount()
        for x in range(_headerCount):

            _headerText = self.ui.tableWidget.verticalHeaderItem(x).text()
            if _headerText.startswith(name):
                _item = pButton
                self.ui.tableWidget.setCellWidget(x,0,_item)
                break

    def insertCellComboBox(self,name,cBox):
        if cBox == None: return
        #loop through headers and find column number for given column name
        _headerCount = self.ui.tableWidget.rowCount()
        for x in range(_headerCount):

            _headerText = self.ui.tableWidget.verticalHeaderItem(x).text()
            if _headerText.startswith(name):
                _item = cBox
                y = self.ui.tableWidget.insertRow()
                self.ui.tableWidget.setCellWidget(y,0,_item)
                break
