__author__ = 'Heinz'
from NeedfullThings import *
from pydispatch import dispatcher
from EngFormat import Format
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.pagesizes import portrait
from reportlab.lib.units import mm
import configparser
import os
import subprocess
import pickle
import ast
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from Workbench import Ticket
from DB_Handler_TPL3 import TPL3Test

class Protocol(QtGui.QDialog):
    update = QtCore.pyqtSignal()
    def __init__(self,test,project=None):
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("Protocol.ui", self)
        self.centerOnScreen()
        self._config = configparser.ConfigParser()
        self._config.read('TMV3.ini')
        self.ret = False
        assert isinstance(test,TPL3Test)
        self.currentTest = test
        self.currentProject = project
        self.canvas = ''
        self.leftMargin = 25
        self.leftOffset1 = 10
        self.leftOffset2 = 50

        self.ui.lbTestNo.setText(test.test_no)
 #       self.editElements=QtGui.QTextEdit(test.elements)
        self.editEnvironment = QtGui.QTableWidget(0,2)
        self.editEnvironment.setHorizontalHeaderLabels(['Title','Serial-No.'])
        self.editEnvironment.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows|QtGui.QAbstractItemView.SingleSelection)
        self.editComment = QtGui.QTextEdit()
        _envRow = 0
   #     print(test.environment)
        if test.environment:
            try:
                enList = test.environment.split(',')
                for n in range (0,len(enList)-1, 2):
                    self.editEnvironment.insertRow(_envRow)
                    self.editEnvironment.setItem(_envRow, 0, QtGui.QTableWidgetItem(enList[n]))
                    self.editEnvironment.setItem(_envRow ,1, QtGui.QTableWidgetItem(enList[n+1]))
                    _envRow += 1
            except Exception as _err:
                print(_err)

        self.editComment=QtGui.QTextEdit(test.comment)
     #   self.ui.textEdit.setText("Dies ist ein Test /n in der zweiten Zeile")
        if self.currentProject is not None:
            self.ui.tableWidget.setItem(0,0,QtGui.QTableWidgetItem(project.title))
            self.ui.tableWidget.setItem(9,0,QtGui.QTableWidgetItem(project.type))
        self.ui.tableWidget.setItem(1,0,QtGui.QTableWidgetItem(test.eut))
        self.ui.tableWidget.setItem(2,0,QtGui.QTableWidgetItem(test.serial_no))
        self.ui.tableWidget.setItem(3,0,QtGui.QTableWidgetItem(test.model_no))
        self.ui.tableWidget.setItem(4,0,QtGui.QTableWidgetItem(test.model_name))
        self.ui.tableWidget.setCellWidget(5,0,self.editEnvironment)
        self.ui.tableWidget.setRowHeight(5, 30 + _envRow * 30)
        self.ui.tableWidget.setItem(6,0,QtGui.QTableWidgetItem(test.company))
        self.ui.tableWidget.setItem(7,0,QtGui.QTableWidgetItem(test.lab))
        self.ui.tableWidget.setItem(8,0,QtGui.QTableWidgetItem(test.technician))
        self.ui.tableWidget.setItem(9,0,QtGui.QTableWidgetItem(test.procedure))
        self.ui.tableWidget.setItem(10,0,QtGui.QTableWidgetItem(test.setup))
        self.ui.tableWidget.setItem(11,0,QtGui.QTableWidgetItem(test.result))
        self.ui.tableWidget.setItem(12,0,QtGui.QTableWidgetItem(test.tempest_z_no))
        self.ui.tableWidget.setItem(13,0,QtGui.QTableWidgetItem(test.date_time))
        self.ui.tableWidget.setItem(14,0,QtGui.QTableWidgetItem(test.label_no))
        self.editComment.setPlainText(test.comment)
        self.ui.tableWidget.setCellWidget(15,0,self.editComment)

        self.ui.tableWidget.setRowHeight(15,94)

        if test.type_of_user == 1: self.ui.RBtnUser1.setChecked(True)
        if test.type_of_user == 2: self.ui.RBtnUser2.setChecked(True)
        if test.type_of_user == 3: self.ui.RBtnUser3.setChecked(True)
        if test.type_of_user == 4: self.ui.RBtnUser4.setChecked(True)
        if test.type_of_test == 1: self.ui.RBtnTT1.setChecked(True)
        if test.type_of_test == 2: self.ui.RBtnTT2.setChecked(True)
        if test.type_of_eut == 1: self.ui.RBtnTE1.setChecked(True)
        if test.type_of_eut == 2: self.ui.RBtnTE2.setChecked(True)
        if test.type_of_eut == 3: self.ui.RBtnTE3.setChecked(True)
        if test.type_of_eut == 4: self.ui.RBtnTE4.setChecked(True)
        if test.type_of_eut == 5: self.ui.RBtnTE5.setChecked(True)
        if test.type_of_eut == 6: self.ui.RBtnTE6.setChecked(True)
        if test.type_of_eut == 7: self.ui.RBtnTE7.setChecked(True)
        if test.type_of_eut == 8: self.ui.RBtnTE8.setChecked(True)


        self.ui.BtnOk.clicked.connect(self.onBtnOk)
        self.ui.BtnCancel.clicked.connect(self.onBtnCancel)
        self.ui.BtnAddEnvironment.clicked.connect(self.onBtnAddEnvironment)
        self.ui.BtnDelEnvironment.clicked.connect(self.onBtnDelEnvironment)
        self.ui.BtnGenDocument.clicked.connect(self.onBtnGenDocument)
        table = QtGui.QTableWidget(2,2)

        tableItem = QtGui.QLineEdit()
        tableItem.setText( "Testing" )
        table.setCellWidget(0, 0, tableItem )

        comboBox = QtGui.QComboBox()
        table.setCellWidget(1,1, comboBox)

        table.show()

        self.show()
    def generate_page(self,testNo):
        _pdfFile = 'Report ' + testNo + '.pdf'
        self.canvas = canvas.Canvas(_pdfFile,pagesize=portrait(A4))
        #width, height = A4
        _line = 0
    # header Text
        self.canvas.translate(mm,mm)
        self.canvas.setFont('Helvetica',32,leading=None)
        self.canvas.drawString(self.leftMargin*mm,260*mm,"Report")
        self.canvas.setFont('Helvetica',24,leading=None)
        self.canvas.drawRightString(190*mm,260*mm,"BS-EAY0A")
        self.canvas.line(self.leftMargin*mm,255*mm,190*mm,255*mm)

        self.canvas.setFont('Helvetica', 12, leading=None)
        self.setTextLine("EUT:", _line)
        self.setTextLine(self.currentTest.eut, _line, self.leftOffset2)
        _line += 1
        self.setTextLine("Serial-No.:", _line)
        self.setTextLine(self.currentTest.serial_no, _line, self.leftOffset2)
        _line += 1
        self.setTextLine("Model-No.:", _line)
        self.setTextLine(self.currentTest.model_no, _line, self.leftOffset2)
        _line += 1
        self.setTextLine("Model-Name.:", _line)
        self.setTextLine(self.currentTest.model_name, _line, self.leftOffset2)
        _line += 1

        self.setTextLine("EUT Environment:", _line)
        _line += 1

        _enList = self.currentTest.environment.split(',')
        for x in range (0,len(_enList)-1,2):
                self.setTextLine(_enList[x],_line, self.leftOffset1)
                self.setTextLine(_enList[x+1],_line, self.leftOffset2)
                _line += 1

        self.setTextLine("Company:", _line)
        self.setTextLine(self.currentTest.company, _line, self.leftOffset2)
        _line += 1
        self.setTextLine("Group:", _line)
        self.setTextLine(self.currentTest.lab, _line, self.leftOffset2)
        _line += 1
        self.setTextLine("Technician:", _line)
        self.setTextLine(self.currentTest.technician, _line, self.leftOffset2)
        _line += 1
        self.setTextLine("Test Procedure:", _line)
        self.setTextLine(self.currentTest.procedure, _line, self.leftOffset2)
        _line += 1
        self.setTextLine("Test Setup:", _line)
        self.setTextLine(self.currentTest.setup, _line, self.leftOffset2)
        _line += 1
        self.setTextLine("Test Result:", _line)
        self.setTextLine(self.currentTest.result, _line, self.leftOffset2)
        _line += 1
        self.setTextLine("TEMPEST Z-No.:", _line)
        self.setTextLine(self.currentTest.tempest_z_no, _line, self.leftOffset2)
        _line += 1
        self.setTextLine("Date:", _line)
        self.setTextLine(self.currentTest.date_time, _line, self.leftOffset2)
        _line += 1
        self.setTextLine("Label-No.:", _line)
        self.setTextLine(self.currentTest.label_no, _line, self.leftOffset2)
        _line += 1
        self.setTextLine("Comment:", _line)
        self.setTextLine(self.currentTest.comment, _line, self.leftOffset2)
        _line += 1

        self.canvas.setFont('Helvetica',12,leading=None)
        self.canvas.drawRightString(190*mm,16*mm,"2015.11.12 16:30")
        self.canvas.line(self.leftMargin*mm,15*mm,190*mm,15*mm)
        self.canvas.showPage()
        self.canvas.save()
        try:
            os.startfile(_pdfFile)
        except AttributeError:
            subprocess.call(['open', _pdfFile])
    def setTextLine(self,text,line,offset=0):
        r = self.leftMargin*mm + offset*mm
        s = 240*mm - line*7*mm
        self.canvas.drawString(r,s,text)
    
    def onBtnGenDocument(self):
        self.saveToDB()
        self.generate_page(self.currentTest.test_no)

    def onBtnAddEnvironment(self):
        self.editEnvironment.setRowCount(self.editEnvironment.rowCount()+1)
        self.ui.tableWidget.setRowHeight(5,self.ui.tableWidget.rowHeight(5)+30)
    def onBtnDelEnvironment(self):
        _rows=[]
  #      for idx in self.editEnvironment.selectedIndexes():
  #          _rows.append(idx.row())
      #  _rows.append(self.editEnvironment.selectedIndexes())
        _rows = self.editEnvironment.selectionModel().selectedRows()
        while len(_rows) > 0:
            self.editEnvironment.removeRow(_rows[0].row())
            self.ui.tableWidget.setRowHeight(5,self.ui.tableWidget.rowHeight(5)-30)
            _rows = self.editEnvironment.selectionModel().selectedRows()

    def onBtnOk(self):
        self.ret = True
        self.saveToDB()
        self.close()

    def onBtnCancel(self):
        self.ret = False
        self.close()

    def saveToDB(self):
        if self.currentProject is not None:
            self.currentProject.title = self.ui.tableWidget.item(0,0).text()
            self.currentProject.type = self.ui.tableWidget.item(9,0).text()
        self.currentTest.eut = self.ui.tableWidget.item(1,0).text()
        self.currentTest.serial_no = self.ui.tableWidget.item(2,0).text()
        self.currentTest.model_no = self.ui.tableWidget.item(3,0).text()
        self.currentTest.model_name = self.ui.tableWidget.item(4,0).text()
        _enStr = ''
        _rows = self.editEnvironment.rowCount()
        for _row in range(0,_rows):
            _x = self.editEnvironment.item(_row, 0).text()
            _x.replace(',','') #commas not allowed
            _enStr += _x
            _enStr += ','
            _y = self.editEnvironment.item(_row, 1).text()
            _y.replace(',','')
            _enStr += _y
            _enStr += ','

        self.currentTest.environment = _enStr.rstrip(',')
        self.currentTest.company = self.ui.tableWidget.item(6,0).text()
        self.currentTest.group = self.ui.tableWidget.item(7,0).text()
        self.currentTest.technician = self.ui.tableWidget.item(8,0).text()
        self.currentTest.procedure = self.ui.tableWidget.item(9,0).text()
        self.currentTest.setup = self.ui.tableWidget.item(10,0).text()
        self.currentTest.result = self.ui.tableWidget.item(11,0).text()
        self.currentTest.tempest_z_no = self.ui.tableWidget.item(12,0).text()
        self.currentTest.date_time = self.ui.tableWidget.item(13,0).text()
        self.currentTest.label_no = self.ui.tableWidget.item(14,0).text()
        self.currentTest.comment = self.editComment.toPlainText()

        if self.ui.RBtnUser1.isChecked(): self.currentTest.type_of_user = 1
        if self.ui.RBtnUser2.isChecked(): self.currentTest.type_of_user = 2
        if self.ui.RBtnUser3.isChecked(): self.currentTest.type_of_user = 3
        if self.ui.RBtnUser4.isChecked(): self.currentTest.type_of_user = 4
        if self.ui.RBtnTT1.isChecked(): self.currentTest.type_of_test = 1
        if self.ui.RBtnTT2.isChecked(): self.currentTest.type_of_test = 2
        if self.ui.RBtnTE1.isChecked(): self.currentTest.type_of_eut = 1
        if self.ui.RBtnTE2.isChecked(): self.currentTest.type_of_eut = 2
        if self.ui.RBtnTE3.isChecked(): self.currentTest.type_of_eut = 3
        if self.ui.RBtnTE4.isChecked(): self.currentTest.type_of_eut = 4
        if self.ui.RBtnTE5.isChecked(): self.currentTest.type_of_eut = 5
        if self.ui.RBtnTE6.isChecked(): self.currentTest.type_of_eut = 6
        if self.ui.RBtnTE7.isChecked(): self.currentTest.type_of_eut = 7
        if self.ui.RBtnTE8.isChecked(): self.currentTest.type_of_eut = 8


    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))