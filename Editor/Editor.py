# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:42:08 2013

@author: HS
"""

from DB_Handler_TDS3 import *
from pydispatch import dispatcher
from NeedfullThings import *

PLAN_TYPE, PLOT_TYPE, ROUTINE_TYPE, LIMIT_TYPE, SETTING_TYPE, TRACE_TYPE, ROUTE_TYPE = range(1001, 1008)
class MainForm(QtGui.QMainWindow):


    def __init__(self,parent=None):
        QtGui.QMainWindow.__init__(self)

        self.ui = uic.loadUi("EditorMain.ui", self)

        self.ui.stackedWidget.setCurrentIndex(0)

#        self.ui.treeWidget.addItem(1004)
        self.ui.BtnOk.clicked.connect(self.onBtnOk)

        self.ui.BtnAddPlot.clicked.connect(self.onBtnAddPlot)
        self.ui.BtnAddRoutine.clicked.connect(self.onBtnAddRoutine)
        self.ui.BtnAddLimit.clicked.connect(self.onBtnAddLimit)
        self.ui.BtnAddSetting.clicked.connect(self.onBtnAddSetting)
        self.ui.BtnAddRoute.clicked.connect(self.onBtnAddRoute)
        self.ui.BtnAddTrace.clicked.connect(self.onBtnAddTrace)
        self.ui.BtnDel.clicked.connect(self.onBtnDel)
        self.ui.BtnAddItem1.clicked.connect(self.onBtnAddDeviceRt)
        self.ui.BtnAddItem2.clicked.connect(self.onBtnAddLimitRt)
        self.ui.BtnAddItem3.clicked.connect(self.onBtnAddLineRt)
        self.ui.BtnDelItem.clicked.connect(self.onBtnDelItemRt)
        self.ui.BtnExpandAll.clicked.connect(self.onBtnExpandAll)
        self.ui.BtnCollapseAll.clicked.connect(self.onBtnCollapseAll)
        self.ui.treeWidget.itemSelectionChanged.connect(self.onSelectionChanged)
        self.ui.treeWidget.copied.connect(self.onCopied)
        self.ui.treeWidget.itemDoubleClicked.connect(self.onItemDClicked)
        self.id = 1
        self.disableBtns()
        self.dataSetFileName = ''
        self.signals = Signal()
        self.openTDS3()
    def openTDS3(self):

        dlg=QtGui.QFileDialog( self )
        dlg.setWindowTitle( 'open or create DataSet' )
        dlg.setViewMode( QtGui.QFileDialog.Detail )
        dlg.setNameFilters( [self.tr('DataSet (*.TDS3)')] )
        dlg.setDefaultSuffix( 'TDS3' )
        dlg.setDirectory('.')
        if dlg.exec_() :
            _fname = dlg.selectedFiles()
            print (_fname)
            if _fname == '':
                return
            if QtCore.QFile.exists(_fname[0]):
                self.onLoadTDS(_fname[0])
            else:
                print('new TDS', _fname)
    def setEditPage(self,type,id):
        if type == PLAN_TYPE:
            self.ui.stackedWidget.setCurrentIndex(0)
            par1 = self.dataSetFileName
            par2 = id
            dispatcher.send(self.signals.EDIT_PLANID,dispatcher.Anonymous,par1,par2)
            self.ui.BtnAddItem1.setEnabled(False)
            self.ui.BtnAddItem2.setEnabled(False)
            self.ui.BtnAddItem3.setEnabled(False)
            self.ui.BtnDelItem.setEnabled(False)

        elif type == PLOT_TYPE:
            self.ui.lbEditor.setText('Plot')
            self.ui.stackedWidget.setCurrentIndex(1)
            par1 = self.dataSetFileName
            par2 = id
            dispatcher.send(self.signals.EDIT_PLOTID,dispatcher.Anonymous, par1, par2)
            self.ui.BtnAddItem1.setEnabled(False)
            self.ui.BtnAddItem2.setEnabled(False)
            self.ui.BtnAddItem3.setEnabled(False)
            self.ui.BtnAddItem4.setEnabled(False)
            self.ui.BtnDelItem.setEnabled(False)
        elif type == ROUTINE_TYPE:
            self.ui.stackedWidget.setCurrentIndex(2)
            self.ui.lbEditor.setText('Routine')
            par1 = self.dataSetFileName
            par2 = id
            print('start Routine')
            self.ui.BtnAddItem1.setEnabled(True)
            self.ui.BtnAddItem2.setEnabled(True)
            self.ui.BtnAddItem3.setEnabled(True)
            self.ui.BtnAddItem4.setEnabled(False)
            self.ui.BtnDelItem.setEnabled(True)
            dispatcher.send(self.signals.EDIT_ROUTINEID,dispatcher.Anonymous, par1, par2)
        elif type == SETTING_TYPE:
            self.ui.stackedWidget.setCurrentIndex(3)
            self.ui.lbEditor.setText('Setting')
            par1 = self.dataSetFileName
            par2 = id
            print('start Setting')
            self.ui.BtnAddItem1.setEnabled(True)
            self.ui.BtnAddItem2.setEnabled(True)
            self.ui.BtnAddItem3.setEnabled(True)
            self.ui.BtnAddItem4.setEnabled(False)
            self.ui.BtnDelItem.setEnabled(True)
            dispatcher.send(self.signals.EDIT_SETTINGID,dispatcher.Anonymous, par1, par2)
    def onBtnAddDeviceRt(self):
        dispatcher.send(self.signals.EDIT_ADD_DEVICE,dispatcher.Anonymous)
        pass
    def onBtnAddLimitRt(self):
        dispatcher.send(self.signals.EDIT_ADD_LIMIT,dispatcher.Anonymous)
        pass
    def onBtnAddLineRt(self):
        dispatcher.send(self.signals.EDIT_ADD_LINE,dispatcher.Anonymous)
        pass
    def onBtnAddInstructionRt(self):
        dispatcher.send(self.signals.EDIT_ADD_I,dispatcher.Anonymous)
        pass
    def onBtnDelItemRt(self):
        dispatcher.send(self.signals.EDIT_DEL_ITEM,dispatcher.Anonymous)

    def onBtnAddRoute(self):
        pass
    def onBtnDelItem(self):
        pass
    def onBtnExpandAll(self):
        self.ui.treeWidget.expandAll()
        pass
    def onBtnCollapseAll(self):
        self.ui.treeWidget.collapseAll()
        pass
    def onLoadTDS(self, fileName):
        self.dataSetFileName = fileName
        #-loads ActiveTestPlan to TreeView

        self.ds = Dataset(fileName)
        if self.ds.read():
            self.initTreeView()
        #self.ui.setCursor(QtCore.Qt.ArrowCursor)

    def initTreeView(self):

        _parentPlan = self.ui.treeWidget.invisibleRootItem()
        _text ='Plan ' + self.ds.db.title
        _parentPlot = self.ui.treeWidget.addItem(_parentPlan,PLAN_TYPE,self.ds.db.title,0)

        for _member_plot in self.ds.db.plot_list:
            assert isinstance(_member_plot,DatasetPlot)
            _parentRoutine = self.ui.treeWidget.addItem(_parentPlot,PLOT_TYPE,_member_plot.title,_member_plot.id_plot)

            for _member_routine in _member_plot.routine_list:
                assert isinstance(_member_routine, DatasetRoutine)
                _parentSetting = self.ui.treeWidget.addItem(_parentRoutine,ROUTINE_TYPE,_member_routine.title,_member_routine.id_routine)

                if not (_member_routine.limits == None):
                    _limitLines = eval (_member_routine.limits)
                    for _member_line in _limitLines:
                        self.ui.treeWidget.addItem(_parentSetting, LIMIT_TYPE, _member_line[0],0)
                    if _member_routine.lines != None:
                        _lines = eval (_member_routine.lines)
                        for _member_line in _lines:
                            self.ui.treeWidget.addItem(_parentSetting, LIMIT_TYPE, _member_line[0])
                    for _member_setting in _member_routine.setting_list:
                        _parentTrace = self.ui.treeWidget.addItem(_parentSetting,SETTING_TYPE,_member_setting.title,_member_setting.id_setting)
                        if _member_setting.route != None:
                            self.ui.treeWidget.addItem(_parentTrace,ROUTE_TYPE,_member_setting.route,0)
                        for _member_trace in _member_setting.trace_list:
                            self.ui.treeWidget.addItem(_parentTrace,TRACE_TYPE,_member_trace.title,_member_trace.id_trace)

        self.onBtnCollapseAll()

    def onItemDClicked(self,item):
        _type = item.type
        _title = item.title
        _id = item.id
      ##  print('dclicked',_type,_title,_id)
        self.setEditPage(_type,_id)
        pass

    def onCopied(self):
        #   print("copiert")
        pass
    def onBtnOk(self):
        self.close()

    def disableBtns(self):
        self.ui.BtnAddPlot.setEnabled(False)
        self.ui.BtnAddRoutine.setEnabled(False)
        self.ui.BtnAddLimit.setEnabled(False)
        self.ui.BtnAddSetting.setEnabled(False)
        self.ui.BtnAddRoute.setEnabled(False)
        self.ui.BtnAddTrace.setEnabled(False)

    def onSelectionChanged(self):
        self.disableBtns()

        _inx = self.ui.treeWidget.selectedIndexes()
        if len(_inx) > 0:
          #  print(_inx[0])
            _type = self.ui.treeWidget.itemFromIndex(_inx[0]).type
            if _type == PLAN_TYPE:
                self.ui.BtnAddPlot.setEnabled(True)
                self.ui.treeWidget.setFlags(None)
            if _type == PLOT_TYPE:
                self.ui.BtnAddRoutine.setEnabled(True)
                self.ui.treeWidget.setFlags(PLAN_TYPE)
            if _type == ROUTINE_TYPE:
                self.ui.BtnAddLimit.setEnabled(True)
                self.ui.BtnAddSetting.setEnabled(True)
                self.ui.treeWidget.setFlags(PLOT_TYPE)
            if _type == SETTING_TYPE:
                self.ui.BtnAddRoute.setEnabled(True)
                self.ui.BtnAddTrace.setEnabled(True)
                self.ui.treeWidget.setFlags(ROUTINE_TYPE)
            if _type == TRACE_TYPE:
                self.ui.treeWidget.setFlags(SETTING_TYPE)
            if _type == LIMIT_TYPE:
                self.ui.treeWidget.setFlags(ROUTINE_TYPE)

            pass
    def onItemChanged(self):
        pass

    def onBtnAddPlot(self):
        _inx = self.ui.treeWidget.selectedIndexes()
        if len(_inx) > 0:
            _parent = self.ui.treeWidget.itemFromIndex(_inx[0])
            self.ui.treeWidget.addItem(_parent,PLOT_TYPE,self.id)
            self.id += 1
        pass
    def onBtnAddRoutine(self):
        _inx = self.ui.treeWidget.selectedIndexes()
        _parent = self.ui.treeWidget.itemFromIndex(_inx[0])
        self.ui.treeWidget.addItem(_parent,ROUTINE_TYPE, self.id)
        self.id += 1
        pass

    def onBtnAddSetting(self):
        _inx = self.ui.treeWidget.selectedIndexes()
        if len(_inx) > 0:
            _parent = self.ui.treeWidget.itemFromIndex(_inx[0])
            self.ui.treeWidget.addItem(_parent,SETTING_TYPE, self.id)
            self.id +=1

    def onBtnAddTrace(self):
        _inx = self.ui.treeWidget.selectedIndexes()
        _parent = self.ui.treeWidget.itemFromIndex(_inx[0])
        self.ui.treeWidget.addItem(_parent,TRACE_TYPE, self.id)
        self.id += 1
        pass

    def onBtnAddLimit(self):
        _inx = self.ui.treeWidget.selectedIndexes()
        _parent = self.ui.treeWidget.itemFromIndex(_inx[0])
        self.ui.treeWidget.addItem(_parent,LIMIT_TYPE, self.id )
        self.id += 1

        pass
    def onBtnAddRoute(self):
        _inx = self.ui.treeWidget.selectedIndexes()
        _parent = self.ui.treeWidget.itemFromIndex(_inx[0])
        self.ui.treeWidget.addItem(_parent,ROUTE_TYPE, self.id)
        self.id += 1
        pass
    def onBtnDel(self):
        _inx = self.ui.treeWidget.selectedIndexes()
        if len(_inx) > 0:
            _item = self.ui.treeWidget.itemFromIndex(_inx[0])
            _c =  _item.childCount()
            msgBox =  QtGui.QMessageBox()
            msgBox.setText('the selected item is head of a branch\nIf you delete this item, all subitems will be deleted too!')
            msgBox.setInformativeText('proceed anyway ?')
            msgBox.setStandardButtons(QtGui.QMessageBox.No|QtGui.QMessageBox.Yes)
            msgBox.setDefaultButton(QtGui.QMessageBox.No)
            _ret = msgBox.exec_()
            if _ret == QtGui.QMessageBox.Yes:
                 self.ui.treeWidget.delItem(_item)
        pass

def main():
    app = QtGui.QApplication(sys.argv)

    sshFile = "../Templates/darkorange.css"
    with open (sshFile,"r") as fh:
        app.setStyleSheet(fh.read())
    form = MainForm()
    form.show()
    app.exec_()




if __name__ == '__main__':
    import sys
    main()



