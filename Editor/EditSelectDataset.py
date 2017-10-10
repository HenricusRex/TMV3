from EditTools import *
from NeedfullThings import *
import configparser
import DB_Handler_TPL3
import DB_Handler_TDS3


class SelectWBDS(QtGui.QDialog):
    def __init__(self, parent=None):
        super(SelectWBDS,self).__init__(parent)
        self.parent = parent
        self.ui = uic.loadUi("../Editor/EditSelectDataset.ui", self)
        self.ret = None

        self.viewTableModel= None
        self.viewTableModel = TableModel(['Id','Title','Version','Date','Used'])
        self.viewTableModel.beginResetModel()
        self.viewTableModel.removeRows(0, self.viewTableModel.rowCount())
        self.config = configparser.ConfigParser()
        self.config.read('../Lib/TMV3.ini')
        workBenchDB = self.config['DataBases']['workbench']

        ds = DB_Handler_TPL3.Tpl3Files(workBenchDB,0)
        idList = ds.findTestplan()
        for id in idList:
            ds = DB_Handler_TPL3.Tpl3Files(workBenchDB, id)
            ds.read()
            refcount = ds.findTestplanReference()
            dataList =[]
            dataList.append(ds.file_id)
            dataList.append(ds.title)
            dataList.append(ds.version)
            dataList.append(ds.date)
            dataList.append(refcount)
            self.viewTableModel.addData(dataList)

        self.ui.tableView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.viewTableModel.endResetModel()
        self.ui.tableView.setModel(self.viewTableModel)
        self.ui.tableView.resizeColumnsToContents()
        self.ui.tableView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ui.tableView.horizontalHeader().hideSection(0)
        self.ui.tableView.doubleClicked.connect(self.onDoubleClick)

        self.BtnOk.clicked.connect(self.onBtnOk)
        self.BtnCancel.clicked.connect(self.onBtnCancel)

    def onDoubleClick(self):
        self.onBtnOk()

    def onBtnOk(self):
        _row = self.ui.tableView.selectedIndexes()[0].row()
        idx = self.ui.tableView.model().index(_row, 0)
        id = self.viewTableModel.data(idx, Qt.DisplayRole)
        self.ret = id
        self.accept()
        pass

    def onBtnCancel(self):
        self.ret = None
        self.close()
        return (False)
        pass

