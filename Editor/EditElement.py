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

class CellChooseList(QtGui.QDialog):

    def __init__(self,table, row, text,cList, parent = None):
        QtGui.QDialog.__init__(self)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        layout = QtGui.QGridLayout(self)
        self.cL = chooseListWidget(self)
        self.cL.clicked.connect(self.dClicked)
        self.cList = cList
        self.ret = False
        self.retChoose = ''
        self.dc = False
        self.row = row
        self.table = table
        table.setCellWidget(row,0,self)
        _height = len(cList) * 20 + 10
        self.setFixedHeight(_height)


        for i in\
                cList:
            self.cL.addItem(i)

        self.cL.setCurrentRow(cList.index(text))

        layout.addWidget(self.cL)
        layout.setMargin(1)


    def focusOutEvent(self, event):
        if self.dc:
            #focus lost by doubleClicked
            return
        if self.cL.hasFocus():
            #focus changed to ListWidget
            return

        self.cancel()

    def cancel(self) :
        self.retChoose = ''
        self.ret = False
        self.table.removeCellWidget(self.row,0)
        print ('cancel')
        self.close()

    def dClicked(self,mId):
        self.dc = True

        _text = self.cList[mId.row()]
        self.retChoose = _text
        self.ret = True
        self.close()

class CellEdit(QtGui.QDialog):

    def __init__(self,table, row, text, parent = None):
        QtGui.QDialog.__init__(self)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        layout = QtGui.QGridLayout(self)
        self.ed = PlainTextEdit(self)
        self.ed.setPlainText(text)
#        self.ed.doubleClicked.connect(self.dClicked)
        self.ret = False
        self.retText = ''
        self.dc = False
        self.row = row
        self.table = table
        table.setCellWidget(row,0,self)
        _height = 200
        self.setFixedHeight(_height)
        layout.addWidget(self.ed)
        layout.setMargin(1)


    def focusOutEvent(self, event):
        if self.dc:
            #focus lost by doubleClicked
            return
        if self.ed.hasFocus():
            #focus changed to ListWidget
            return

        self.cancel()

    def cancel(self) :
        self.ret = False
        self.table.removeCellWidget(self.row,0)
        print ('cancel')
        self.close()

    def dClicked(self,mId):
        self.dc = True

        _text = self.cList[mId.row()]
        self.retChoose = _text
        self.ret = True
        self.close()


class chooseListWidget(QtGui.QListWidget):
    def __init__(self,parent):
        QtGui.QListWidget.__init__(self)

        self.parent = parent

    def focusOutEvent(self, event):
        self.parent.cancel()

class PlainTextEdit(QtGui.QPlainTextEdit):
    def __init__(self,parent):
        QtGui.QPlainTextEdit.__init__(self)

        self.parent = parent

    def focusOutEvent(self, event):
        self.parent.cancel()
