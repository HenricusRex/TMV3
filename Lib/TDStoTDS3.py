__author__ = 'Heinz'
__author__ = 'Heinz'
from PyQt4 import uic, QtGui, QtCore
import pypyodbc
import sys,getopt
import sqlite3 as lite
import configparser
import shutil
import os.path,time
from datetime import datetime
from datetime import datetime, timedelta


class TDStoTDS3(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("TDStoTDS3.ui", self)
        self.centerOnScreen()
        self.inputFile = ""
        self.outputFile = ""
        self.rtFileName = ""
        self.rtFileData = ""
        self.drFileName = ""
        self.drFileData = ""
        self.config = configparser.ConfigParser()
        self.config.read('TMV3.ini')
        self.tdsDate = 0

        self.ui.BtnFileTDS.clicked.connect(self.loadTDS)
        self.ui.BtnFileRT.clicked.connect(self.loadRT)
        self.ui.BtnFileDR.clicked.connect(self.loadDR)
        self.ui.BtnOk.clicked.connect(self.onBtnOk)
        self.ui.BtnCancel.clicked.connect(self.onBtnCancel)
    def onBtnOk(self):
        if self.convert():
            self.close()
            return


    def onBtnCancel(self):
        self.close()

    def loadRT(self):
        _ret = QtGui.QFileDialog.getOpenFileName(self, "Open Routine PY", "", "RT (*.PY)")
        if (_ret == ""): return
        self.ui.lineEdit_2.setText(_ret)
        self.rtFileName = os.path.splitext(os.path.basename(_ret))[0]
        with open(_ret) as f:
            self.rtFileData = f.readlines()
        pass
    def loadDR(self):
        _ret = QtGui.QFileDialog.getOpenFileName(self, "Open Routine PY", "", "RT (*.PY)")
        if (_ret == ""): return
        self.ui.lineEdit_3.setText(_ret)
        self.drFileName = os.path.splitext(os.path.basename(_ret))[0]
        with open(_ret) as f:
            self.drFileData = f.readlines()
        pass
    def loadTDS(self):

        _ret = QtGui.QFileDialog.getOpenFileName(self, "Open TDS", "", "TDS (*.Tds)")
        if (_ret == ""): return
        self.ui.lineEdit.setText(_ret)

        self.inputFile = _ret
        self.outputFile = self.inputFile+'3'
        if os.path.isfile(self.outputFile):
            _s = "new TDS3  " + self.outputFile + "  already exists"
            QtGui.QMessageBox.information(self, 'TMV3', _s, QtGui.QMessageBox.Ok)
            return
        shutil.copy("../Templates/TMV3.TDS3",self.outputFile)

    def convert(self):
        _t = time.gmtime(os.path.getmtime(self.inputFile))
        self.tdsDate = time.strftime('%Y-%m-%d %H:%M:%S', _t)

        _conI = pypyodbc.win_connect_mdb(self.inputFile)
        _curI = _conI.cursor()

        try:
            _conz = lite.connect(self.outputFile)
            _curz = _conz.cursor()

            _conq = pypyodbc.win_connect_mdb(self.inputFile)
            _curq = _conq.cursor()
            _curq.execute('SELECT [tTitle],[tEUT],[tComment],[tVersion],[bNATO] from Plan')
            _plan = _curq.fetchall()
            print (_plan)

            _curz.execute("INSERT INTO Plan (Title,TMVVersion,Version,Date,NATO,Company,Comment) VALUES (?,?,?,?,?,?,?)",
                          (str(_plan[0][0]), '2',str(_plan[0][3]),str(self.tdsDate),str(_plan[0][4]),'BSI',str(_plan[0][2])))

            _conz.commit()
            _rowIDPlan = _curz.lastrowid
            print(_rowIDPlan)
            _blob = ''.join(self.rtFileData)
            _curz.execute("INSERT INTO Files (Title,Type,Data) VALUES (?,?,?)",
                          (self.rtFileName, "Routine", _blob))
            _blob = ''.join(self.drFileData)
            _curz.execute("INSERT INTO Files (Title,Type,Data) VALUES (?,?,?)",
                          (self.drFileName, "Driver", _blob))

            _conz.commit()



            _curq.execute('SELECT * from Routinen')
            _routinen = _curq.fetchall()

            for n in _routinen:
                print(n)
                _routineID = n[0]
                _curz.execute("INSERT INTO Plots (PlanID,Title,X1,X2,Y1,Y2,Log,Unit,Annotation,[Order],Comment) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                          (str(_rowIDPlan), str(n[2]),str(n[3]),str(n[4]),str(n[5]),str(n[6]),str(int(n[8])),str('dBµV'),str(n[11]),str(n[16]),str(n[13])))
                _conz.commit()
                _rowIDPlot = _curz.lastrowid
                print(_rowIDPlot)

                _curq.execute('SELECT [tTitle] FROM Limits WHERE [lRoutineID]={0}'.format(str(_routineID)))
                _limits = _curq.fetchall()
                # add version
                _lim = []
                _e = '0','0'

                for _x in _limits:
                    _lim.append((_x[0],'1.0'))

                _curz.execute("INSERT INTO Routines (PlotID,Title,Device1,SignalClass,[Order],Comment,Limits) VALUES (?,?,?,?,?,?,?)",
                          (str(_rowIDPlot), self.rtFileName,self.drFileName,str(n[14]),str(n[16]),str(n[13]),str(_lim)))
                _conz.commit()
                _rowIDRoutine = _curz.lastrowid
                print(_rowIDRoutine)

                _curq.execute('SELECT * from Settings WHERE [lRoutineID]={0}'.format(str(_routineID)))
                _settings = _curq.fetchall()

                for i in _settings:
                    _settingID = i[0]
                    _curz.execute("INSERT INTO Settings (RoutineID,[Order],StartFreq,StopFreq,Title,Step,StepWidth,StepTime,Route) VALUES (?,?,?,?,?,?,?,?,?)",
                          (str(_rowIDRoutine), str(int(i[23])),str(i[3]),str(i[4]),str(i[2]),'0','0',str(i[9]),str(i[17])))
                    _conz.commit()
                    _rowIDSetting = _curz.lastrowid
                    print(_rowIDSetting)
                    _curz.execute("INSERT INTO [Commands] ([SettingID],[Order],[Command],[Parameter]) VALUES (?,?,?,?)",
                                   (str(_rowIDSetting),str('1'),str('set_StartFreq'),str(i[3])))
                    _curz.execute("INSERT INTO Commands (SettingID,[Order],Command,Parameter) VALUES (?,?,?,?)",
                                   (str(_rowIDSetting),'2','set_StopFreq',str(i[4])))
                    _curz.execute("INSERT INTO Commands (SettingID,[Order],Command,Parameter) VALUES (?,?,?,?)",
                                   (str(_rowIDSetting),'3','set_ResBW',str(i[5])))
                    _curz.execute("INSERT INTO Commands (SettingID,[Order],Command,Parameter) VALUES (?,?,?,?)",
                                   (str(_rowIDSetting),'4','set_VidBW',str(i[6])))
                    _curz.execute("INSERT INTO Commands (SettingID,[Order],Command,Parameter) VALUES (?,?,?,?)",
                                   (str(_rowIDSetting),'5','set_Attenuator',str(i[10])))
                    if n[15] == "FSET":
                        _curz.execute("INSERT INTO Commands (SettingID,[Order],Command,Parameter) VALUES (?,?,?,?)",
                                       (str(_rowIDSetting),'6','set_PreSelector',str(i[15])))
                        _curz.execute("INSERT INTO Commands (SettingID,[Order],Command,Parameter) VALUES (?,?,?,?)",
                                       (str(_rowIDSetting),'7','set_PreAmplifier',str(int(i[11]))))
                    else:
                        _curz.execute("INSERT INTO Commands (SettingID,[Order],Command,Parameter) VALUES (?,?,?,?)",
                                       (str(_rowIDSetting),'6','set_PreSelector',str(int(i[12]))))
                        _curz.execute("INSERT INTO Commands (SettingID,[Order],Command,Parameter) VALUES (?,?,?,?)",
                                       (str(_rowIDSetting),'7','set_PreAmplifier',str(int(i[13]))))

                    _curz.execute("INSERT INTO Commands (SettingID,[Order],Command,Parameter) VALUES (?,?,?,?)",
                                   (str(_rowIDSetting),'8','set_RefLevel',str(i[8])))
                    _curz.execute("INSERT INTO Commands (SettingID,[Order],Command,Parameter) VALUES (?,?,?,?)",
                                   (str(_rowIDSetting),'9','set_Detector',str(i[22])))
                    _curz.execute("INSERT INTO Commands (SettingID,[Order],Command,Parameter) VALUES (?,?,?,?)",
                                   (str(_rowIDSetting),'10','set_StepTime',str(i[9])))
                    _conz.commit()

                    _curq.execute("SELECT * FROM Traces WHERE [lSettingID]={0}".format(str(_settingID)))
                    _traces = _curq.fetchall()

                    for j in _traces:
                        _curz.execute("INSERT INTO Traces (SettingID,StartFreq,StopFreq) VALUES (?,?,?)",
                          (str(_rowIDSetting), str(int(j[2])),str(j[3])))
                        _conz.commit()




    #    for n in x:
    #        _curq.execute('SELECT [dXValue],[dYValue] from LIMITVALUES where [lLimitID] = {0} ORDER by [dXValue]'.format(str(n[2])))
    #        y = _curq.fetchall()
    #        print (str(n[0]))
    #        print (str(mDate))
    #        print (str(n[1]))
    #        print(str(y))
    #        _curz.execute("INSERT INTO Limits (Title,Date,Comment,DataXY) VALUES (?,?,?,?)", (str(n[0]), str(mDate),str(n[1]),str(y)))
    #        _conz.commit()

    #    _conz.close()
        except Exception as _err:
            print(_err)
            QtGui.QMessageBox.information(self, 'TMV3', str(_err), QtGui.QMessageBox.Ok)
            return (False)
        return True

    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))