__author__ = 'heinz'


from PyQt4 import uic,QtGui
from PyQt4.QtCore import *
from pydispatch import dispatcher
from NeedfullThings import *
from DB_Handler_TPL3 import TPL3Test, TPL3TestInfo, Tpl3Files
import configparser
import TableView
import time




class TestDescription(QtGui.QDialog):


    def __init__(self,modeNew):
        #global model
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("TestDescription.ui", self)
        self.centerOnScreen()
        self._mode_new = modeNew
        self._time = time.localtime()
        self.signals = Signal()
        self._current_planID = -1
        self._current_testID = -1
        self._current_pos = 0
        self._max_tests = 0
        self._test = TPL3Test
        self._testInfo = TPL3TestInfo
        self._testNo = ''
        self._config = configparser.ConfigParser()
        self._wb_ok = True
        self._wb_error = False
        self._tm =TableModel(['ID', 'Title', 'Version','Date','Comment'])
        self.ui.tableView.setModel(self._tm)
        self._test_description_table = []


        self._config.read('TMV3.ini')
        self.ui.label_11.setText("Workbench: " + self._config['DataBases']['workbench'])
        self._current_testID = self._config['Current']['current_testID']
        self._current_planID = self._config['Current']['current_planID']


        #Buttons
       # self.ui.BtnLoadAndStart.clicked.connect(self.onBtnLoadAndStart)
        #self.ui.BtnLoadAndResume.clicked.connect(self.onBtnLoadAndResume)
        self.ui.BtnAddPlan.clicked.connect(self.onBtnAddPlan)
        self.ui.BtnDeletePlan.clicked.connect(self.onBtnDeletePlan)
        self.ui.BtnExportPlan.clicked.connect(self.onBtnExportPlan)
        self.ui.BtnCloneDescription.clicked.connect(self.onBtnCloneDescription)
        self.ui.BtnCancel.clicked.connect(self.onBtnCancel)
        self.ui.BtnOk.clicked.connect(self.onBtnOk)
        self.ui.BtnFwd.clicked.connect(self.onBtnFwd)
        self.ui.BtnFFwd.clicked.connect(self.onBtnFFwd)
        self.ui.BtnRwd.clicked.connect(self.onBtnRwd)
        self.ui.BtnFRwd.clicked.connect(self.onBtnFRwd)
        self.ui.BtnShowPlots.clicked.connect(self.onBtnShowPlots)
        self.ui.BtnActivatePlan.clicked.connect(self.onBtnActivatePlan)
        self.ui.BtnNewDescription.clicked.connect(self.onBtnNewDescription)
        self.ui.BtnSaveDescription.clicked.connect(self.onBtnSaveDescription)

        dispatcher.connect(self.onWB_Plan, signal=self.signals.WB_PLAN, sender=dispatcher.Any)
        dispatcher.connect(self.onWB_CurrentPlanID, signal=self.signals.WB_CURRENT_PLAN_ID, sender=dispatcher.Any)
        dispatcher.connect(self.onWB_Test,signal=self.signals.WB_TEST, sender=dispatcher.Any)
        dispatcher.connect(self.onWB_TestInfo,signal=self.signals.WB_TESTINFO, sender=dispatcher.Any)
        dispatcher.connect(self.onWB_Ok,signal=self.signals.WB_OK, sender=dispatcher.Any)
        dispatcher.connect(self.onWB_Error,signal=self.signals.WB_ERROR, sender=dispatcher.Any)

        dispatcher.send(self.signals.WB_GET_TESTINFO, dispatcher.Anonymous,self)

        #test_description_table = list of all tests with ID in database
        #pos = position in test_description_table. pos will be used for user information about
        #sum of test an actual position
        if self._current_testID in self._test_description_table:
            _pos = self._test_description_table.index(self._current_testID)
        else:
            _pos = len(self._test_description_table)
            self._current_testID = self._test_description_table[_pos-1]

        self._current_pos = _pos
        self.ui.label_12.setText(str(self._current_pos) + " of " + str(self._max_tests))



      #  if (self._mode_new):
      #      dispatcher.send(self.signals.WB_GET_NEW_TEST, dispatcher.Anonymous,self)
      #      self.ui.label_10.setText(time.strftime("%Y-%m-%d %H:%M:%S",self._time))
      #      self._testNo = self.getNumber(time.mktime(self._time))
      #      self.ui.label_3.setText(str(self._testNo))


       #     self.ui.label_11.setText("Workbench: "+ self._config['ControllerDefaults']['current_workbench'] + "   ID: "
       #                              + str(self._current_testID))
        #else:

        dispatcher.send(self.signals.WB_GET_TEST, dispatcher.Anonymous,self,self._current_testID)
        self.ui.label_11.setText("Workbench: "+ self._config['DataBases']['workbench'] + "   ID: "
                                     + str(self._current_testID))



        # get all TestDescriptions
        #dispatcher.send(self.signals.WB_GET_TESTS,self)
        #self._test_model = TableModel()
        #self.ui.tableView_2.setModel(self._test_model)

    def _fill_form(self):
        self._testNo = self._test.test_no
        self.ui.label_3.setText(self._testNo)
        self.ui.lineEdit_2.setText(self._test.title)
        self.ui.lineEdit_5.setText(self._test.eut)
        self.ui.lineEdit_3.setText(self._test.serial_no)
        self.ui.lineEdit_6.setText(self._test.user_no)
        self.ui.lineEdit_4.setText(self._test.operator)

        self.ui.plainTextEdit.setPlainText(self._test.comment)

        if self._test.type_of_user == 1:
            self.ui.RBtnUser1.setChecked(True)
        if self._test.type_of_user == 2:
            self.ui.RBtnUser2.setChecked(True)
        if self._test.type_of_user == 3:
            self.ui.RBtnUser3.setChecked(True)
        if self._test.type_of_user == 4:
            self.ui.RBtnUser4.setChecked(True)

        if self._test.type_of_test == 1:
            self.ui.RBtnTT1.setChecked(True)
        if self._test.type_of_test == 2:
            self.ui.RBtnTT2.setChecked(True)

        if self._test.type_of_eut == 1:
            self.ui.RBtnTE1.setChecked(True)
        if self._test.type_of_eut == 2:
            self.ui.RBtnTE2.setChecked(True)
        if self._test.type_of_eut == 3:
            self.ui.RBtnTE3.setChecked(True)
        if self._test.type_of_eut == 4:
            self.ui.RBtnTE4.setChecked(True)
        if self._test.type_of_eut == 5:
            self.ui.RBtnTE5.setChecked(True)
        if self._test.type_of_eut == 6:
            self.ui.RBtnTE6.setChecked(True)
        if self._test.type_of_eut == 7:
            self.ui.RBtnTE7.setChecked(True)
        if self._test.type_of_eut == 8:
            self.ui.RBtnTE7.setChecked(True)

        self._tm.reset()

        self._tm.removeRows(0,self._tm.rowCount())

        for l in self._test.plan_list:
            self._tm.addData(l)

    def onBtnFwd(self):
        #pos: 1 - n (for user information)
        #id: 0 - n-1 (for data base)
        if self._current_pos < self._max_tests:
            _pos = self._current_pos + 1
            id = self._testInfo.test_list[_pos - 1]
            dispatcher.send(self.signals.WB_GET_TEST, dispatcher.Anonymous,self, id)
            if not self._wb_error:
                self._current_pos = self._current_pos + 1
                self.ui.label_12.setText(str(self._current_pos) + " of " + str(self._max_tests))
                self.ui.BtnFRwd.setEnabled(True)
                self.ui.BtnRwd.setEnabled(True)
                if self._current_pos == self._max_tests:
                    self.ui.BtnFFwd.setEnabled(False)
                    self.ui.BtnFwd.setEnabled(False)

        pass
    def onBtnFFwd(self):
        #pos: 1 - n (for user information)
        #id: 0 - n-1 (for data base)
        id = self._testInfo.test_list[self._max_tests - 1]
        dispatcher.send(self.signals.WB_GET_TEST, dispatcher.Anonymous,self, id)
        if not self._wb_error:
            self._current_pos = self._max_tests
            self.ui.label_12.setText(str(self._current_pos) + " of " + str(self._max_tests))
            self.ui.BtnFFwd.setEnabled(False)
            self.ui.BtnFwd.setEnabled(False)
            self.ui.BtnFRwd.setEnabled(True)
            self.ui.BtnRwd.setEnabled(True)
        pass

    def onBtnRwd(self):
        #pos: 1 - n (for user information)
        #id: 0 - n-1 (for data base)
        if self._current_pos > 1:
            _pos = self._current_pos - 1
            id = self._testInfo.test_list[_pos - 1]
            dispatcher.send(self.signals.WB_GET_TEST, dispatcher.Anonymous,self, id)
            if not self._wb_error:
                self._current_pos -= 1
                self.ui.label_12.setText(str(self._current_pos) + " of " + str(self._max_tests))
                self.ui.BtnFFwd.setEnabled(True)
                self.ui.BtnFwd.setEnabled(True)
                if self._current_pos == 1:
                    self.ui.BtnFRwd.setEnabled(False)
                    self.ui.BtnRwd.setEnabled(False)

        pass
    def onBtnFRwd(self):
        #pos: 1 - n (for user information)
        #id: 0 - n-1 (for data base)
        id = self._testInfo.test_list[0]
        dispatcher.send(self.signals.WB_GET_TEST, dispatcher.Anonymous,self, id)
        if not self._wb_error:
            self._current_pos = 1
            self.ui.label_12.setText(str(self._current_pos) + " of " + str(self._max_tests))
            self.ui.BtnFFwd.setEnabled(True)
            self.ui.BtnFwd.setEnabled(True)
            self.ui.BtnFRwd.setEnabled(False)
            self.ui.BtnRwd.setEnabled(False)
        pass
    def onBtnLoadAndStart(self):
        print('onBtnLoadAndStart')
        pass

    def onBtnLoadAndResume(self):
        print('onBtnLoadAndResume')
        pass

    def onBtnAddPlan(self):
        _ret = QtGui.QFileDialog.getOpenFileName(self, "Open TestPlan", "", "TestPlan (*.Tds3)")
        if (_ret == ""):
            return
        dispatcher.send(self.signals.WB_ADD_PLAN, self, _ret, self._current_testID)
        #refresh test description
        dispatcher.send(self.signals.WB_GET_TEST, dispatcher.Anonymous,self,self._current_testID)
        pass

    def onBtnDeletePlan(self):
        print('onBtnDeletePlan')
        pass

    def onBtnExportPlan(self):

        _selectedLine = self.ui.tableView.selectedIndexes()
        if _selectedLine == 0:
            QtGui.QMessageBox.information(self, 'TMV3',"no TestPlan selected")
            return

        _planID = self._tm.data(_selectedLine[0],Qt.DisplayRole)

        #get target file name
        _export_file_name = QtGui.QFileDialog.getSaveFileName(self, "Export TestPlan", "", "TestPlan (*.Tds3)")
        if (_export_file_name == ""):
            return

        dispatcher.send(self.signals.WB_EXPORT_FILE, self, _planID, _export_file_name)
        pass
    def onBtnShowPlots(self):
        print('onBtnShowPlots')
        pass
    def onBtnActivatePlan(self):
        # signals Workbench to extract TestPlan as file "ActiveTestPlan"
        # signals Controller to load "ActiveTestPlan"
        _selectedLine = self.ui.tableView.selectedIndexes()
        if _selectedLine == 0:
            QtGui.QMessageBox.information(self, 'TMV3',"no TestPlan selected")
            return

        _planID = self._tm.data(_selectedLine[0],Qt.DisplayRole)

        dispatcher.send(self.signals.WB_EXPORT_FILE, self, _planID, "ActiveTestPlan.TDS3")
        dispatcher.send(self.signals.WB_EXPORT_LIMIT, self, _planID, "ActiveTestPlan.TDS3")
        dispatcher.send(self.signals.WB_EXPORT_ANTENNA, self, _planID, "ActiveTestPlan.TDS3")
        dispatcher.send(self.signals.WB_EXPORT_CABLE, self, _planID, "ActiveTestPlan.TDS3")
        dispatcher.send(self.signals.CTR_LOAD_TESTPLAN,self)

        pass

    def onBtnNewDescription(self):
        dispatcher.send(self.signals.WB_GET_NEW_TEST, dispatcher.Anonymous,self)
        if self._wb_error:
            return
        dispatcher.send(self.signals.WB_GET_TESTINFO, dispatcher.Anonymous,self)
        if self._wb_error:
            return

        _pos = len(self._test_description_table)
        self._current_testID = self._test_description_table[_pos-1]
        self._current_pos = _pos
        self.ui.label_12.setText(str(self._current_pos) + " of " + str(self._max_tests))

        self._time = time.localtime()
        self.ui.label_10.setText(time.strftime("%Y-%m-%d %H:%M:%S",self._time))
        self._testNo = self.getNumber(time.mktime(self._time))
        self.ui.label_3.setText(str(self._testNo))
        self.ui.label_11.setText("Workbench: "+ self._config['ControllerDefaults']['current_workbench'] + "   ID: "
                                     + str(self._current_testID))
        pass
    def onBtnSaveDescription(self):
        self._test.test_no = self._testNo
        self._test.title = self.ui.lineEdit_2.text()
        self._test.eut = self.ui.lineEdit_5.text()
        self._test.serial_no = self.ui.lineEdit_3.text()
        self._test.user_no = self.ui.lineEdit_6.text()
        self._test.operator = self.ui.lineEdit_4.text()
        if self.ui.radioButton_16.isChecked():
            self._test.category = "Wiederholungsprüfung"
        if self.ui.radioButton_15.isChecked():
            self._test.category = "Erstvermessung"
        if self.ui.radioButton_18.isChecked():
            self._test.category = "Zulassung"
        if self.ui.radioButton_17.isChecked():
            self._test.category = "try out"
        self._test.comment = self.ui.plainTextEdit.toPlainText()
        if self.ui.RBtnUser1.isChecked():
            self._test.type_of_user = 1
        if self.ui.RBtnUser2.isChecked():
            self._test.type_of_user = 2
        if self.ui.RBtnUser3.isChecked():
            self._test.type_of_user = 3
        if self.ui.RBtnUser4.isChecked():
            self._test.type_of_user = 4
        if self.ui.RBtnTT1.isChecked():
            self._test.type_of_test = 1
        if self.ui.RBtnTT2.isChecked():
            self._test.type_of_test = 2
        if self.ui.RBtnTE1.isChecked():
            self._test.type_of_eut = 1
        if self.ui.RBtnTE2.isChecked():
            self._test.type_of_eut = 2
        if self.ui.RBtnTE3.isChecked():
            self._test.type_of_eut = 3
        if self.ui.RBtnTE4.isChecked():
            self._test.type_of_eut = 4
        if self.ui.RBtnTE5.isChecked():
            self._test.type_of_eut = 5
        if self.ui.RBtnTE6.isChecked():
            self._test.type_of_eut = 6
        if self.ui.RBtnTE7.isChecked():
            self._test.type_of_eut = 7
        if self.ui.RBtnTE8.isChecked():
            self._test.type_of_eut = 8
        dispatcher.send(self.signals.WB_UPDATE_TEST,dispatcher.Anonymous,self,self._test)
    def onBtnCloneDescription(self):
        print('onBtnCopyDescription')
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

    def getNumber(self,sec):
        #get seconds since 2014 converted to base34 (base 36 without I and O)
        t = sec - 1387584000
        alphabet = '0123456789ABCDEFGHJKLMNPQRSTUVWXYZ'

        base34 = ''
        while t:
            t, i = divmod(t, 34)
            base34 = alphabet[int(i)] + base34

        return base34

    def saveTestDescription(self):
        self._mode_new = False
        pass

    def onWB_Plan(self):
        pass

    def onWB_CurrentPlanID(self,id):
        self._current_plan = id
        pass

    def onWB_Test(self,client,test):
        #workbench sends test-data
        assert isinstance(test,TPL3Test)
        if client == self:
            self._test = test
            self._current_testID = test.test_id
            self._fill_form()
            pass

    def onWB_TestInfo(self,client,testInfo):
        #workbench sends overview info of tests
        assert isinstance(testInfo,TPL3TestInfo)
        if client == self:
            self._testInfo = testInfo
            self._test_description_table = self._testInfo.test_list
            self._max_tests = len(self._test_description_table)
            pass

    def onWB_Ok(self,client):
        if self == client:
            print("WB_Ok")
        pass

    def onWB_Error(self,client,text):
        if self == client:
            print("WB_Error")
            ret = QtGui.QMessageBox.information(self, 'TMV3',text)
        pass

class TableModel(QAbstractTableModel):
    def __init__(self, header, parent = None):
        super(TableModel, self).__init__(parent)
        self._data = []
        self._header = header

    def rowCount(self, parent = QModelIndex()):
        return len(self._data)

    def columnCount(self, parent = QModelIndex()):
        return len(self._header)

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None

        return self._data[index.row()][index.column()]

    def addData(self,data):
        self._data.append(data)

    def headerData(self, col, orientation, role):
        if role == Qt.DisplayRole :
            if orientation == Qt.Horizontal :
                return self._header[col]
            elif orientation == Qt.Vertical :
                return None
        return None

    def removeRows(self, row, count, parent=QModelIndex()):
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        del self._data[row:row + count]
        self.endRemoveRows()
        return True


    def sort(self, Ncol, order):
        """
        Sort table by given column number.
        """
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        #self._data = sorted(self._data, key=Ncol))
        if order == Qt.DescendingOrder:
            self.arraydata.reverse()
        self.emit(SIGNAL("layoutChanged()"))

        return None
