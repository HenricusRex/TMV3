import sys
from NeedfullThings import *
from DB_Handler_TDS3 import DatasetCommand
import EngFormat

class EditYesNo(QtGui.QDialog):
    def __init__(self, pos, parent=None):
        super(EditYesNo,self).__init__(parent)
        self.ret = 'No'
    #   self.ui = uic.loadUi("../Editor/EditYesNo.ui", self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.move(pos)
        self.setFixedHeight(80)
        layout = QtGui.QVBoxLayout(self)
        self.rbYes = QtGui.QRadioButton(self)
        self.rbYes.setText('Yes')
        self.rbNo = QtGui.QRadioButton(self)
        self.rbNo.setText('No')
        layout.addWidget(self.rbYes)
        layout.addWidget(self.rbNo)
        #
      #  self.lEdit.setText(value)
        self.move(pos)
        self.ret = 'No'
        self.rbYes.clicked.connect(self.onYes)
        self.rbNo.clicked.connect(self.onNo)

    #   self.ui.rBno.clicked.connect(self.onNo)
      # #  self.setModal(True)

    def onYes(self):
        self.ret = 'Yes'
        self.close()
    def onNo(self):
        self.ret = 'No'
        self.close()
    @staticmethod
    def getYesNo(pos, parent = None):
        dialog = EditYesNo(pos,parent)
        result = dialog.exec_()
        ret = dialog.ret
        return (ret)

class EditLine(QtGui.QDialog):
    def __init__(self, pos, value, parent=None):
        super(EditLine,self).__init__(parent)
      #  print ('EditLine')
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setFixedHeight(80)
        self.ret = ''

        layout = QtGui.QVBoxLayout(self)
        layoutH = QtGui.QHBoxLayout()
        self.lEdit = QtGui.QLineEdit(self)
        self.lEdit.setText(value)

        self.okBtn = QtGui.QPushButton('Ok')
        self.clBtn = QtGui.QPushButton('cancel')

        layout.addWidget(self.lEdit)
        layout.addLayout(layoutH)
        layoutH.addWidget(self.clBtn)
        layoutH.addWidget(self.okBtn)

        self.okBtn.clicked.connect(self.onBtnOk)
        self.clBtn.clicked.connect(self.onBtnCancel)


    def onBtnOk(self):
        self.ret = self.lEdit.text()
        self.close()
        pass

    def onBtnCancel(self):
        self.ret = None
        self.close()
        pass

    @staticmethod
    def getLine(pos, value, parent = None):
        dialog = EditLine(pos,value,parent)
        result = dialog.exec_()
        return(dialog.ret)

class EditSpin(QtGui.QDialog):
    def __init__(self, pos, value, parent=None):
        super(EditSpin,self).__init__(parent)
        self.setFixedHeight(80)
        self.ret = 0

        layout = QtGui.QVBoxLayout(self)
        layoutH = QtGui.QHBoxLayout()
        self.sBox = QtGui.QDoubleSpinBox(self)
        self.sBox.setValue(value)
        self.sBox.setMaximum(40e9)
        self.sBox.setMinimum(0)

        self.okBtn = QtGui.QPushButton('Ok')
        self.clBtn = QtGui.QPushButton('cancel')

        layout.addWidget(self.sBox)
        layout.addLayout(layoutH)
        layoutH.addWidget(self.clBtn)
        layoutH.addWidget(self.okBtn)

        self.okBtn.clicked.connect(self.onBtnOk)
        self.clBtn.clicked.connect(self.onBtnCancel)


    def onBtnOk(self):
        self.ret = self.sBox.value()
        self.close()
        pass

    def onBtnCancel(self):
        self.ret = None
        self.close()
        pass

    @staticmethod
    def getValue(pos, value, parent = None):
        dialog = EditSpin(pos,value,parent)
        result = dialog.exec_()
        return(dialog.ret)

class EditPlain(QtGui.QDialog):
    def __init__(self, pos,text, parent=None):
        super(EditPlain,self).__init__(parent)
        self.ui = uic.loadUi("../Editor/EditPlain.ui", self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.move(pos)
        self.text = text
        self.ui.plainTextEdit.setPlainText(text)
        self.ret = ''
        self.ui.BtnCancel.clicked.connect(self.onBtnCancel)
        self.ui.BtnOk.clicked.connect(self.onBtnOk)

    def onBtnCancel(self):
        self.ret = self.text
        self.close()

    def onBtnOk(self):
        self.ret = self.ui.plainTextEdit.toPlainText()
        self.close()
    @staticmethod
    def getText(pos,text, parent = None):
        dialog = EditPlain(pos,text,parent)
        result = dialog.exec_()
        ret = dialog.ret
        return (ret)

class EditDate(QtGui.QDialog):
    def __init__(self,pos,text, parent = None):
        super(EditDate,self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setFixedHeight(80)
        self.setFixedWidth(160)
        self.move(pos)
        self.retChoose = text
        self.okBtn = QtGui.QPushButton('Ok')
        self.clBtn = QtGui.QPushButton('cancel')

        layout = QtGui.QVBoxLayout(self)
        layoutH = QtGui.QHBoxLayout()
        self.datetime = QtGui.QDateTimeEdit(self)
        self.datetime.setCalendarPopup(True)
        self.datetime.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(self.datetime)
        layout.addLayout(layoutH)
        layoutH.addWidget(self.clBtn)
        layoutH.addWidget(self.okBtn)

        self.okBtn.clicked.connect(self.onBtnOk)
        self.clBtn.clicked.connect(self.onBtnCancel)


    def onBtnOk(self):
        date = self.datetime.dateTime()
        self.retChoose = date.toString('yyyy-MM-dd HH:mm:ss')
        self.close()
        pass
    def onBtnCancel(self):
        self.close()
        pass

    @staticmethod
    def getDate(pos,text, parent = None):
        dialog = EditDate(pos,text,parent)
        result = dialog.exec_()
        ret = dialog.retChoose
        return (ret)

class EditSelection(QtGui.QDialog):
    def __init__(self, pos, selection, parent=None):
        super(EditSelection,self).__init__(parent)
     #   print("EditSelection",parent )
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint )
        if not pos == None:
            self.move(pos)
        self.setFixedHeight(80)
        self.setFixedWidth(80)
        self.ret = None

        layout = QtGui.QVBoxLayout(self)
        layoutH = QtGui.QHBoxLayout()
        self.lWid = QtGui.QListWidget(self)
        self.okBtn = QtGui.QPushButton('Ok')
        self.clBtn = QtGui.QPushButton('cancel')

        length = 0
        for i in selection:
            self.lWid.addItem(i)
            if len(i)> length: length = len(i)

        height = len(selection)*20 + 60
        if height < 80:
            height = 80
        self.setFixedHeight(height)

        length = length*6 + 50
        if length < 100:
            length = 100
        self.setFixedWidth(length)

        layout.addWidget(self.lWid)
        layout.addLayout(layoutH)
        layoutH.addWidget(self.clBtn)
        layoutH.addWidget(self.okBtn)

        self.lWid.itemClicked.connect(self.onSelectionChanged)

        self.okBtn.clicked.connect(self.onBtnOk)
        self.clBtn.clicked.connect(self.onBtnCancel)


    def onBtnOk(self):
        self.ret = self.lWid.currentItem().text()
        self.close()
        pass

    def onBtnCancel(self):
        self.ret = None
        self.close()
        pass

    def onSelectionChanged(self):
        self.ret = self.lWid.currentItem().text()
        self.close()
 #       self.accept()

    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))


    def accept(self):
        super(EditSelection,self).accept()

    @staticmethod
    def getSelection(pos, selection, parent = None):
        dialog = EditSelection(pos,selection,parent)
        result = dialog.exec_()
        ret = dialog.ret
        return (ret)

class EditMultiSelection(QtGui.QDialog):
    def __init__(self, pos, selection, parent=None):
        super(EditMultiSelection,self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        height = len(selection)*20 + 40
        if height < 80:
            height = 80
        self.setFixedHeight(height)

        self.move(pos)
        self.retChoose = ''

        layout = QtGui.QVBoxLayout(self)
        layoutH = QtGui.QHBoxLayout()
        self.lWid = QtGui.QListWidget(self)
        self.lWid.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        length = 0
        for i in selection:
            self.lWid.addItem(i)
            if len(i)> length: length = len(i)
        length = length*6 + 50
        if length < 100:
            length = 100
        self.setFixedWidth(length)

        self.okBtn = QtGui.QPushButton('Ok')
        self.clBtn = QtGui.QPushButton('cancel')

        layout.addWidget(self.lWid)
        layout.addLayout(layoutH)
        layoutH.addWidget(self.clBtn)
        layoutH.addWidget(self.okBtn)

        self.okBtn.clicked.connect(self.onBtnOk)
        self.clBtn.clicked.connect(self.onBtnCancel)

        self.setModal(True)
    def onBtnOk(self):
        self.retChoose = []
        for i in self.lWid.selectedItems():
            self.retChoose.append(i.text())
        self.close()
        pass
    def onBtnCancel(self):
        self.retChoose = None
        self.close()
        pass

    @staticmethod
    def getMultiSelection(pos, selection, parent = None):
        dialog = EditMultiSelection(pos,selection,parent)
        result = dialog.exec_()
        ret = dialog.retChoose
        return (ret)

class EditCom():
    def __init__(self,command,driver=""):
        #format = S0: x
        #         S3: x.xxx
        #         Sx: free text
        #         L: List
        self.dsCom = command
        self.driver = driver
        self.format = ''
        self.dim = ''
        self.list = []
        self.editor = ''
        if driver != "":
            self.getFormat(self.dsCom.command,driver)

    def formatParamToEngString(self,*par):
        dS = str(par[0])
        if self.format == 'L':
            try:
                dF = float(dS)
            except:
                return dS
            formatter = EngFormat.Format()
            dS = formatter.FloatToString(dF,0)


        elif self.format == 'S0':
            formatter = EngFormat.Format()
            dF = formatter.StringToFloat(dS)
            dS = formatter.FloatToString(dF,0,self.dim)

        elif self.format == 'S3':
            formatter = EngFormat.Format()
            dF = formatter.StringToFloat(dS)
            dS = formatter.FloatToString(dF,3,self.dim)
            pass

        elif self.format == 'SX':
            pass
        return (dS)

    def formatParamToString(self,*par):
        if self.format == 'L':
            return
        dS = str(par[0])
        formatter = EngFormat.Format()
        dF = formatter.StringToFloat(dS)
        dS = str(dF)
        return(dS)

    def getFormat(self,func,driver):
      #  print (func,driver)
        module = __import__(driver)
        class_ = getattr(module, driver)
        dDriv = class_()
        func = getattr(dDriv, func)
        annotations = func.__annotations__
        form = annotations['par']
        if type(form) == list:
            self.format = 'L'
            self.list = form
        else:
            self.format = form[:2]
            self.dim = form[2:]
   #     print(self.format,self.dim)

    def getTableEntry(self):
        sPar = self.formatParamToEngString(self.dsCom.parameter)
        sRet = self.dsCom.command + " (" + self.getParam() + ")\n"
        return sRet

    def getParam(self):
        sPar = self.formatParamToEngString(self.dsCom.parameter)
        return sPar

    def edit(self):
        if self.format == 'L':
            ret = EditSelection.getSelection(None,self.list)
            if not ret is None:
                self.dsCom.parameter = self.formatParamToEngString(ret)
        else:
            ret = EditLine.getLine(None,self.formatParamToEngString(self.dsCom.parameter))
            if not ret is None:
                self.dsCom.parameter = self.formatParamToEngString(ret)

