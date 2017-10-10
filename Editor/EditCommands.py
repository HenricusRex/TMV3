from EditTools import *
from NeedfullThings import *
from EngFormat import Format
from DB_Handler_TDS3 import DatasetCommand



class EditCommands(QtGui.QDialog):
    def __init__(self, commands, dDriver, parent=None):

        super(EditCommands,self).__init__(parent)


        self.parent = parent
        self.ui = uic.loadUi("../Editor/EditCommands.ui", self)
        self.ret = None
        self.funcList = []

        self.viewTableModel= None
        self.viewTableModel = TableModel(['Command','Parameter','oCommand'])
        self.viewTableModel.beginResetModel()
        self.viewTableModel.removeRows(0, self.viewTableModel.rowCount())
        self.driverName = dDriver

        if len(commands)== 0:
            if not self.getCommandsToAdd(dDriver):
                return
            #generate new list of Commands
            for x in self.funcList:
                c = DatasetCommand("",0)
                c.command = x
                c.parameter = ""
                c.driver = dDriver
                ret = self.getFormat(x,dDriver)
                c.format = ret[0]
                c.pList = ret[1]
                c.dim = ret[2]
                self.viewTableModel.addData([c.command, "", c])
        else:
            for c  in commands:
              #  self.viewTableModel.addData([command.command, command.parameter])
                self.viewTableModel.addData([c.command, self.formatParamToEngString(c),c])
               # dDriver = c.driver

        self.ui.tableView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.viewTableModel.endResetModel()
        self.ui.tableView.setModel(self.viewTableModel)
        self.ui.tableView.resizeColumnsToContents()
        self.ui.tableView.doubleClicked.connect(self.onDoubleClick)
        self.ui.tableView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ui.tableView.horizontalHeader().hideSection(2)

        self.BtnOk.clicked.connect(self.onBtnOk)
        self.BtnCancel.clicked.connect(self.onBtnCancel)
        self.BtnUp.clicked.connect(self.onBtnUp)
        self.BtnDown.clicked.connect(self.onBtnDown)
        self.BtnAdd.clicked.connect(self.onBtnAdd)
        self.BtnDel.clicked.connect(self.onBtnDel)
       # self.setModal(True)
        self.getCommandsToAdd(dDriver)

    def getCommandsToAdd(self,dDriver):
        try:
            module = __import__(dDriver)
            class_ = getattr(module, dDriver)
            self.dDriv = class_()
            self.funcList = self.dDriv.editableCommands
        except Exception as _err:
            msgBox = QtGui.QMessageBox()
            msgBox.setText(str(_err) + '\nNot able to load function list.\n'
                           'Editable Commands defined in driver?')
            msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
            msgBox.exec_()
            return False
        return True


    def onDoubleClick(self,mi):
        self.ui.tableView.blockSignals(True)
        try:
            row = mi.row()
            col = mi.column()
  #          colName = self.viewTableModel.headerData(col, Qt.Horizontal, Qt.DisplayRole)
            idx = self.ui.tableView.model().index(row, 0)
            sCommand = self.viewTableModel.data(idx,Qt.DisplayRole)
            idx1 = self.ui.tableView.model().index(row, 1)
            sValue = self.viewTableModel.data(idx1,Qt.DisplayRole)
            idx2 = self.ui.tableView.model().index(row, 2)
            c = self.viewTableModel.data(idx2,Qt.DisplayRole)
            #ret = c.edit()
            if c.format == 'L':
                ret = EditSelection.getSelection(None, c.pList)
                if not ret is None:
                    c.parameter = ret
                    c.parameter = self.formatParamToEngString(c)
                    self.viewTableModel.setData(idx1,c.parameter)
                    self.viewTableModel.setData(idx2,c)
            else:
                ret = EditLine.getLine(None, self.formatParamToEngString(c))
                if not ret is None:
#                    idx = self.ui.tableView.model().index(row, 1)
                    c.parameter = ret
                    c.parameter = self.formatParamToEngString(c)
                    self.viewTableModel.setData(idx1,c.parameter)
                    self.viewTableModel.setData(idx2,c)

        except Exception as _err:
            print ('doubleClick',_err)
            pass

        self.ui.tableView.blockSignals(False)



    def onBtnOk(self):
        retString = ''
        order = 1
        retComList = []
        for row in range(self.viewTableModel.rowCount()):
            index = self.viewTableModel.index(row, 2)
            oCom = self.viewTableModel.data(index,Qt.DisplayRole)
            oCom.tableEntry = self.getTableEntry(oCom)
            oCom.order = order
            oCom.driver = self.driverName
            order += 1
            retComList.append(oCom)
            retString += oCom.tableEntry

        self.ret = (retString.rstrip('\n'),retComList)
        super(EditCommands, self).accept()
        #self.close()
        pass

    def onBtnCancel(self):
        self.ret = None
        self.close()
        pass

    def onBtnDown(self):
        self.swapTable('DOWN')
        pass

    def onBtnUp(self):
        self.swapTable('UP')
        pass

    def swapTable(self,dir):
        dataTable = []
        rowCount = self.viewTableModel.rowCount()
        colCcount = self.viewTableModel.columnCount()
        row = self.ui.tableView.selectedIndexes()[0].row()

        if ((dir == 'UP') and (row > 0)) or ((dir == 'DOWN') and (row < rowCount-1)):
            for n in range(rowCount):
                rowList = []
                for m in range(colCcount):
                    idx = self.viewTableModel.index(n,m)
                    rowList.append(self.viewTableModel.data(idx,Qt.DisplayRole))
                dataTable.append(rowList)

            if dir == 'UP':
                dataTable[row], dataTable[row-1] = dataTable[row-1],dataTable[row]
            else:
                dataTable[row], dataTable[row+1] = dataTable[row+1],dataTable[row]

            for n in reversed(range(rowCount)):
                self.viewTableModel.removeRow(n)

            for n in range(rowCount):
                self.viewTableModel.addData(dataTable[n])

            if dir =='UP':
                self.ui.tableView.selectRow(row-1)
            else:
                self.ui.tableView.selectRow(row+1)

    def onBtnDel(self):

        try:
            idx = self.ui.tableView.selectedIndexes()
            self.viewTableModel.removeRow(idx[0].row())
        except Exception as err:
            print (err)

    def onBtnAdd(self):
        cursor = QtGui.QCursor()
      #  pos = self.ui.treeWidget.mapFromGlobal(cursor.pos())
        ret = EditSelection.getSelection(None,self.funcList)
        if not ret == None:
            self.viewTableModel.addData([ret, ''])
        pass
        self.ui.tableView.resizeColumnsToContents()

    def errorMessage(self,err):
        msgBox = QtGui.QMessageBox()
        msgBox.setText('the selected item is head of a branch\nIf you delete this item, all subitems will be deleted too!')
        msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
        _ret = msgBox.exec_()

    def formatParamToEngString(self,c):
        dS = c.parameter
        if c.format == 'L':
            try:
                dF = float(dS)
            except:
                return dS
            formatter = EngFormat.Format()
            dS = formatter.FloatToString(dF,0)


        elif c.format == 'S0':
            formatter = EngFormat.Format()
            dF = formatter.StringToFloat(dS)
            dS = formatter.FloatToString(dF,0,c.dim)

        elif c.format == 'S3':
            formatter = EngFormat.Format()
            dF = formatter.StringToFloat(dS)
            dS = formatter.FloatToString(dF,3,c.dim)
            pass

        elif c.format == 'SX':
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
            return('L',form,0)
            self.format = 'L'
            self.list = form
        else:
            return (form[:2],[],form[2:])
            self.format = form[:2]
            self.dim = form[2:]
   #     print(self.format,self.dim)

    def getTableEntry(self,com):
        sPar = self.formatParamToEngString(com)
        sRet = com.command + " (" + sPar + ")\n"
        return sRet

    def getParam(self,com):
        sPar = self.formatParamToEngString(com.parameter)
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



    @staticmethod
    def editCommands(commands, driver,parent = None):
        dialog = EditCommands(commands,driver,parent)
        #result = dialog.show()
        dialog.exec_()
        ret = dialog.ret
     #   print(ret)
        return (ret)



